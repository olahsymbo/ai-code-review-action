# AI Code Review Action

A pull-request reviewer that can use GPT, Claude, and Gemini together. It runs one compact review per configured provider over the actual Git diff.

> [!IMPORTANT]
> AI authorship cannot be reliably proven from source code alone. The action's AI-likelihood score is a review signal—not evidence—and should never be the sole reason to reject a contribution or penalize a contributor.

## What it checks

- Correctness, security, data loss, race conditions, and broken edge cases
- Missing validation, error handling, tests, and backward compatibility
- Dead code, fabricated APIs, repetitive boilerplate, and unnecessary abstractions
- AI-like patterns, with a score, confidence level, concrete signals, and a mandatory caveat
- One to three parallel provider reviews without a fourth model call for synthesis
- New-file line numbers from the PR diff

Aggressive mode increases scrutiny; it does not permit fabricated findings. The action updates its previous PR comment on every synchronization instead of adding duplicate comments.

## Usage

```yaml
name: AI Code Review

on:
  pull_request:
    types: [opened, reopened, synchronize]

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: olahsymbo/ai-code-review-action@v1
        with:
          token_github: ${{ secrets.GITHUB_TOKEN }}
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          review_level: aggressive
```

Only one AI key is required. With one key, that provider reviews alone. With two or three keys, the available providers review concurrently. For example, omit `anthropic_api_key` if you only have OpenAI access.

## Inputs

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `openai_api_key` | No | — | OpenAI API key |
| `anthropic_api_key` | No | — | Anthropic API key |
| `gemini_api_key` | No | — | Google Gemini API key |
| `token_github` | Yes | — | Token used to create or update the PR comment |
| `review_level` | No | `aggressive` | `aggressive` or `balanced` |
| `openai_model` | No | `gpt-5.5` | OpenAI flagship model |
| `anthropic_model` | No | `claude-opus-4-8` | Claude Opus flagship model |
| `gemini_model` | No | `gemini-3.1-pro-preview` | Gemini flagship reasoning model (preview) |
| `max_tokens_per_reviewer` | No | `1200` | Output cap per provider; clamped to 150–4000 |

At least one of the three provider API keys must be supplied.

The built-in `GITHUB_TOKEN` is normally sufficient when the workflow has the permissions shown above. Pull requests from forks do not receive repository secrets under GitHub's standard `pull_request` security model.

## Output

Each review contains:

- a verdict: `REQUEST CHANGES`, `NEEDS HUMAN REVIEW`, or `PASS`;
- findings ranked from `BLOCKER` to `LOW`;
- an AI-likelihood score with evidence and uncertainty;
- specific test gaps.

Diffs larger than 40,000 characters are truncated and receive a `NEEDS HUMAN REVIEW` verdict. Each configured provider receives the diff, so this cap controls input usage while the per-provider setting controls output usage.

## Development

```bash
python -m pip install -r requirements.txt
python -m unittest -v
```

The model call is isolated from the input-building tests, so the test suite does not require an API request.

## License

MIT
