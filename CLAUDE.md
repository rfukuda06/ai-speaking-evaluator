# CLAUDE.md

## Project Overview

AI English Speaking Evaluator — a web app that simulates an IELTS-style speaking test. Uses a FastAPI backend + vanilla JS frontend. OpenAI APIs (GPT-4o, Whisper, TTS) handle adaptive questioning, speech transcription, and scoring.

## Tech Stack

- **Backend:** Python / FastAPI
- **Frontend:** Vanilla JS, HTML, CSS
- **APIs:** OpenAI (GPT-4o-mini for examiner, GPT-4o for scoring, Whisper for STT, TTS for audio)
- **Config:** python-dotenv for environment variables

## Project Structure

```
backend/
  main.py               → FastAPI app entry point, CORS, static file serving
  config.py             → Models, constants, thresholds, scoring weights
  state_management.py   → Part initialization + session state helpers
  llm_functions.py      → GPT prompts, question generation, scoring
  voice_functions.py    → Audio I/O, Whisper STT, TTS, timing metrics
  scoring.py            → IELTS rubric, band scores, CEFR mapping
  utils.py              → Formatting, timers, silence detection
  routes/
    session.py          → Session management endpoints
    test_flow.py        → Test progression endpoints
    audio.py            → Audio/TTS endpoints
  services/
    session_store.py    → In-memory session storage
    test_engine.py      → Test logic engine

frontend/
  index.html            → Main HTML page
  css/style.css         → Dark-mode UI styles
  js/
    app.js              → Main app logic + state machine
    api.js              → Backend API client
    audio.js            → Audio recording/playback
    timer.js            → Countdown timers
    ui.js               → DOM rendering helpers
```

## Local Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Create .env with OPENAI_API_KEY=your_key
uvicorn backend.main:app --reload
# Runs on http://localhost:8000
```

## Key Commands

- `uvicorn backend.main:app --reload` — start the dev server
- `pip install -r requirements.txt` — install dependencies

## Environment Variables

- `OPENAI_API_KEY` (required) — OpenAI API key
- `DEEPGRAM_API_KEY` (optional) — for future use

## Important Notes

- Never commit `.env` or API keys
- `backend/config.py` holds all model names, scoring weights, and test structure constants
- The app uses a multi-step state machine flow: START → PART1 → PART2 → PART2_LONG_RESPONSE → PART2_ROUNDING → PART3 → RESULTS
- Scoring uses a hybrid approach: objective speech metrics (WPM, pauses) + LLM evaluation across 5 weighted criteria
- Frontend served as static files by FastAPI at `/`
- API routes are prefixed under `/api/` (session, test_flow, audio)
