# Versa Speaking Test - Project Plan & Build Plan

## Project Overview
An AI-powered English speaking assessment tool that evaluates users through a 3-part conversation, providing IELTS-style scoring (1-9) with detailed feedback.

## The Optimal 3-Part Assessment Flow

### I. User Onboarding (The Setup)
Before the clock starts, the bot establishes the "Testing Environment" to reduce user anxiety.

- **Introduction**: "Hello, I'm your Speaking Assistant. My goal is to estimate your English level through a short conversation."
- **Structure**: "We will do three parts: a short interview, a 2-minute story, and a deeper discussion. The whole process takes about 11–14 minutes."
- **The Consent**: "I will record your responses to analyze your fluency and vocabulary. Are you ready to begin?"

### Part 1: The Warm-up (2–3 mins)
- **Goal**: Establish baseline comfort.
- **Logic**: Ask exactly 3 questions about 3 randomly selected topics from: Family, Hobbies, Work and Studies, Going out, Hometown, Daily routine, Friends, Food.
- **Implementation**: GPT generates questions dynamically (not scripted) for natural conversation flow.
- **Question Strategy**: Questions build off the user's previous relevant answers. Third question leads to topic transition.
- **Redirect Logic**: Two-strike policy - first off-topic answer gets redirect, second off-topic answer moves to next question.
- **Word Limit**: 65 words per response (displayed as "brief, conversational responses").
- **Optimal Strategy**: Use this part primarily to calculate Base Fluency (WPM) and Grammar Accuracy on simple tenses. It's the "floor" of their ability.

### Part 2: The Long Turn (3–4 mins)
- **Goal**: Test "Discourse Management" (can they organize a 2-minute talk?).
- **Logic**: Provide the Prompt Card (one of 8 topics: person, place, object, event, activity, media, decision, journey). Force a 60s prep silence (5s for testing).
- **Prompt Card**: GPT generates main prompt with 3-4 bullet point assistive questions.
- **Long Response**: 
  - 400 word maximum (hard limit)
  - 50 word soft minimum (warns and keeps text if under, doesn't clear)
  - Redirect logic applies (two-strike policy)
- **Rounding-Off Questions**: 
  - Exactly 2 follow-up questions related to long response
  - 65 word limit per answer
  - Redirect logic applies
- **Transition**: Fixed message displayed with "Continue to Part 3" button
- **Optimal Strategy**: This is where you measure Organization and Length of Response. If they speak for less than 90 seconds, it's a major signal of a lower level.

### Part 3: The Deep Dive (4–5 mins)
- **Goal**: Find the "ceiling."
- **Logic**: Exactly 3 main questions related to Part 2's theme (GPT extracts 2-4 word theme from Part 2 prompt).
- **Question Style**: Simple, clear, conversational questions (not overly advanced phrasing).
- **Adaptive Follow-ups**: 
  - After first answer to main question: Always ask follow-up #1
  - After follow-up #1: If first answer ≥30 words, move to next main question. If <30 words, check current answer - if ≥20 words move on, if <20 words ask follow-up #2
  - After follow-up #2: Always move to next main question
- **Building Off**: Questions build off user's previous relevant responses, exploring related angles.
- **Redirect Logic**: Two-strike policy (redirects reset between questions, don't count toward follow-up limit).
- **Word Limit**: 150 words per response (displayed as "thoughtful, detailed responses").
- **Optimal Strategy**: This is the most important part for Lexical Resource and Cohesion. This is where the LLM looks for "big ideas" and complex linkers.

## The Optimal Rubric (Weighted & Categorized)

To get an IELTS-style score (1–9), we weight 10 criteria into four "Buckets."

### Bucket 1: Fluency & Speed (Weight: 25%)
- **Rate of Speech (ASR-based)**: Words per minute (excluding silence). Optimal: 120–150 WPM = High Score.
- **Pause Distribution (ASR-based)**: Are pauses at sentence boundaries (Good) or mid-clause (Bad)?
- **Repetition & Repair (ASR/LLM)**: Does the user constantly restart sentences?

### Bucket 2: Lexical Resource & Grammar (Weight: 25%)
- **Vocabulary Range (LLM-based)**: Usage of "uncommon" words and successful paraphrasing when they get stuck.
- **Grammatical Error Rate (LLM-based)**: Count of mistakes per 100 words. Optimal: Prioritize "Global Errors" (mistakes that make them hard to understand) over "Local Errors" (small slips like 's' on verbs).

### Bucket 3: Coherence & Organization (Weight: 25%)
- **Cohesive Devices (LLM-based)**: Effective use of "linkers" (However, Consequently).
- **Organization (LLM-based)**: Is there a logical flow (Introduction → Detail → Conclusion)?
- **Length of Response (Time-based)**: Did they meet the 2-minute target in Part 2?

### Bucket 4: Effectiveness & Relevance (Weight: 25%)
- **Overall Effectiveness (LLM-based)**: Did they successfully communicate the message despite errors?
- **Relevance (LLM-based)**: Did they answer the specific question or drift off-topic?
- **Redirection Penalty**: Deduct 0.5 points for every time the bot had to "Redirect" an off-topic user.

## Handling the Edge Cases (The "Robustness" Logic)

### 1. The "Silent" Student (State Management)
- **Threshold**: 12 seconds of ASR silence.
- **Fallback 1**: "Take your time—start whenever you're ready."
- **Fallback 2**: "If it helps, you can start by describing [Topic Specific]."
- **Outcome**: If silence persists after 2 helps, skip the question. Score Impact: 0 for that specific "Length of Response" segment.

### 2. The "Off-Topic" Student (Semantic Filtering)
- **Logic**: After each answer, LLM does a "Relevance Check" using GPT.
- **Two-Strike Policy**:
  - **First off-topic answer**: Generate polite redirect message, stay on same question
  - **Second off-topic answer**: Say "Thank you. Let's move on." and move to next question
- **Implementation**: Redirect count resets when moving to new questions (including follow-ups).
- **Applies to**: All questions in Part 1, Part 2 long response, Part 2 rounding-off questions, Part 3 main questions and follow-ups.
- **Score Impact**: Major deduction in "Relevance" bucket.

## The Feedback & Suggestions

At the end of the test, the bot provides a "Prep Roadmap" based on the 10 criteria.

- **If Repetition is High**: "You repeated the word 'important' 5 times. Try using synonyms like 'essential', 'crucial', or 'vital'."
- **If Fluency is Low**: "You have a high number of mid-clause pauses. Practice 'Shadowing' exercises to improve your rhythm."
- **If Relevance is Low**: "Make sure to answer the specific question asked before expanding into other areas."

### General Tips:
- "Don't speak too fast; aim for clarity."
- "It's okay to pause to think—use 'filler phrases' like 'That's a tough question, let me see...' instead of silence."
- "Focus on accuracy over big words."

---

## The 10-Hour Build Sprint

### Phase 1: The Skeleton (Hours 1–3)
- **State Machine Logic**: Build a simple controller (Python) that manages the test flow (Onboarding -> Part 1 -> Part 2 -> Part 3 -> Scoring).
- **Prompt Engineering**: Create your "System Prompts" for the LLM. You need two:
  - **The Examiner**: To handle conversation and redirects.
  - **The Grader**: To analyze the final transcript against your 4 buckets.
- **Basic Text Loop**: Get the test working entirely in text first. If you can't "pass" the test via typing, the voice version will be a mess.

### Phase 2: The Sensory Organs (Hours 4–6)
- **STT (Speech-to-Text) Integration**: Use Deepgram API.
  - **Crucial**: Ensure you are getting word-level timestamps. You need these for your "Pause Distribution" and "WPM" metrics.
- **TTS (Text-to-Speech) Integration**: Use ElevenLabs or OpenAI TTS. These are low-latency and sound professional enough for an examiner.
- **The Timer Logic**: Implement the 12-second silence detector. This should be a client-side or local listener that triggers your "Fallback" messages.

### Phase 3: The Brain & Scoring (Hours 7–9)
- **Quantitative Script**: Write the function that parses the ASR JSON.
  - Calculate: Total Words / (End_Time - Start_Time).
  - Flag any pause > 1.0s and check if it's at a sentence boundary (punctuation).
- **Qualitative Analysis**: Send the full transcript to the "Grader" prompt.
  - **Tip**: Use JSON Mode or Function Calling to ensure the LLM returns the rubric scores in a format your code can parse into a final report.

### Phase 4: Feedback & Polishing (Hour 10)
- **The Scorecard**: Build the UI/Console output for the "Prep Roadmap."
- **Final Testing**: Run a "Silent" test and an "Off-Topic" test to ensure your fallbacks trigger correctly.

## Tech Stack

| Component | Best Fast Option | Why? |
|-----------|-----------------|------|
| Logic | Python (FastAPI/Streamlit) | Easiest for data processing and ASR parsing. |
| STT | Deepgram | Fastest for real-time word-level timestamps. |
| LLM | GPT-4o-mini | High speed, low cost, excellent at following JSON schemas. |
| UI | Streamlit | You can build a web interface for this in 20 minutes. |

## Current Progress

✅ **Completed:**
- **Project Setup**
  - Project structure created
  - Dependencies installed (openai, deepgram-sdk, streamlit, python-dotenv)
  - .env file created for API keys
  - State machine: START → ONBOARDING → PART_1 → PART_2 → PART_3 → SCORING
  - Streamlit UI foundation with custom CSS (style.css)

- **Onboarding Flow**
  - 3-step introduction with consent
  - Go back option at consent screen

- **Part 1: The Interview (Text Mode) ✅**
  - GPT-generated questions from 8 topics (removed Childhood for brevity)
  - Randomly selects 3 topics per test
  - **Strict counts**: Exactly 3 questions per topic, exactly 3 topics
  - Brief acknowledgment + follow-up style
  - **Build-off logic**: Questions reference previous relevant answers (first 2 questions only)
  - **Redirect logic**: Two-strike policy implemented with relevance checking
  - 65 word limit (displayed as "brief, conversational responses")
  - Conversation history tracking
  - Examiner LLM prompt implemented
  - Enter key support with `st.form(clear_on_submit=True)`
  - Fixed transition message with "Continue" button

- **Part 2: The Long Turn (Text Mode) ✅**
  - GPT-generated prompt cards (8 topic types)
  - Main prompt with 3-4 bullet point assistive questions
  - Preparation timer (60s normal, 5s for testing) with skip option
  - **Long response**: 400 word max, 50 word soft minimum (warns without clearing)
  - **Rounding-off questions**: Exactly 2 follow-up questions
  - 65 word limit for rounding-off (displayed as "brief responses")
  - Redirect logic for both long response and rounding-off questions
  - GPT generates questions based on user's long response
  - Fixed transition message with "Continue to Part 3" button

- **Part 3: The Discussion (Text Mode) ✅**
  - Theme extraction (2-4 words) from Part 2 prompt using GPT
  - **Strict count**: Exactly 3 main questions
  - Simple, conversational question phrasing
  - **Adaptive follow-ups**: 1-2 follow-ups per main question based on word count
    - First answer always gets follow-up #1
    - Logic: First answer ≥30 words = 1 total follow-up; <30 words = check follow-up #1 answer (≥20 words = done, <20 words = ask follow-up #2)
  - Questions build off previous relevant responses
  - Redirect logic (two-strike policy, resets between questions)
  - 150 word limit (displayed as "thoughtful, detailed responses")
  - Fixed completion message with "View Results" button

- **Results/Scoring Page ✅**
  - CEFR levels (A1-C2) display with descriptions
  - Placeholder B1 level assessment
  - Comprehensive improvement tips (Delivery & Fluency, Content & Relevance, Practice Methods)
  - External resource link (GlobalExam IELTS guide)
  - "Take Test Again" button (resets all session state)

- **UI/UX Enhancements**
  - Custom CSS to remove red focus borders (changed to gray)
  - Form hint text handling
  - Word limit displays (hard limits and soft guidance)
  - Natural language length expectations (not just word counts)
  - Debug controls: Skip to Part 1, Part 2, Part 3, or Results

- **LLM Integration**
  - GPT-4o-mini for Examiner role
  - Relevance checking with GPT
  - Redirect message generation
  - Theme extraction
  - Dynamic question generation for all parts
  - Acknowledgment generation

🔄 **In Progress:**
- **Phase 2: Voice Integration** ✅ (COMPLETED)
  - Mode selection screen (Voice Mode vs Text Mode)
  - OpenAI TTS for reading questions aloud (auto-play + replay button)
  - OpenAI Whisper API for speech-to-text transcription
  - Browser-based audio recording using `st.audio_input()`
  - Hard cutoff timers for voice mode (30s/120s/30s/60s with 10s buffer)
  - Silence detection preserved for text mode
  - Check-in messages and auto-skip functionality (text mode)
  - Text input fully preserved as separate mode

📋 **Next Up:**

- **Phase 3: Evaluation & Scoring**
  - Build Grader LLM prompt for actual scoring
  - Implement scoring logic (4 buckets: Fluency, Lexical/Grammar, Coherence, Effectiveness)
  - Replace placeholder B1 with data-driven CEFR assessment
  - Word-per-minute (WPM) calculation
  - Pause distribution analysis
  - Vocabulary and grammar assessment
  - Add personalized feedback based on conversation analysis
  - Progress tracking across multiple test sessions
