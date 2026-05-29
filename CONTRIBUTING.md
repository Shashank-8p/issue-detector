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
To test the AI logic without triggering GitHub Actions, create a `dummy_payload.json` file in your root folder mimicking a GitHub webhook payload, then run `python main.py`.

## Pull Request Process
1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes and test them locally.
3. Commit your changes using descriptive commit messages.
4. Push your branch to your fork and submit a Pull Request against our `main` branch.