# AI English Speaking Evaluator

**Live demo:** [https://ai-speaking-evaluator.streamlit.app](https://ai-speaking-evaluator.streamlit.app)

AI-powered conversational English speaking test that evaluates fluency, grammar, and coherence through a structured multi-part interview. The system generates adaptive questions, analyzes responses using speech + LLM pipelines, and produces IELTS-style band scores (1–9) with detailed feedback.

---

## Demo

Try the live app here: **[https://ai-speaking-evaluator.streamlit.app](https://ai-speaking-evaluator.streamlit.app)**

> *(Optional but highly recommended: add a demo GIF + screenshots here — see “Adding visuals” section below.)*

---

## Overview

This project simulates a professional English speaking exam similar to IELTS. Users complete a 3-part adaptive conversation where responses are analyzed for fluency, vocabulary, grammar, and coherence.

The system combines:

* Real-time speech transcription (voice mode)
* LLM-based conversational examiner
* Hybrid scoring engine (objective metrics + GPT evaluation)
* IELTS-style band scoring with CEFR mapping

---

## Technical Highlights

* Designed a multi-stage conversational **state machine** for a structured speaking exam flow
* Built a real-time speech pipeline using **Whisper STT** + **OpenAI TTS**
* Implemented a **hybrid scoring engine** combining objective speech metrics (WPM, pauses) with LLM evaluation
* Engineered **adaptive questioning** using relevance checks and follow-ups based on response depth
* Created an IELTS-style rubric with **weighted scoring** across 5 criteria + **CEFR mapping (A1–C2)**
* Developed a modular codebase separating UI, voice processing, LLM logic, and scoring

---

## Features

### Voice Mode

* Real-time speech-to-text transcription
* Word-level timestamps (when available)
* Speaking rate (WPM) calculation
* Pause detection and fluency analysis
* Automated timing controls

### Text Mode

* Typing-based alternative assessment
* Silence detection with check-ins / auto-skip
* Full scoring and feedback preserved

### Adaptive Conversation Engine

* Questions dynamically generated from user responses
* Follow-ups based on response depth and relevance
* Two-strike redirect for off-topic answers
* Theme extraction across sections (Part 2 → Part 3 continuity)

### Professional Scoring

* IELTS **1–9** band scoring
* 5 weighted criteria:

  * Fluency & Coherence (25%)
  * Lexical Resource (20%)
  * Grammar (20%)
  * Cohesion (15%)
  * Task Response (20%)
* CEFR mapping (A1–C2)
* Detailed strengths + improvement feedback per criterion

---

## System Architecture

```
app.py                → Streamlit UI + conversational state machine
llm_functions.py      → GPT examiner prompts, question generation, scoring calls
voice_functions.py    → Audio I/O, Whisper STT, timing + pause metrics
scoring.py            → IELTS rubric, penalties, band score + CEFR mapping
state_management.py   → Part initialization + session state helpers
utils.py              → Formatting, timers, general utilities
config.py             → Models, constants, thresholds, rubric weights
```

---

## Test Structure

### Part 1: Interview

* 3 topic areas
* Adaptive follow-up questions
* Target: concise responses (word limits enforced)

### Part 2: Long Turn

* Generated prompt card + preparation time
* Extended response + follow-up questions
* Target: longer response with structure and detail

### Part 3: Discussion

* Theme extracted from Part 2
* Higher-level reasoning questions
* Dynamic follow-ups based on response depth

---

## Technologies

* **Frontend/UI:** Streamlit
* **LLM:** OpenAI GPT-4o-mini (examiner), GPT-4o (scoring)
* **STT:** OpenAI Whisper (with word-level timestamps when supported)
* **TTS:** OpenAI TTS
* **Styling:** Custom CSS
* **Language:** Python

---

## Why I Built This

Traditional English speaking exams (IELTS/TOEFL) can be expensive, stressful, and difficult to access consistently—especially for global learners who want frequent practice and actionable feedback. I built this project to explore how modern LLMs and speech models can simulate a realistic speaking test experience: adaptive questioning, real-time fluency metrics, and detailed rubric-based scoring that helps learners improve between attempts.

---

## Running Locally

Clone the repo:

```bash
git clone https://github.com/YOUR_USERNAME/ai-english-speaking-evaluator.git
cd ai-english-speaking-evaluator
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```text
OPENAI_API_KEY=your_key_here
```

Run:

```bash
streamlit run app.py
```

---

## Adding Visuals (Recommended)

Add a short GIF + a few screenshots so recruiters can understand the product in 5 seconds.

1. Record a 15–25s walkthrough (start test → answer → results) and save as `demo.gif`
2. Take screenshots (main UI, voice mode, results) as `screenshot1.png`, `screenshot2.png`, `screenshot3.png`
3. Put the files in the repo root (or `/assets`) and add this under the **Demo** section:

```md
### Demo Walkthrough
![Demo](demo.gif)

### Screenshots
![Interface](screenshot1.png)
![Voice Mode](screenshot2.png)
![Results](screenshot3.png)
```
