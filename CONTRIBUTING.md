To work on this Python-based Action locally without accidentally triggering live GitHub APIs or corrupting the production database, you will need to set up an isolated virtual environment and use your own test API keys.

### 1. Fork & Clone
Fork the repository to your own GitHub account and clone it to your local machine.

### 2. Set up the Environment
Create an isolated Python virtual environment to prevent dependency conflicts.
```bash
python -m venv venv
# Windows: .\venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Secrets
Create a `.env` file in the root directory. **Do not commit this file.** Add your personal test keys:
```env
OPENAI_API_KEY=sk-your-openai-key
PINECONE_API_KEY=pc-your-pinecone-key
PINECONE_INDEX_NAME=your-test-index
GITHUB_EVENT_PATH=dummy_payload.json
```

### 5. Local Testing

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

## Pull Request Process
1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes and test them locally.
3. Commit your changes using descriptive commit messages.
4. Push your branch to your fork and submit a Pull Request against our `main` branch.