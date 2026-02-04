# Implementation Progress & Documentation

This document tracks what we've built, the key concepts used, and the main building blocks of the Speaking Test application.

---

## ✅ Completed Features

### 1. Project Setup
- Created Python virtual environment (`.venv`)
- Installed dependencies: `openai`, `deepgram-sdk`, `streamlit`, `python-dotenv`
- Set up `.env` file for secure API key storage
- Created basic Streamlit app structure

### 2. State Machine Foundation
- Implemented basic state management using Streamlit's `session_state`
- Created initial states: `START`, `ONBOARDING`, `PART_1`
- State flow: `START` → `ONBOARDING` → `PART_1` (→ `PART_2` → `PART_3` → `SCORING`)

### 3. Onboarding Flow
- **3-step introduction process:**
  1. Introduction message (explains the assistant's purpose)
  2. Structure explanation (describes the 3-part test format)
  3. Consent question (asks permission to record)
- Each step has a "Continue" button to progress
- Consent screen includes "Go back" option to return to start
- User must consent before proceeding to Part 1

### 4. Part 1: The Interview (Text Mode)
- **GPT-generated questions from topics:**
  - Randomly selects 3 topics from 8 available topics (Family, Hobbies, Work and Studies, Going out, Hometown, Daily routine, Friends, Food)
  - **Removed Childhood** (requires more reflection, not suitable for quick questions)
  - **Strict counts:** Exactly 3 questions per topic, exactly 3 topics (enforced programmatically)
  - Questions are conversational and natural
- **Build-off logic:**
  - Questions 1 & 2 of each topic build off user's previous relevant answers
  - Question 3 leads to topic transition (doesn't build off)
  - If user's answer was irrelevant (redirected twice), next question doesn't build off
- **Redirect logic (two-strike policy):**
  - First off-topic answer: Polite redirect, stay on same question
  - Second off-topic answer: "Thank you. Let's move on" and move to next question
  - Redirect count resets for each new question
  - Relevance checking uses GPT
- **Conversation flow:**
  - User types answers in text input
  - **Enter key support:** User can press Enter to submit (using `st.form()`)
  - **Auto-clear input:** Input field clears after submission (`clear_on_submit=True`)
  - GPT acknowledges answers briefly (stored in `part1_acknowledgment`)
  - Acknowledgment + next question concatenated and displayed together
  - All conversation stored in history for later scoring
- **Word limit:**
  - 65 words maximum (hard limit, blocks submission if exceeded)
  - Displayed as "Expected length: Brief, conversational responses (a few sentences)"
- **Completion:**
  - Fixed transition message: "Thank you for your responses; that completes Part 1. Now, let's move on to Part 2"
  - "Continue to Part 2" button appears
- **State tracking:**
  - Tracks current topic (0, 1, 2)
  - Tracks questions asked per topic (0-3)
  - Tracks redirect count per question
  - Tracks last relevant answer for build-off logic
  - Stores full conversation history
- **Examiner LLM integration:**
  - Uses GPT-4o-mini with custom system prompt
  - Separate prompts for asking questions vs. acknowledging answers
  - Question prompt conditionally asks to build off previous answer
  - Acknowledgment prompt explicitly told not to ask questions

---

## 🔑 Key Concepts Explained

### Session State (`st.session_state`)
**What it is:** Streamlit's way to remember information between button clicks and page refreshes.

**Why we need it:** Web apps are "stateless" by default—they forget everything after each interaction. Session state lets us remember where the user is in the test flow.

**How we use it:**
- `st.session_state.step` - Tracks which major section we're in (START, ONBOARDING, PART_1, PART_2, etc.)
- `st.session_state.onboarding_step` - Tracks progress within the onboarding flow (0, 1, or 2)
- `st.session_state.part1_*` - Multiple variables tracking Part 1 progress (topics, questions, conversation history)

### State Machine Pattern
**What it is:** A way to organize your app into distinct "states" or "screens" that the user moves through in a specific order.

**Why we use it:** The speaking test has a clear flow: onboarding → part 1 → part 2 → part 3 → scoring. A state machine makes it easy to control this flow.

**Current flow:**
```
START → ONBOARDING (3 steps) → PART_1 → PART_2 → PART_3 → SCORING
```

### Rerun (`st.rerun()`)
**What it is:** A command that refreshes the Streamlit page to show updated content.

**Why we need it:** When a user clicks a button and we change the state, we need to refresh the page so they see the new screen. Without `st.rerun()`, the page wouldn't update.

### OpenAI API Integration
**What it is:** We use OpenAI's GPT-4o-mini model to generate the examiner's questions and responses.

**How it works:**
1. We create a "system prompt" that tells GPT how to behave (friendly examiner, ask specific questions, etc.)
2. We send the conversation history so GPT knows what's been discussed
3. GPT generates a natural response (question, acknowledgment, or redirect)
4. We display GPT's response to the user

**Why GPT-4o-mini:** Fast, affordable, and good at following instructions. Perfect for generating conversational questions.

**Multiple use cases:**
- Generating Part 1 questions (with/without build-off)
- Generating Part 1 acknowledgments
- Generating Part 2 prompt cards
- Generating Part 2 rounding-off questions
- Generating Part 3 questions (main and follow-up)
- Generating Part 3 acknowledgments
- Checking relevance of user responses
- Generating redirect messages
- Extracting themes from Part 2 prompts

### Relevance Checking (`check_relevance()`)
**What it is:** A function that uses GPT to determine if a user's answer is relevant to the question asked.

**How it works:**
1. Takes user's response, the question, and conversation context
2. Sends to GPT with specific prompt asking for relevance judgment
3. GPT returns JSON with `is_relevant` (boolean) and `relevance_score` (0-1)
4. We consider relevant if `is_relevant=true` OR `relevance_score >= 0.7`

**Why we need it:** To detect off-topic answers and trigger the redirect system.

### Redirect Logic (Two-Strike Policy)
**What it is:** A system that gently corrects off-topic answers, giving users a second chance.

**How it works:**
1. **First off-topic answer:** Generate polite redirect message, stay on same question, increment redirect counter
2. **Second off-topic answer:** Say "Thank you. Let's move on.", move to next question, reset counter
3. **Relevant answer:** Reset redirect counter to 0

**Where it applies:** All questions in Parts 1, 2, and 3 (including main questions and follow-ups)

**Key feature:** Redirect count resets when moving to new questions, so each question gets its own two strikes.

### Build-Off Logic (Part 1 & Part 3)
**What it is:** A technique where questions reference and expand on previous user answers.

**Part 1 implementation:**
- Questions 1 & 2 build off previous relevant answers
- Question 3 transitions to new topic (doesn't build off)
- If answer was irrelevant (redirected twice), next question doesn't build off
- Stored in `part1_last_relevant_answer` and `part1_should_build_off` flags

**Part 3 implementation:**
- All questions (main and follow-up) build off previous relevant responses
- Prompt explicitly instructs: "Build your next question off what the candidate just said"
- Creates more natural, flowing conversation

### Adaptive Follow-Ups (Part 3)
**What it is:** A word-count based system that determines how many follow-up questions to ask.

**Logic:**
- First answer to main question: Always ask follow-up #1, store word count
- After follow-up #1:
  - If first answer ≥ 30 words: Done (only 1 follow-up total)
  - If first answer < 30 words: Check current answer
    - If current ≥ 20 words: Done (1 follow-up total)
    - If current < 20 words: Ask follow-up #2
- After follow-up #2: Always done (max 2 follow-ups)

**Why:** Ensures candidates provide sufficient depth without over-questioning those who speak thoroughly.

**State tracking:** Uses `part3_followups_asked` (0-2) and `part3_first_answer_word_count`.

### IELTS Scoring System (1-9 Band Scale)
**What it is:** A comprehensive GPT-4 based scoring system that evaluates speaking ability on the official IELTS 1-9 band scale.

**Architecture:**
1. **Metric Calculation** (Objective): Code-based analysis of conversation data
   - Response counts, word counts, timeouts, irrelevant answers
   - Voice metrics: WPM, pause frequency, pause lengths (voice mode only)
   - Part-specific metrics: Word counts vs ideal ranges
2. **GPT-4 Assessment** (Subjective): AI analysis with detailed rubric
   - 5 criteria with band descriptors (9/7/5/3)
   - Receives formatted metrics + full conversation transcript
   - Returns structured JSON with scores and justifications
3. **Weighted Calculation**: Final band = sum of (criterion_score × weight)
4. **Results Display**: User-friendly breakdown with feedback

**5 Scoring Criteria:**
1. **Fluency & Coherence (25%)**: WPM 120-160 ideal, pause placement (boundary vs mid-clause), hesitation, flow
2. **Lexical Resource (20%)**: Appropriate vocabulary range, natural collocation, paraphrasing ability
3. **Grammatical Range & Accuracy (20%)**: Structure variety, complex attempts (errors OK if clear), effectiveness
4. **Coherence & Cohesion (15%)**: Linking words, logical organization, idea progression
5. **Task Achievement (20%)**: Length targets met, relevance, question addressing, penalties applied

**Penalty System:**
- Timeouts: -0.5 band from Task Achievement each
- Irrelevant answers: -0.5 band from Task Achievement each
- Minimum score: 1.0

**Why this approach:** Combines objective metrics (hard data) with subjective assessment (GPT's language understanding) for balanced, accurate scoring similar to human IELTS examiners.

### Word-Level Timestamps & Pause Analysis (Voice Mode)
**What it is:** Whisper API captures exact timing of each word spoken, enabling precise pause detection and fluency analysis.

**How it works:**
1. Transcribe audio with `timestamp_granularities=["word"]`
2. Returns: `{text: "...", words: [{word, start, end}], duration: X}`
3. Calculate pauses: `next_word.start - current_word.end`
4. Categorize: <0.3s (ignored), 0.3-1.5s (counted), >1.5s (flagged as long)
5. Reconstruct text with markers: `[pause: X.Xs]` inserted at actual locations
6. GPT sees pause-marked transcript and can assess placement (boundary vs mid-clause)

**Why it matters:** 
- Natural pauses between sentences = good (thinking time)
- Frequent mid-clause pauses = concerning (processing difficulty)
- Previous system could only count pauses, not assess placement quality
- Now GPT has full context to make nuanced fluency judgments

**Example:**
```
Candidate: I like to travel. [pause: 2.1s] Because it broadens my mind.
```
vs.
```
Candidate: I like to [pause: 2.1s] travel because it broadens my mind.
```
GPT can tell the first is natural, the second suggests disfluency.

---

## 🏗️ Main Building Blocks

### 1. State Management
- **Location:** Top of `app.py` (lines ~39-153)
- **Purpose:** Initialize and track user progress through the test
- **Key variables organized by part:**
  - **Global:** `step`, `onboarding_step`
  - **Part 1:** `part1_initialized`, `part1_topics`, `part1_current_topic_index`, `part1_questions_asked`, `part1_conversation_history`, `part1_current_question`, `part1_acknowledgment`, `part1_redirect_count`, `part1_last_relevant_answer`, `part1_should_build_off`, `part1_completion_message`, `part1_showing_completion`
  - **Part 2:** `part2_initialized`, `part2_prompt_card`, `part2_prep_time_remaining`, `part2_prep_started`, `part2_prep_complete`, `part2_skip_prep`, `part2_conversation_history`, `part2_long_response_submitted`, `part2_rounding_off_questions`, `part2_rounding_question_index`, `part2_rounding_questions_answered`, `part2_rounding_redirect_count`, `part2_rounding_acknowledgment`, `part2_long_response_redirect_count`, `part2_long_response_redirect_message`, `part2_draft_response`, `part2_completion_message`, `part2_showing_completion`
  - **Part 3:** `part3_initialized`, `part3_theme`, `part3_conversation_history`, `part3_questions_asked`, `part3_current_question`, `part3_acknowledgment`, `part3_redirect_count`, `part3_followups_asked`, `part3_first_answer_word_count`, `part3_completion_message`, `part3_showing_completion`

### 2. Main Function Structure
- **Location:** `main()` function in `app.py`
- **Pattern:** Uses `if/elif` statements to check the current state and display the appropriate screen
- **Flow control:** Each state has buttons that change the state and trigger `st.rerun()`
- **States:** START → ONBOARDING → PART_1 → PART_2 → PART_3 → SCORING

### 3. Helper Functions

#### Core LLM Functions
- **`get_examiner_response(system_prompt, conversation_history)`**: Calls OpenAI API with system prompt and history
- **`format_conversation_history(history)`**: Converts history list to readable string for GPT context
- **`check_relevance(user_response, question, context)`**: Uses GPT to check if answer is on-topic
- **`generate_redirect_message(question)`**: Uses GPT to create polite redirect for off-topic answers

#### Part 1 Functions
- **`initialize_part1()`**: Randomly selects 3 topics and resets all Part 1 state variables
- **`get_examiner_prompt_part1(...)`**: Creates system prompts for Part 1 (separate for questions vs acknowledgments)

#### Part 2 Functions
- **`initialize_part2()`**: Generates prompt card and resets Part 2 state
- **`generate_part2_prompt_card()`**: Uses GPT to create prompt with main question and bullet points
- **`generate_rounding_off_questions(long_response, main_prompt)`**: Uses GPT to create 2 follow-up questions
- **`get_examiner_prompt_part2(conversation_history, phase)`**: Creates prompts for Part 2 acknowledgments

#### Part 3 Functions
- **`initialize_part3()`**: Extracts theme from Part 2 and resets Part 3 state
- **`extract_theme_from_part2(part2_prompt)`**: Uses GPT to extract 2-4 word theme
- **`get_examiner_prompt_part3(...)`**: Creates prompts for Part 3 (questions, follow-ups, acknowledgments)
- **`generate_part3_question(..., question_type)`**: Generates main or follow-up questions
- **`generate_part3_acknowledgment(...)`**: Generates brief acknowledgments

#### Completion Functions
- **`generate_part_completion_message(part_number, history)`**: Returns fixed transition message

#### Scoring Functions (Phase 3)
- **`calculate_response_metrics(conversation_history)`**: Calculates basic response statistics
- **`calculate_voice_metrics(voice_timing_data)`**: Aggregates voice/fluency metrics (WPM, pauses)
- **`calculate_part_specific_metrics(part1_history, part2_history, part3_history)`**: Per-part word count analysis
- **`count_timeouts_and_relevance(conversation_history)`**: Scans for timeouts and irrelevant answers
- **`generate_metrics_summary(...)`**: Master function combining all metrics
- **`combine_conversation_histories(...)`**: Merges all parts with labels
- **`format_metrics_for_prompt(metrics)`**: Formats metrics for GPT prompt
- **`format_full_conversation(combined_history, voice_timing_data)`**: Formats conversation with pause markers
- **`reconstruct_text_with_pauses(words_data, threshold=0.5)`**: Inserts pause markers into text
- **`map_band_to_cefr(band_score)`**: Converts IELTS band to CEFR level
- **`score_speaking_test(...)`**: Main GPT-4 scoring function with IELTS rubric

#### Voice Functions
- **`transcribe_audio(audio_file, include_timestamps=False)`**: Whisper transcription with optional word-level timestamps
- **`store_voice_timing_data(part, question, answer, timing_result)`**: Stores timing metrics for each voice response
- **`text_to_speech(text)`**: OpenAI TTS to generate audio from text

#### UI Functions
- **`load_css()`**: Reads style.css and injects custom CSS into Streamlit

### 4. Onboarding Component
- **Location:** `elif st.session_state.step == "ONBOARDING"` block
- **Structure:** Three nested `if/elif` statements checking `onboarding_step`
- **Features:**
  - Sequential message display
  - Continue buttons for progression
  - Consent with go-back option (two-column layout)

### 5. Part 1 Interview Component
- **Location:** `elif st.session_state.step == "PART_1"` block
- **Display logic:**
  - Check for completion message first
  - Show acknowledgment + question concatenated together
  - Display topic header
  - Form for user input
- **Answer processing:**
  1. Check word count (≤ 65)
  2. Check relevance with GPT
  3. If relevant: store answer, reset redirect count, generate acknowledgment, increment question count, check if need new question or topic transition
  4. If irrelevant & first time: generate redirect, increment redirect count
  5. If irrelevant & second time: move on, increment question count
- **Features:**
  - Strict question/topic counts enforced
  - Build-off logic for questions 1-2
  - Redirect system with relevance checking
  - Conversation history tracking

### 6. Part 2 Long Turn Component
- **Location:** `elif st.session_state.step == "PART_2"` block
- **Phases:**
  1. **Preparation:** Countdown timer (60s) with skip button
  2. **Long response:** Text area for main answer, relevance checking, redirect logic
  3. **Rounding-off questions:** 2 follow-up questions with acknowledgments and redirects
  4. **Completion:** Fixed message and continue button
- **Features:**
  - Dynamic prompt card generation
  - Soft minimum (50 words) with warning
  - Hard maximum (400 words)
  - Redirect system for long response and rounding-off questions
  - Strict count of 2 rounding-off questions

### 7. Part 3 Discussion Component
- **Location:** `elif st.session_state.step == "PART_3"` block
- **Flow:**
  1. Extract theme from Part 2
  2. Generate and ask 3 main questions
  3. For each main question, apply adaptive follow-up logic (1-2 follow-ups)
  4. Apply redirect system
  5. Display completion message
- **Features:**
  - Theme extraction and display
  - Adaptive follow-ups based on word count
  - Build-off logic (all questions)
  - Redirect system with reset between questions
  - 150 word limit

### 8. Scoring/Results Component
- **Location:** `elif st.session_state.step == "SCORING"` block
- **Score Calculation (runs once on first render):**
  1. Gather all conversation histories and voice timing data
  2. Call `generate_metrics_summary()` to get objective metrics
  3. Call `score_speaking_test()` to get GPT-4 assessment
  4. Cache result in `st.session_state.calculated_scores`
- **Display Sections:**
  1. **Full Conversation History** (expandable)
     - All 3 parts displayed with examiner/candidate labels
     - Plain text format (no pause markers shown to user)
  2. **Overall Band Score**
     - Large, prominent display of final band (1-9)
     - CEFR level mapping (A1-C2)
     - Overall feedback summary
  3. **Detailed Criterion Breakdown** (expandable sections)
     - Each of 5 criteria shown with band score, weight, justification
     - Color-coded: Green (7+), Yellow (5-6.9), Red (<5)
     - Additional details: Notable vocabulary, complex structures, cohesive devices
     - Task Achievement shows penalty breakdown
  4. **Strengths & Areas for Improvement**
     - Two-column layout
     - Bullet points from GPT analysis
     - Actionable feedback
  5. **CEFR Levels Explanation**
     - A1-C2 descriptions
     - General improvement tips
     - External resources
     - Retake button (resets all state)

### 9. Debug Controls
- **Location:** Expandable section at top of `main()`
- **Features:**
  - 4 skip buttons (Part 1, Part 2, Part 3, Results)
  - Properly initializes/resets state when skipping

### 5. Part 2: The Long Turn (Text Mode)
- **Prompt card generation:**
  - GPT generates a prompt card with 8 possible topics (person, place, object, event, activity, media, decision, journey)
  - Card includes main prompt and 3-4 bullet point assistive questions
  - User sees the card and has 5 seconds prep time (for testing; normally 1 minute)
- **Long response:**
  - User writes response (400 word max, 50 word soft minimum)
  - System checks relevance and applies redirect logic
  - If < 50 words, prompts for expansion (without clearing text box)
- **Rounding-off questions:**
  - Exactly 2 follow-up questions related to the long response
  - 65 word limit per answer
  - Redirect logic applies (two-strike policy)
- **Completion:**
  - Fixed transition message displayed
  - "Continue to Part 3" button

### 6. Part 3: The Discussion (Text Mode)
- **Theme extraction:**
  - GPT extracts 2-4 word theme from Part 2's main prompt
  - Questions explore abstract concepts related to this theme
- **Main questions:**
  - Exactly 3 main questions asked
  - Questions build off user's previous relevant responses
  - Questions are simple, conversational, and less advanced
- **Adaptive follow-up logic:**
  - First answer to main question: Always asks follow-up #1
  - After follow-up #1:
    - If first answer ≥ 30 words: Move to next main question
    - If first answer < 30 words:
      - If current answer ≥ 20 words: Move to next main question
      - If current answer < 20 words: Ask follow-up #2
  - After follow-up #2: Always move to next main question
- **Redirect logic:**
  - Same two-strike policy as other parts
  - Redirects reset when moving to new questions/follow-ups
  - Redirects don't count toward follow-up limit
- **Word limit:** 150 words per response
- **Completion:**
  - After 3 main questions, displays completion message
  - "View Results" button transitions to SCORING

### 7. Results/Scoring Page
- **CEFR Level Display:**
  - Shows all CEFR levels (A1-C2) with descriptions
  - Currently displays placeholder B1 level assessment
  - Note: Future versions will analyze conversation data for accurate scoring
- **CEFR Levels Explained:**
  - A1 (Beginner): Familiar everyday expressions and basic phrases
  - A2 (Elementary): Simple routine tasks and direct information exchange
  - B1 (Intermediate): Handle travel situations, describe experiences
  - B2 (Upper Intermediate): Fluent interaction, detailed text production
  - C1 (Advanced): Fluent, spontaneous expression for all purposes
  - C2 (Proficiency): Understand virtually everything, express precisely
- **Improvement Tips:**
  - **Delivery & Fluency:** Pacing, clarity, reducing filler words, using thinking time
  - **Content & Relevance:** Stay on-topic, avoid memorized answers, use appropriate vocabulary
  - **Practice Methods:** Sample questions, daily speaking, listening/reading aloud, thinking in English, recording yourself, learning phrases, acting confident
- **External Resources:**
  - Link to GlobalExam's comprehensive IELTS Speaking guide
- **Retake Option:**
  - "Take Test Again" button resets all session state

### 8. UI/UX Enhancements
- **Custom CSS (style.css):**
  - Removed red focus borders on text inputs and text areas
  - Changed to gray borders (#d0d0d0) for better aesthetics
  - Applied using `load_css()` function that reads style.css and injects it
- **Word Limit Displays:**
  - Hard limits enforced before submission (blocks if exceeded)
  - Natural language descriptions instead of just numbers where appropriate
  - Part 1 & Part 3: "Expected length: ..." instead of "Max words: X"
- **Debug Controls (Temporary):**
  - Expandable section with 4 skip buttons
  - Skip to Part 1, Part 2, Part 3, or Results
  - Allows quick testing without going through entire flow
  - Part 1 skip initializes topics
  - Part 3 skip resets initialization flag
- **Form Handling:**
  - `st.form(clear_on_submit=True)` for Enter key submission
  - Special handling for Part 2 soft minimum (doesn't clear if < 50 words)
- **Completion Messages:**
  - Fixed messages between parts (not GPT-generated)
  - Persistent display with "Continue" buttons
  - User-controlled progression

---

## 📋 Next Steps (Implementation Roadmap)

### ✅ Phase 1: Text Mode (COMPLETED)
- [x] Part 1: Interview questions (text mode) ✅
- [x] Part 2: Long turn (text mode) ✅
- [x] Part 3: Deep dive abstract questions (text mode) ✅
- [x] Results page with CEFR levels and tips ✅
- [x] Examiner LLM prompt (for conversation) ✅

### 🎙️ Phase 2: Voice Integration (COMPLETED)
- [x] **Mode Selection Screen**
  - Users choose between Voice Mode and Text Mode before starting Part 1
  - Choice applies to all parts of the test
  - Clean UI with clear descriptions of each mode
  - Info banner: "💡 Voice Mode is recommended for the most realistic and accurate speaking assessment"
  - Voice Mode card labeled as "Recommended"
- [x] **Voice Output (TTS)**
  - Integrated OpenAI TTS API (tts-1 model with alloy voice)
  - Questions auto-play when they appear
  - "🔄 Replay Question" button for each question
  - Audio files saved to `/tmp/` directory
- [x] **Voice Input (STT)**
  - Integrated OpenAI Whisper API for transcription
  - Browser-based audio recording using `st.audio_input()`
  - Real-time transcription feedback with spinner
  - Transcribed text shown before submission (editable)
  - Dynamic audio widget keys to reset on new questions/redirects
- [x] **Hard Cutoff Timers (Voice Mode)**
  - Replaces silence detection with hard time limits
  - **Part 1:** 30 seconds displayed, 40 seconds actual (10s buffer)
  - **Part 2 Long Response:** 120 seconds displayed, 130 seconds actual (10s buffer)
  - **Part 2 Rounding:** 30 seconds displayed, 40 seconds actual (10s buffer)
  - **Part 3:** 60 seconds displayed, 70 seconds actual (10s buffer)
  - No countdown shown to user (exam-like experience)
  - Auto-skip with "Time's up!" message when time expires
  - Uses `st_autorefresh` with intervals matching actual time limits
- [x] **Text Mode (Preserved)**
  - Text input remains fully functional
  - Silence detection with check-in messages (original behavior)
  - All original timing logic preserved
  - **Part 1:** 30s check-in, 60s auto-skip
  - **Part 2 Long Response:** 60s check-in, 120s auto-skip
  - **Part 2 Rounding:** 30s check-in, 60s auto-skip
  - **Part 3:** 40s check-in, 80s auto-skip

### 📊 Phase 3: Evaluation & Scoring (COMPLETED)
- [x] **IELTS 1-9 Band Scale Scoring System**
  - 5 weighted criteria implementation
  - Fluency & Coherence (25%): WPM, pause analysis, hesitation, flow
  - Lexical Resource (20%): Vocabulary range, appropriacy, paraphrasing
  - Grammatical Range & Accuracy (20%): Structure variety, complexity attempts, error tolerance
  - Coherence & Cohesion (15%): Linking words, logical organization, idea progression
  - Task Achievement (20%): Response length, relevance, question addressing
- [x] **Metric Calculation Functions (5 functions)**
  - `calculate_response_metrics()`: Counts responses, timeouts, avg word count
  - `calculate_voice_metrics()`: WPM, pause statistics (voice mode only)
  - `calculate_part_specific_metrics()`: Per-part word counts vs ideal ranges
  - `count_timeouts_and_relevance()`: Penalty calculation from conversation patterns
  - `generate_metrics_summary()`: Master function combining all metrics
- [x] **Helper Functions (4 functions)**
  - `combine_conversation_histories()`: Merges Part 1, 2, 3 with labels
  - `format_metrics_for_prompt()`: Formats metrics dict for GPT
  - `format_full_conversation()`: Formats conversation with pause markers
  - `map_band_to_cefr()`: Converts band score (1-9) to CEFR level (A1-C2)
- [x] **GPT-4 Scoring Function**
  - `score_speaking_test()`: Main scoring function with detailed IELTS rubric
  - Comprehensive prompt with all band descriptors (9/7/5/3)
  - Structured JSON response parsing
  - Error handling with fallback scoring
  - Temperature 0.3 for consistent scoring
- [x] **Word-Level Timestamp Capture (Voice Mode)**
  - Whisper API configured: `response_format="verbose_json"`, `timestamp_granularities=["word"]`
  - Returns `{text, words: [{word, start, end}], duration}`
  - Stored in `voice_timing_data` for each response
  - `store_voice_timing_data()`: Calculates WPM, pauses, metrics
- [x] **Pause Analysis**
  - Small pauses (<0.3s): Ignored (natural breathing)
  - Medium pauses (0.3s-1.5s): Counted
  - Long pauses (>1.5s): Flagged specifically
  - Pause location markers: `[pause: X.Xs]` embedded in transcript
  - GPT can distinguish boundary pauses (good) from mid-clause pauses (concerning)
- [x] **Enhanced Results Page**
  - Overall band score display (prominent, color-coded)
  - CEFR level mapping (A1-C2)
  - Detailed criterion scores (expandable sections with justifications)
  - Notable vocabulary, complex structures, cohesive devices shown
  - Penalty breakdown for Task Achievement
  - Strengths & areas for improvement (from GPT analysis)
  - Full conversation history display
  - Score caching in session state (no re-computation)
- [x] **Penalty System**
  - Timeouts: -0.5 band score from Task Achievement each
  - Irrelevant answers: -0.5 band score from Task Achievement each
  - Applied to base Task Achievement score
  - Minimum score floor: 1.0
- [x] **Ideal Word Count Targets**
  - Part 1: 20-50 words (too short if <10)
  - Part 2 Long Response: 150+ ideal, 100+ acceptable (too short if <100)
  - Part 2 Rounding: 20-50 words (too short if <10)
  - Part 3: 50-100 words (too short if <30)
- [x] **Bug Fixes**
  - Irrelevant answers now correctly saved to conversation history (all parts, both modes)
  - Audio playback state management fixed (no overlap between questions)
  - Transcription caching (prevents re-transcription on refresh)
  - Text mode refresh logic optimized (removed race conditions)
  - Voice mode single-click submission (added missing `st.rerun()` calls)

---

## 📝 Notes

- Both **text mode** and **voice mode** are fully implemented
- Users choose their preferred mode at the start of the test (voice mode recommended)
- **OpenAI APIs used:**
  - GPT-4o-mini: Examiner role (question generation, acknowledgments, redirects)
  - GPT-4o: Scoring and assessment (detailed IELTS rubric)
  - TTS-1 (alloy voice): Question audio generation
  - Whisper: Speech-to-text with word-level timestamps
- **Scoring system:**
  - IELTS 1-9 band scale with 5 weighted criteria
  - Hybrid approach: Objective metrics + GPT-4 subjective assessment
  - Penalty system for timeouts and irrelevant answers
  - CEFR mapping (A1-C2)
- **Voice mode features:**
  - Word-level timestamp capture for pause analysis
  - Pause markers embedded in GPT assessment transcript
  - WPM calculation and fluency metrics
  - Hard time limits with 10s buffer
- **Text mode features:**
  - Silence detection with check-in messages
  - Adaptive refresh logic (no race conditions)
  - All original timing logic preserved
- Conversation history stored with all responses (including irrelevant answers)
- Topics/prompts randomly generated for variety between test sessions
- Redirect logic (two-strike policy) applies consistently across all parts
- Word limits vary by part: Part 1 (65), Part 2 long (400), Part 2 rounding (65), Part 3 (150)
- Results page shows full scoring breakdown but not detailed voice analytics (kept internal for GPT)