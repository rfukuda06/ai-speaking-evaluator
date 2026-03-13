# CLAUDE.md

## Project Overview

AI English Speaking Evaluator — a Streamlit web app that simulates an IELTS-style speaking test. Uses OpenAI APIs (GPT-4o, Whisper, TTS) for adaptive questioning, speech transcription, and scoring.

## Tech Stack

- **Language:** Python
- **Framework:** Streamlit
- **APIs:** OpenAI (GPT-4o-mini for examiner, GPT-4o for scoring, Whisper for STT, TTS for audio)
- **Config:** python-dotenv for environment variables

## Project Structure

```
app.py                → Main Streamlit UI + state machine
config.py             → Models, constants, thresholds, scoring weights
state_management.py   → Part initialization + session state helpers
llm_functions.py      → GPT prompts, question generation, scoring
voice_functions.py    → Audio I/O, Whisper STT, TTS, timing metrics
scoring.py            → IELTS rubric, band scores, CEFR mapping
utils.py              → Formatting, timers, silence detection
style.css             → Custom dark-mode CSS
```

## Local Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Create .env with OPENAI_API_KEY=your_key
streamlit run app.py
# Runs on http://localhost:8501
```

## Key Commands

- `streamlit run app.py` — start the dev server
- `pip install -r requirements.txt` — install dependencies

## Environment Variables

- `OPENAI_API_KEY` (required) — OpenAI API key
- `DEEPGRAM_API_KEY` (optional) — for future use

## Important Notes

- Never commit `.env` or API keys
- `config.py` holds all model names, scoring weights, and test structure constants
- The app uses a multi-step state machine flow: START → PART1 → PART2 → PART2_LONG_RESPONSE → PART2_ROUNDING → PART3 → RESULTS
- Scoring uses a hybrid approach: objective speech metrics (WPM, pauses) + LLM evaluation across 5 weighted criteria
