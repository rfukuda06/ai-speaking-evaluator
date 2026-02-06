# AI English Speaking Evaluator

A professional AI-powered English speaking assessment tool that evaluates users through a comprehensive 3-part conversation, providing IELTS-style band scores (1-9) with detailed feedback across multiple criteria.

## Features

- **Voice Mode**: Natural speech-to-text assessment with real-time transcription and fluency analysis
- **Text Mode**: Alternative typing-based assessment for quiet environments
- **IELTS 1-9 Band Scoring**: Comprehensive evaluation across 5 weighted criteria
- **Adaptive Testing**: Dynamic question generation that builds off user responses
- **Word-Level Analysis**: Pause detection and speaking rate measurement (voice mode)
- **Professional UI**: Clean, modern interface optimized for assessment

## Project Structure

```
speaking-test/
├── app.py                   # Main Streamlit application (UI and state machine)
├── config.py                # Configuration, constants, and API clients
├── state_management.py      # Session state initialization functions
├── utils.py                 # General utility functions
├── voice_functions.py       # Audio/TTS/STT processing
├── llm_functions.py         # GPT interaction and content generation
├── scoring.py               # Metrics calculation and IELTS scoring
├── style.css                # Professional CSS styling
├── requirements.txt         # Python dependencies
├── .env                     # API keys (not in git)
└── .gitignore              # Git ignore rules
```

## Module Breakdown

### `app.py` (~2,690 lines)
Main application entry point with:
- Streamlit UI rendering
- State machine logic (START → ONBOARDING → MODE_SELECTION → PART_1 → PART_2 → PART_3 → SCORING)
- Session state initialization
- Quick Navigation panel for demo purposes

### `config.py` (~100 lines)
Configuration and constants:
- OpenAI API client initialization
- Model settings (GPT-4o-mini for examiner, GPT-4o for scoring)
- Part 1 topics and Part 2 categories
- Word limits and ideal ranges
- Timer settings for each section
- Scoring weights and thresholds
- Pause detection parameters

### `utils.py` (~120 lines)
General utility functions:
- CSS loader
- Conversation history formatting
- Silence detection (text mode check-ins and auto-skip)
- Part completion messages
- Timer management

### `state_management.py` (~85 lines)
Part initialization functions:
- `initialize_part1()`: Select 3 random topics, assign 2-3 questions per topic
- `initialize_part2()`: Select category, generate prompt card with GPT
- `initialize_part3()`: Extract theme from Part 2, reset state

### `voice_functions.py` (~170 lines)
Audio processing functions:
- `text_to_speech()`: OpenAI TTS for question audio
- `transcribe_audio()`: Whisper STT with optional word-level timestamps
- `store_voice_timing_data()`: Calculate and store WPM, pause metrics
- `check_voice_timer_expired()`: Hard timer logic for voice mode
- Time formatting utilities

### `llm_functions.py` (~330 lines)
GPT-4 interaction functions:
- Examiner prompt creation (Part 1, 2, 3)
- Question generation (main and follow-up)
- Acknowledgment generation
- Relevance checking
- Redirect message generation
- Theme extraction from Part 2
- Rounding-off question generation

### `scoring.py` (~350 lines)
Scoring and metrics:
- Response metrics calculation (word counts, timeouts)
- Voice metrics aggregation (WPM, pauses)
- Part-specific analysis
- Penalty counting
- IELTS band score calculation with GPT-4
- Comprehensive rubric with 5 weighted criteria
- CEFR level mapping (A1-C2)

## Installation

### Prerequisites
- Python 3.8+
- OpenAI API key

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd speaking-test
```

2. Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_api_key_here
```

5. Run the application:
```bash
streamlit run app.py
```

## Test Flow

### Part 1: The Interview (2-3 minutes)
- 3 randomly selected topics
- 2-3 questions per topic (randomized)
- Questions build off previous relevant answers
- **Word limit**: 65 words per response
- **Redirect logic**: Two-strike policy for off-topic answers

### Part 2: The Long Turn (3-4 minutes)
- GPT-generated prompt card with 3-4 bullet points
- 60-second preparation time
- **Main response**: 150+ words ideal (100+ acceptable, 400 max)
- 2 rounding-off follow-up questions
- **Rounding word limit**: 20-50 words ideal (65 max)

### Part 3: The Discussion (4-5 minutes)
- Theme extracted from Part 2 prompt
- 3 main questions with adaptive follow-ups
- **Follow-up logic**: 1-2 follow-ups based on response length
- **Word limit**: 50-100 words ideal (150 max)

### Scoring
- IELTS 1-9 band scale
- 5 weighted criteria (Fluency 25%, Lexical 20%, Grammar 20%, Cohesion 15%, Task 20%)
- Penalties: -0.5 per timeout/irrelevant answer
- CEFR mapping (A1-C2)
- Detailed feedback with strengths and improvements

## Technologies

- **Frontend**: Streamlit
- **LLM**: OpenAI GPT-4o-mini (examiner), GPT-4o (scoring)
- **TTS**: OpenAI TTS-1 (alloy voice)
- **STT**: OpenAI Whisper with word-level timestamps
- **Styling**: Custom CSS with professional dark theme
- **State Management**: Streamlit session_state

## Key Features

### Voice Mode
- Natural speech assessment
- Word-level timestamp capture
- Pause detection and analysis
- Speaking rate (WPM) calculation
- Automated timing controls

### Text Mode
- Typing-based alternative
- Silence detection with check-ins
- Auto-skip for inactive users
- Full functionality preserved

### Adaptive Logic
- Questions build off previous responses
- Dynamic follow-up counts based on answer length
- Two-strike redirect policy for irrelevant answers
- Automatic theme extraction and continuation

### Professional Scoring
- Objective metrics (word count, WPM, pauses)
- Subjective GPT-4 assessment (vocabulary, grammar, coherence)
- Hybrid approach for balanced evaluation
- Detailed criterion breakdown with justifications

## Quick Navigation

The app includes a "Quick Navigation" panel for demonstration purposes, allowing you to:
- Switch between voice and text modes
- Jump to any section (Start, Part 1, Part 2, Part 3, Results)
- Test specific features without completing the full assessment

This feature is intended for portfolio reviewers and developers, not for production exam use.

## Development

### Running in Development Mode
```bash
streamlit run app.py --server.runOnSave true
```

### Project Guidelines
- All functionality tested in both voice and text modes
- No emojis in production code
- Professional styling consistent throughout
- Modular architecture for maintainability
- Comprehensive error handling with fallbacks


