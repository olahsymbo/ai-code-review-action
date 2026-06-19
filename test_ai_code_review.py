import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from ai_code_review import (
    Provider,
    SYSTEM_PROMPT,
    _response_text,
    available_providers,
    bounded_tokens,
    build_prompt,
    derive_verdict,
    load_diff,
    main,
    review_diff,
)


class ReviewInputTests(unittest.TestCase):
    def test_load_diff_reports_truncation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "change.diff"
            path.write_text("abcdefgh", encoding="utf-8")
            content, truncated = load_diff(str(path), max_chars=4)
        self.assertEqual(content, "abcd")
        self.assertTrue(truncated)

    def test_review_level_and_truncation_are_in_prompt(self):
        prompt = build_prompt("+change", "balanced", True)
        self.assertIn("MEDIUM severity and above", prompt)
        self.assertIn("truncated", prompt)

    def test_unknown_mode_falls_back_to_aggressive(self):
        self.assertIn("Review level: aggressive", build_prompt("+change", "extreme", False))

    def test_diff_is_explicitly_treated_as_untrusted(self):
        self.assertIn("as untrusted data", SYSTEM_PROMPT)

    def test_token_budget_is_bounded(self):
        self.assertEqual(bounded_tokens("bad"), 450)
        self.assertEqual(bounded_tokens(10), 150)
        self.assertEqual(bounded_tokens(5000), 1000)

    def test_available_providers_uses_only_supplied_keys(self):
        providers = available_providers({
            "ANTHROPIC_API_KEY": "claude-key",
            "GEMINI_API_KEY": "gemini-key",
        })
        self.assertEqual([provider.name for provider in providers],
                         ["Anthropic / Claude", "Google / Gemini"])

    def test_provider_model_can_be_overridden(self):
        providers = available_providers({
            "GEMINI_API_KEY": "key",
            "GEMINI_MODEL": "gemini-custom",
        })
        self.assertEqual(providers[0].model, "gemini-custom")

    def test_one_key_runs_one_provider(self):
        providers = available_providers({"OPENAI_API_KEY": "key"})
        self.assertEqual(len(providers), 1)
        self.assertEqual(providers[0].model, "gpt-5.5")

    def test_anthropic_defaults_to_opus(self):
        providers = available_providers({"ANTHROPIC_API_KEY": "key"})
        self.assertEqual(providers[0].model, "claude-opus-4-8")

    def test_multiple_providers_run_in_stable_order(self):
        calls = []
        lock = threading.Lock()
        providers = [
            Provider("OpenAI / GPT", "one", "gpt-test"),
            Provider("Anthropic / Claude", "two", "claude-test"),
            Provider("Google / Gemini", "three", "gemini-test"),
        ]

        def fake_runner(provider, prompt, tokens):
            with lock:
                calls.append((provider.name, tokens))
            return "DECISION: PASS\nNo actionable defects"

        output = review_diff("+change", "aggressive", providers, False, 400, fake_runner)
        self.assertEqual(len(calls), 3)
        headings = [f"### {provider.name}" for provider in providers]
        self.assertEqual([output.index(heading) for heading in headings], sorted(output.index(h) for h in headings))
        self.assertIn("**PASS**", output)
        self.assertEqual({tokens for _, tokens in calls}, {400})

    def test_one_failed_reviewer_requires_human_review(self):
        providers = [Provider("OpenAI / GPT", "one", "gpt"),
                     Provider("Anthropic / Claude", "two", "claude")]

        def partial_runner(provider, prompt, tokens):
            if provider.name.startswith("Anthropic"):
                raise TimeoutError()
            return "DECISION: PASS"

        output = review_diff("+change", "aggressive", providers, False, 450, partial_runner)
        self.assertIn("**NEEDS HUMAN REVIEW**", output)
        self.assertIn("Provider unavailable", output)

    def test_no_provider_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least one"):
            review_diff("+change", "aggressive", [], False, 450)

    def test_all_provider_failures_are_rejected(self):
        providers = [Provider("OpenAI / GPT", "key", "model")]

        def failed_runner(provider, prompt, tokens):
            raise ConnectionError()

        with self.assertRaisesRegex(RuntimeError, "all configured"):
            review_diff("+change", "aggressive", providers, False, 450, failed_runner)

    def test_content_blocks_are_normalized(self):
        content = [{"type": "text", "text": "first"}, {"type": "text", "text": "second"}]
        self.assertEqual(_response_text(content), "first\nsecond")

    def test_main_requires_a_provider_key(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(main(), 2)

    def test_main_writes_pass_for_empty_diff_without_model_call(self):
        with tempfile.TemporaryDirectory() as directory:
            diff_path = Path(directory) / "review.diff"
            output_path = Path(directory) / "review.md"
            diff_path.write_text("", encoding="utf-8")
            env = {
                "OPENAI_API_KEY": "test-key",
                "REVIEW_DIFF_PATH": str(diff_path),
                "REVIEW_OUTPUT_PATH": str(output_path),
            }
            with patch.dict(os.environ, env, clear=True):
                self.assertEqual(main(), 0)
            self.assertIn("**PASS**", output_path.read_text(encoding="utf-8"))

    def test_verdict_precedence_and_malformed_output(self):
        self.assertEqual(derive_verdict(["DECISION: PASS", "DECISION: REQUEST CHANGES"], False),
                         "REQUEST CHANGES")
        self.assertEqual(derive_verdict(["malformed", "DECISION: PASS"], False),
                         "NEEDS HUMAN REVIEW")
        self.assertEqual(derive_verdict(["DECISION: PASS", "DECISION: PASS"], True),
                         "NEEDS HUMAN REVIEW")


if __name__ == "__main__":
    unittest.main()
