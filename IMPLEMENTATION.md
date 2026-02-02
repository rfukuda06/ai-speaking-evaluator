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
- **Features:**
  - CEFR levels display (A1-C2)
  - Placeholder B1 assessment
  - Improvement tips (3 categories)
  - External resource link
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

## 📋 Next Steps (Not Yet Implemented)

- [x] Part 1: Interview questions (text mode) ✅
- [x] Part 2: Long turn (text mode) ✅
- [x] Part 3: Deep dive abstract questions (text mode) ✅
- [x] Results page with CEFR levels and tips ✅
- [ ] Part 1: Add voice input (STT integration)
- [ ] Speech-to-Text (STT) integration with Deepgram for all parts
- [ ] Text-to-Speech (TTS) integration for bot responses
- [ ] Silence detection (12-second threshold)
- [x] Examiner LLM prompt (for conversation) ✅
- [ ] Grader LLM prompt (for scoring analysis)
- [ ] Scoring system (4 buckets: Fluency, Lexical/Grammar, Coherence, Effectiveness)
- [ ] Actual conversation analysis for accurate CEFR scoring
- [ ] Personalized feedback based on user performance
- [ ] Progress tracking across multiple test sessions

---

## 📝 Notes

- All parts are implemented in **text mode** (user types answers)
- Voice input/output will be added in Phase 2 of the build plan
- OpenAI GPT-4o-mini is used for the Examiner role
- Conversation history is stored for later scoring analysis
- Topics/prompts are randomly generated for variety between test sessions
- Current scoring shows placeholder B1 level; future versions will analyze actual conversation data
- Redirect logic (two-strike policy) applies consistently across all parts
- Word limits vary by part: Part 1 (65), Part 2 long (400), Part 2 rounding (65), Part 3 (150)
