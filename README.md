# AI Duplicate Issue Detector

An autonomous GitHub Action that uses semantic embeddings and vector search to detect duplicate GitHub issues. Instead of relying on keyword matching, it understands the meaning behind issue descriptions and flags potentially duplicate reports for human review.

---

## Why I Built This

I started exploring this idea during my time contributing to open source through GSSoC. While things did not unfold exactly as I had hoped, the experience exposed me to a real challenge faced by maintainers: identifying duplicate issues hidden behind different wording.

That observation eventually led to this project, which uses semantic embeddings and vector search to help surface potential duplicates automatically while keeping maintainers in control.

Examples:

- "Unable to log in to dashboard"
- "Authentication fails after entering credentials"

Although semantically identical, keyword matching may miss them.

AI Duplicate Issue Detector solves this problem by:

- Converting issue descriptions into semantic embeddings.
- Storing embeddings in a vector database.
- Performing similarity searches against previously reported issues.
- Alerting maintainers when highly similar issues are detected.

The final decision always remains with a human maintainer.

---

## ✨ Features

- Semantic duplicate detection using vector embeddings
- GitHub Actions integration
- Automated issue scanning on issue creation and updates
- Pinecone-powered similarity search
- Markdown and code-block preprocessing
- Dockerized execution environment
- Human-in-the-loop workflow
- Graceful failure handling for missing tokens or services

---

## 🏗️ Architecture

```text
GitHub Issue
      │
      ▼
Text Preprocessing
      │
      ▼
OpenAI Embeddings
      │
      ▼
Pinecone Vector Search
      │
      ▼
Similarity Evaluation
      │
      ▼
GitHub Comment Notification
```

---

## 🛠️ Tech Stack

| Component | Technology |
|------------|------------|
| Language | Python 3.11 |
| Embeddings | OpenAI text-embedding-3-small |
| Vector Database | Pinecone |
| CI/CD | GitHub Actions |
| Containerization | Docker |
| Repository Integration | GitHub REST API |

---

## 📂 Project Structure

```text
issue-detector/
│
├── .github/
├── workflows/
│   └── duplicate-checker.yml     
└── ISSUE_TEMPLATE/               
    └── bug_report.yml    # file for the issue form
├── .gitignore            # Ignored files and folders
├── action.yml            # Defines the GitHub Action inputs/outputs
├── CONTRIBUTING.md       # Open source contribution guidelines
├── Dockerfile            # Container configuration
├── LICENSE               # MIT License
├── main.py               # Core application logic
├── README.md             # Project documentation
└── requirements.txt      # Python dependencies
```

---

## 📋 Prerequisites

Before using this project, ensure you have:

- Python 3.11+
- OpenAI API Key
- Pinecone API Key
- Pinecone Index
- GitHub Repository with Actions enabled

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/Shashank-8p/issue-detector.git
cd issue-detector
```

### Create Virtual Environment

```bash
python -m venv venv
```

Linux/macOS:

```bash
source venv/bin/activate
```

Windows:

```powershell
.\venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_index_name
GITHUB_EVENT_PATH=dummy_payload.json
```

| Variable | Description |
|-----------|------------|
| OPENAI_API_KEY | OpenAI API access key |
| PINECONE_API_KEY | Pinecone access key |
| PINECONE_INDEX_NAME | Pinecone vector index name |
| GITHUB_EVENT_PATH | Local GitHub event payload |

---

## 🧪 Local Testing

GitHub Actions pass event data to scripts via a temporary JSON file. To test this bot locally without risking live repository infrastructure, we can "trick" the script by providing our own mock file. 

*(Ensure you have set `GITHUB_EVENT_PATH=dummy_payload.json` in your local `.env` file before starting).*

### 1. Create the Mock Payload
Create a file named `dummy_payload.json` in your root folder and paste this mock issue data:

```json
{
  "issue": {
    "number": 99,
    "title": "Login page not working",
    "body": "Users cannot authenticate after entering credentials."
  }
}
```

### 2. Run the Engine (Test for "Unique")
Execute the script in your terminal:
```bash
python main.py
```
**Expected Outcome:** Because this is the first time the bot has seen this text, it should calculate the embeddings, query Pinecone, fail to find a match, and print `[UNIQUE ISSUE] No severe duplicate detected.` It will then save this issue to your test database.

### 3. Trigger a Duplicate (Test for "Match")
To prove the AI works, open your `dummy_payload.json` file and slightly alter the wording to simulate a new user posting the same bug:

```json
{
  "issue": {
    "number": 100,
    "title": "Cannot sign in to the platform",
    "body": "The authentication system is broken when I type my password."
  }
}
```

Run `python main.py` one more time. 
**Expected Outcome:** The bot will read the new words, realize the semantic meaning matches Issue #99, and print `[MATCH FOUND] This issue appears to be a duplicate!`

---

## 🚀 GitHub Action Usage

Create:

```text
.github/workflows/duplicate-checker.yml
```

```yaml
name: Issue Duplicate Checker

on:
  issues:
    types:
      - opened
      - edited

jobs:
  check-duplicates:
    runs-on: ubuntu-latest

    permissions:
      issues: write

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Run AI Duplicate Detector
        uses: Shashank-8p/issue-detector@main

        with:
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          pinecone_api_key: ${{ secrets.PINECONE_API_KEY }}
          pinecone_index_name: ${{ secrets.PINECONE_INDEX_NAME }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

---

## 🔍 How It Works

1. A GitHub issue is created or edited.
2. The issue content is cleaned and preprocessed.
3. OpenAI generates a semantic embedding.
4. Pinecone searches for the nearest existing issues.
5. Similarity scores are evaluated.
6. If the score exceeds the threshold, a notification comment is posted.
7. Maintainers decide whether the issue should be closed as a duplicate.

---

## 🎯 Example Workflow

```text
Issue #15:
"Cannot sign in to dashboard"

↓ Embedding Generated

↓ Pinecone Search

Issue #3:
"Authentication failing on main page"

Similarity Score: 0.82

↓ Threshold Passed

Bot Comment:
"This issue appears highly similar to #3.
Please verify whether it is a duplicate."
```

---

## 🤝 Contributing

Contributions are welcome.

Potential areas for improvement:

- Better text preprocessing
- Multi-language issue support
- Adaptive similarity thresholds
- Issue clustering
- Repository analytics dashboard
- Additional vector database support

---

## 🔮 Future Enhancements

- Support for multiple embedding models
- Automatic duplicate issue labeling
- Maintainer feedback learning loop
- Slack and Discord notifications
- Historical issue trend analysis
- Repository health metrics

---

## 📜 License

MIT License

Copyright (c) Shashank Pathak

---

## 🙏 Acknowledgements

- OpenAI
- Pinecone
- GitHub Actions
- Open-source maintainers who inspired this project