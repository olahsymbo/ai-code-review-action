````markdown
# 🤖 AI Code Review GitHub Action

An AI-powered GitHub Action that automatically reviews pull requests using OpenAI's GPT models. It highlights potential bugs, suggests improvements, and helps enforce code quality standards—without needing a human to review every line.

---

## 🚀 How It Works

This action triggers on pull requests or commits. It uses the GitHub diff and OpenAI's API to generate intelligent review comments.

---

## 📦 Usage

### Step 1: Add the Action to Your Workflow

```yaml
name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run AI Code Review
        uses: olahsymbo/ai-code-review-action@v1
        with:
          token_github: ${{ secrets.TOKENGITHUB }}
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
````

---

### Step 2: Set Required Secrets

| Secret Name      | Description                                     |
| ---------------- | ----------------------------------------------- |
| `TOKENGITHUB`    | GitHub Personal Access Token (with repo access) |
| `OPENAI_API_KEY` | Your OpenAI API key for GPT access              |

To add secrets:

* Go to your repo → Settings → Secrets → Actions
* Click “New repository secret”

---

## 🔧 Inputs

| Input            | Required | Description                       |
| ---------------- | -------- | --------------------------------- |
| `token_github`   | ✅        | GitHub personal access token (PAT) for posting comments |
| `openai_api_key` | ✅        | OpenAI API key for GPT access     |

---

## 📁 Project Structure

```
.
├── action.yml            # Composite GitHub Action definition
├── ai_code_review.py     # Main logic for generating code reviews
├── README.md             # This file
```

---

## 🛠 Requirements

* Python 3.9+ (used in the GitHub runner)
* An OpenAI key (GPT-4 or GPT-3.5)

---

## 🧪 Example Output

> The action leaves GitHub review comments like:

```
💡 Consider renaming this variable for clarity.
🚨 Possible off-by-one error here.
✅ This function looks well-structured.
```

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repo
2. Create a feature branch
3. Submit a pull request with a clear description

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙌 Acknowledgements

Built with ❤️ using GitHub Actions and OpenAI.

```
