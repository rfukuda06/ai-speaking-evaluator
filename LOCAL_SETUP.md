# Local Setup Guide

How to get the AI English Speaking Evaluator running on your machine.

## Prerequisites

- **Python 3.11+** (recommended)
- **OpenAI API key** with access to GPT-4o, Whisper, and TTS

## Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-english-speaking-evaluator.git
cd ai-english-speaking-evaluator
```

## Step 2: Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:
```bash
.venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `streamlit` — web framework
- `openai` — GPT, Whisper, and TTS APIs
- `python-dotenv` — environment variable loading
- `streamlit-autorefresh` — auto-refresh component

## Step 4: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

> **Do not commit this file.** It is already in `.gitignore`.

## Step 5: Start the Server

```bash
streamlit run app.py
```

The app will open in your browser at **http://localhost:8501**.

## DevContainer (Optional)

If you use VS Code with the Dev Containers extension, the project includes a `.devcontainer/devcontainer.json` that:

- Uses a Python 3.11 image
- Auto-installs dependencies on container creation
- Forwards port 8501
- Installs Python + Pylance extensions

Just open the project in VS Code and select **"Reopen in Container"** when prompted.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Make sure your virtual environment is activated and you ran `pip install -r requirements.txt` |
| `openai.AuthenticationError` | Check that your `.env` file exists and `OPENAI_API_KEY` is set correctly |
| App doesn't open in browser | Navigate manually to `http://localhost:8501` |
| Port 8501 in use | Run with `streamlit run app.py --server.port 8502` to use a different port |
| Voice mode not working | Ensure your browser has microphone permissions enabled |
