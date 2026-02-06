import streamlit as st
import time
from streamlit_autorefresh import st_autorefresh

# Import from our modules
from config import client, PART1_TOPICS, PART2_CATEGORIES, RELEVANCE_THRESHOLD
from utils import load_css, format_conversation_history, reset_silence_timer, check_silence_and_update, generate_part_completion_message
from state_management import initialize_part1, initialize_part2, initialize_part3
from voice_functions import text_to_speech, transcribe_audio, store_voice_timing_data, check_voice_timer_expired
from llm_functions import (get_examiner_prompt, get_examiner_prompt_part2, get_examiner_prompt_part3,
                           get_examiner_response, check_relevance, generate_redirect_message,
                           generate_part2_prompt_card, generate_rounding_off_questions,
                           extract_theme_from_part2, generate_part3_question, generate_part3_acknowledgment)
from scoring import (generate_metrics_summary, score_speaking_test, get_cefr_description)

if 'step' not in st.session_state:
    st.session_state.step = "START"

# 'onboarding_step' tracks which onboarding message to show (0, 1, or 2)
# We need this because onboarding has 3 separate messages
if 'onboarding_step' not in st.session_state:
    st.session_state.onboarding_step = 0

# 'test_mode' tracks whether user selected 'text' or 'voice' mode
if 'test_mode' not in st.session_state:
    st.session_state.test_mode = None

# Part 1 state variables
if 'part1_initialized' not in st.session_state:
    st.session_state.part1_initialized = False
if 'part1_topics' not in st.session_state:
    st.session_state.part1_topics = []
if 'part1_current_topic_index' not in st.session_state:
    st.session_state.part1_current_topic_index = 0
if 'part1_questions_asked' not in st.session_state:
    st.session_state.part1_questions_asked = 0  # Questions asked for current topic
if 'part1_questions_per_topic' not in st.session_state:
    st.session_state.part1_questions_per_topic = []  # Target questions for each topic (2 or 3)
if 'part1_conversation_history' not in st.session_state:
    st.session_state.part1_conversation_history = []  # Store all Q&A for scoring
if 'part1_waiting_for_answer' not in st.session_state:
    st.session_state.part1_waiting_for_answer = False
if 'part1_current_question' not in st.session_state:
    st.session_state.part1_current_question = ""
if 'part1_completion_message' not in st.session_state:
    st.session_state.part1_completion_message = ""
if 'part1_showing_completion' not in st.session_state:
    st.session_state.part1_showing_completion = False
if 'part1_redirect_count' not in st.session_state:
    st.session_state.part1_redirect_count = 0
if 'part1_acknowledgment' not in st.session_state:
    st.session_state.part1_acknowledgment = ""
if 'part1_last_relevant_answer' not in st.session_state:
    st.session_state.part1_last_relevant_answer = ""
if 'part1_should_build_off' not in st.session_state:
    st.session_state.part1_should_build_off = False  # Track redirects for current question

# Part 2 state variables
if 'part2_initialized' not in st.session_state:
    st.session_state.part2_initialized = False
if 'part2_category' not in st.session_state:
    st.session_state.part2_category = ""
if 'part2_prompt_card' not in st.session_state:
    st.session_state.part2_prompt_card = {}  # Will store: main_prompt, bullet_points
if 'part2_prep_start_time' not in st.session_state:
    st.session_state.part2_prep_start_time = None
if 'part2_prep_elapsed' not in st.session_state:
    st.session_state.part2_prep_elapsed = 0
if 'part2_prep_complete' not in st.session_state:
    st.session_state.part2_prep_complete = False
if 'part2_long_response' not in st.session_state:
    st.session_state.part2_long_response = ""
if 'part2_rounding_off_questions' not in st.session_state:
    st.session_state.part2_rounding_off_questions = []
if 'part2_current_rounding_question' not in st.session_state:
    st.session_state.part2_current_rounding_question = ""
if 'part2_rounding_question_index' not in st.session_state:
    st.session_state.part2_rounding_question_index = 0
if 'part2_rounding_questions_answered' not in st.session_state:
    st.session_state.part2_rounding_questions_answered = 0  # Track total questions answered (including redirects)
if 'part2_waiting_for_rounding_answer' not in st.session_state:
    st.session_state.part2_waiting_for_rounding_answer = False
if 'part2_conversation_history' not in st.session_state:
    st.session_state.part2_conversation_history = []
if 'part2_completion_message' not in st.session_state:
    st.session_state.part2_completion_message = ""
if 'part2_showing_completion' not in st.session_state:
    st.session_state.part2_showing_completion = False
if 'part2_long_response_redirect_count' not in st.session_state:
    st.session_state.part2_long_response_redirect_count = 0  # Track redirects for long response
if 'part2_rounding_redirect_count' not in st.session_state:
    st.session_state.part2_rounding_redirect_count = 0  # Track redirects for current rounding question
if 'part2_long_response_acknowledgment' not in st.session_state:
    st.session_state.part2_long_response_acknowledgment = ""  # Store GPT's acknowledgment of long response
if 'part2_rounding_acknowledgment' not in st.session_state:
    st.session_state.part2_rounding_acknowledgment = ""  # Store GPT's acknowledgment of rounding answer
if 'part2_long_response_redirect_message' not in st.session_state:
    st.session_state.part2_long_response_redirect_message = ""  # Store redirect message for long response
if 'part2_instruction_audio_played' not in st.session_state:
    st.session_state.part2_instruction_audio_played = False  # Track if instruction audio has been played in voice mode
if 'part2_showing_intro' not in st.session_state:
    st.session_state.part2_showing_intro = False  # Track if showing intro page (voice mode only)
if 'part2_intro_start_time' not in st.session_state:
    st.session_state.part2_intro_start_time = None  # Track when intro started for auto-transition

# Part 3 state variables
if 'part3_initialized' not in st.session_state:
    st.session_state.part3_initialized = False
if 'part3_theme' not in st.session_state:
    st.session_state.part3_theme = ""
if 'part3_questions_asked' not in st.session_state:
    st.session_state.part3_questions_asked = 0  # Count of main questions (max 3)
if 'part3_followups_asked' not in st.session_state:
    st.session_state.part3_followups_asked = 0  # Count of follow-ups for current main question (0-2)
if 'part3_first_answer_word_count' not in st.session_state:
    st.session_state.part3_first_answer_word_count = 0  # Word count of first answer to current main question
if 'part3_conversation_history' not in st.session_state:
    st.session_state.part3_conversation_history = []
if 'part3_current_question' not in st.session_state:
    st.session_state.part3_current_question = ""
if 'part3_waiting_for_answer' not in st.session_state:
    st.session_state.part3_waiting_for_answer = False
if 'part3_redirect_count' not in st.session_state:
    st.session_state.part3_redirect_count = 0
if 'part3_acknowledgment' not in st.session_state:
    st.session_state.part3_acknowledgment = ""
if 'part3_completion_message' not in st.session_state:
    st.session_state.part3_completion_message = ""
if 'part3_showing_completion' not in st.session_state:
    st.session_state.part3_showing_completion = False

# ===== SILENCE DETECTION STATE VARIABLES =====
# Part 1 silence detection (for text mode)
if 'part1_question_start_time' not in st.session_state:
    st.session_state.part1_question_start_time = None
if 'part1_check_in_shown' not in st.session_state:
    st.session_state.part1_check_in_shown = False
if 'part1_check_in_message' not in st.session_state:
    st.session_state.part1_check_in_message = ""

# Part 1 voice mode timer
if 'part1_voice_timer_start' not in st.session_state:
    st.session_state.part1_voice_timer_start = None
if 'part1_voice_audio_data' not in st.session_state:
    st.session_state.part1_voice_audio_data = None  # Store generated TTS audio

# Voice mode timing data (for all parts)
if 'voice_timing_data' not in st.session_state:
    st.session_state.voice_timing_data = []  # List of timing info for each voice response

# Part 2 long response silence detection (for text mode)
if 'part2_long_question_start_time' not in st.session_state:
    st.session_state.part2_long_question_start_time = None
if 'part2_long_check_in_shown' not in st.session_state:
    st.session_state.part2_long_check_in_shown = False
if 'part2_long_check_in_message' not in st.session_state:
    st.session_state.part2_long_check_in_message = ""

# Part 2 rounding-off silence detection (for text mode)
if 'part2_rounding_question_start_time' not in st.session_state:
    st.session_state.part2_rounding_question_start_time = None
if 'part2_rounding_check_in_shown' not in st.session_state:
    st.session_state.part2_rounding_check_in_shown = False
if 'part2_rounding_check_in_message' not in st.session_state:
    st.session_state.part2_rounding_check_in_message = ""

# Part 2 voice mode timer
if 'part2_voice_timer_start' not in st.session_state:
    st.session_state.part2_voice_timer_start = None
if 'part2_voice_audio_data' not in st.session_state:
    st.session_state.part2_voice_audio_data = None  # Store generated TTS audio
if 'part2_rounding_voice_timer_start' not in st.session_state:
    st.session_state.part2_rounding_voice_timer_start = None
if 'part2_rounding_voice_audio_data' not in st.session_state:
    st.session_state.part2_rounding_voice_audio_data = None

# Part 3 silence detection (for text mode)
if 'part3_question_start_time' not in st.session_state:
    st.session_state.part3_question_start_time = None
if 'part3_check_in_shown' not in st.session_state:
    st.session_state.part3_check_in_shown = False
if 'part3_check_in_message' not in st.session_state:
    st.session_state.part3_check_in_message = ""

# Part 3 voice mode timer
if 'part3_voice_timer_start' not in st.session_state:
    st.session_state.part3_voice_timer_start = None
if 'part3_voice_audio_data' not in st.session_state:
    st.session_state.part3_voice_audio_data = None  # Store generated TTS audio
if 'part3_audio_played_key' not in st.session_state:
    st.session_state.part3_audio_played_key = None  # Track which question's audio has been played
if 'part3_transcribed_answer' not in st.session_state:
    st.session_state.part3_transcribed_answer = None  # Store transcribed answer to prevent retranscription
def main():
    # Load custom CSS styles
    load_css()
    
    st.title("AI English Speaking Evaluator")
    
    # Demo Shortcuts - Collapsed by default
    with st.expander("Demo Shortcuts", expanded=False):
        st.caption("Use these controls to navigate between sections during development and demonstration.")
        st.write("")
        
        # Mode switcher - always visible
        current_mode = st.session_state.get('test_mode')
        if current_mode:
            st.write(f"**Test Mode:** {current_mode.title()}")
        else:
            st.write("**Test Mode:** Not selected (defaults to Voice)")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            if st.button("Voice Mode", key="nav_voice", use_container_width=True):
                st.session_state.test_mode = 'voice'
                st.rerun()
        with col_m2:
            if st.button("Text Mode", key="nav_text", use_container_width=True):
                st.session_state.test_mode = 'text'
                st.rerun()
        
        st.write("")
        st.write("---")
        st.write("**Jump to Section:**")
        st.write("")
        
        # Navigation buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Part 1", key="nav_part1", use_container_width=True):
                # Set voice mode as default if not set
                if not st.session_state.get('test_mode'):
                    st.session_state.test_mode = 'voice'
                st.session_state.step = "PART_1"
                initialize_part1()
                st.rerun()
        
        with col2:
            if st.button("Part 2", key="nav_part2", use_container_width=True):
                # Set voice mode as default if not set
                if not st.session_state.get('test_mode'):
                    st.session_state.test_mode = 'voice'
                st.session_state.step = "PART_2"
                st.rerun()
        
        with col3:
            if st.button("Part 3", key="nav_part3", use_container_width=True):
                # Set voice mode as default if not set
                if not st.session_state.get('test_mode'):
                    st.session_state.test_mode = 'voice'
                st.session_state.step = "PART_3"
                st.session_state.part3_initialized = False
                st.rerun()
        
        with col4:
            if st.button("Results", key="nav_results", use_container_width=True):
                # Set voice mode as default if not set
                if not st.session_state.get('test_mode'):
                    st.session_state.test_mode = 'voice'
                st.session_state.step = "SCORING"
                st.rerun()

    if st.session_state.step == "START":
        st.write("Hello! Ready to start your English test?")
        if st.button("Begin"):
            # When user clicks Begin, move to ONBOARDING (not directly to PART_1)
            st.session_state.step = "ONBOARDING"
            st.session_state.onboarding_step = 0  # Start at the first onboarding message
            st.rerun()  # Refresh the page to show the new state

    elif st.session_state.step == "ONBOARDING":
        # This is the onboarding flow with 3 messages shown one at a time
        # onboarding_step 0 = Introduction
        # onboarding_step 1 = Structure explanation
        # onboarding_step 2 = Consent question
        
        if st.session_state.onboarding_step == 0:
            # Message 1: Introduction
            st.write("### Introduction")
            st.write("Hello, I'm your Speaking Assistant. My goal is to estimate your English level through a short conversation.")
            if st.button("Continue"):
                st.session_state.onboarding_step = 1  # Move to next message
                st.rerun()
        
        elif st.session_state.onboarding_step == 1:
            # Message 2: Structure explanation
            st.write("### Test Structure")
            st.write("We will do three parts: a short interview, a 2-minute story, and a deeper discussion. The whole process takes about 11–14 minutes.")
            if st.button("Continue"):
                st.session_state.onboarding_step = 2  # Move to consent
                st.rerun()
        
        elif st.session_state.onboarding_step == 2:
            # Message 3: Consent
            st.write("### Consent")
            st.write("I will record your responses to analyze your fluency and vocabulary. Are you ready to begin?")
            # Two buttons: one to consent, one to go back
            col1, col2 = st.columns(2)  # Create two side-by-side buttons
            with col1:
                if st.button("Yes, I'm ready"):
                    # User consented, move to mode selection
                    st.session_state.step = "MODE_SELECTION"
                    st.rerun()
            with col2:
                if st.button("Go back"):
                    # User wants to go back, return to START
                    st.session_state.step = "START"
                    st.session_state.onboarding_step = 0
                    st.rerun()

    elif st.session_state.step == "MODE_SELECTION":
        # Voice mode as primary option
        st.write("### Ready to Begin Your Speaking Test")
        st.write("")
        st.write("Speak your answers naturally using your microphone for the most realistic IELTS experience.")
        st.write("")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.write("**Why Voice Mode?**")
            st.write("• Tests your actual speaking ability")
            st.write("• Natural conversation flow")
            st.write("• Authentic IELTS-style assessment")
            st.write("• More accurate fluency and pronunciation analysis")
            st.write("")
            st.write("")
            if st.button("Start Test with Voice Mode", use_container_width=True, type="primary"):
                st.session_state.test_mode = 'voice'
                st.session_state.step = "PART_1"
                st.rerun()
        
        st.write("")
        st.write("")
        st.write("---")
        
        # Small text mode alternative at the bottom
        with st.expander("Alternative: Text Mode (if microphone is unavailable)", expanded=False):
            st.caption("Use this option only if you cannot use a microphone or are in a location where speaking aloud is not possible.")
            st.write("")
            st.write("**Note:** Text mode provides a simplified assessment and may not reflect your true speaking ability.")
            st.write("")
            if st.button("Continue with Text Mode", use_container_width=True):
                st.session_state.test_mode = 'text'
                st.session_state.step = "PART_1"
                st.rerun()

    elif st.session_state.step == "PART_1":
        # Initialize Part 1 when we first enter
        initialize_part1()
        
        # Show completion message if Part 1 is done (check this FIRST before showing questions/input)
        if st.session_state.part1_showing_completion and st.session_state.part1_completion_message:
            st.write("### Part 1: The Interview")
            st.write("---")
            st.write(f"**Examiner:** {st.session_state.part1_completion_message}")
            st.write("")
            if st.button("Continue to Part 2", key="part1_continue_button"):
                st.session_state.step = "PART_2"
                st.rerun()
        else:
            st.write("### Part 1: The Interview")
            st.write("I'll ask you some questions about different topics. Plese respond with brief, conversational responses.")
            
            # Show current topic
            if st.session_state.part1_current_topic_index < len(st.session_state.part1_topics):
                current_topic = st.session_state.part1_topics[st.session_state.part1_current_topic_index]
                st.info(f"**Current Topic:** {current_topic}")
            
            # If we haven't asked the first question yet, or we're ready for a new question
            if not st.session_state.part1_waiting_for_answer and st.session_state.part1_current_question == "":
                # FIRST: Check if we've already asked target number of questions for this topic
                target_questions = st.session_state.part1_questions_per_topic[st.session_state.part1_current_topic_index]
                if st.session_state.part1_questions_asked >= target_questions:
                    # We've completed this topic - move to next topic
                    st.session_state.part1_current_topic_index += 1
                    st.session_state.part1_questions_asked = 0
                    st.session_state.part1_redirect_count = 0
                    st.session_state.part1_should_build_off = False  # Reset for new topic
                    st.session_state.part1_last_relevant_answer = ""  # Clear for new topic
                    
                    # Check if we've finished all topics
                    if st.session_state.part1_current_topic_index >= len(st.session_state.part1_topics):
                        # Part 1 is complete
                        completion_message = generate_part_completion_message(1, st.session_state.part1_conversation_history)
                        st.session_state.part1_completion_message = completion_message
                        st.session_state.part1_showing_completion = True
                        
                        st.session_state.part1_conversation_history.append({
                            'role': 'examiner',
                            'content': completion_message
                        })
                        st.rerun()
                    else:
                        # Continue to next topic
                        st.rerun()
                else:
                    # Get the first question or next question from GPT
                    with st.spinner("Thinking of a question..."):
                        # Create prompt specifically for asking a question
                        current_topic = st.session_state.part1_topics[st.session_state.part1_current_topic_index]
                        
                        # Check if we should build off the previous answer
                        if st.session_state.part1_should_build_off and st.session_state.part1_last_relevant_answer:
                            # Build a follow-up question based on their previous answer
                            system_prompt = f"""You are a friendly English speaking test examiner conducting Part 1 of an IELTS-style speaking test.

Current topic: {current_topic}
You have asked {st.session_state.part1_questions_asked} question(s) about this topic so far.

The candidate just answered: "{st.session_state.part1_last_relevant_answer}"

Your task: Ask a natural follow-up question that builds off what they just said. Pick up on something specific they mentioned and ask them to elaborate or share more about it.

Guidelines:
- Keep it conversational and natural
- Reference something specific from their answer
- Stay on the topic of {current_topic}
- Keep it simple (this is Part 1 - warm-up)
- ONLY ask ONE question

Previous conversation:
{format_conversation_history(st.session_state.part1_conversation_history[-6:])}

Now, ask your follow-up question."""
                        else:
                            # Ask a fresh question about the topic
                            system_prompt = f"""You are a friendly English speaking test examiner conducting Part 1 of an IELTS-style speaking test.

Current topic: {current_topic}
You have asked {st.session_state.part1_questions_asked} question(s) about this topic so far.

Your task: Ask a simple, conversational question about {current_topic}.

Guidelines:
- Keep questions simple and natural (this is Part 1 - warm-up)
- If this is the first question about this topic, introduce it naturally (e.g., "Let's talk about {current_topic}")
- Make it relevant to everyday life
- Be encouraging and friendly
- ONLY ask ONE question - do not include acknowledgments or multiple questions

Previous conversation:
{format_conversation_history(st.session_state.part1_conversation_history)}

Now, ask your question."""
                        
                        examiner_response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": "Please ask me a question."}
                            ],
                            temperature=0.7,
                            max_tokens=100
                        ).choices[0].message.content
                        st.session_state.part1_current_question = examiner_response
                        
                        # Add examiner's question to history
                        st.session_state.part1_conversation_history.append({
                            'role': 'examiner',
                            'content': examiner_response
                        })
                        
                        st.session_state.part1_waiting_for_answer = True
                        st.session_state.part1_questions_asked += 1
                        st.session_state.part1_redirect_count = 0  # Reset redirect count for new question
                        reset_silence_timer("part1")  # Reset timer for new question
                        st.session_state.part1_voice_audio_data = None  # Clear audio data for new question
                        st.rerun()
            
            # ===== MODE-SPECIFIC INPUT/OUTPUT HANDLING =====
            
            if st.session_state.test_mode == 'text':
                # ===== TEXT MODE =====
                # Display the current question (with acknowledgment if available)
                if st.session_state.part1_current_question:
                    # If there's an acknowledgment, show it first, then the question
                    if st.session_state.part1_acknowledgment:
                        combined_response = st.session_state.part1_acknowledgment + " " + st.session_state.part1_current_question
                        st.write("**Examiner:** " + combined_response)
                    else:
                        st.write("**Examiner:** " + st.session_state.part1_current_question)
                
                # Silence detection for text mode
                if st.session_state.part1_waiting_for_answer and st.session_state.part1_current_question:
                    silence_status = check_silence_and_update("part1", 30)  # 30s check-in, 60s auto-skip
                    
                    # Show check-in message if threshold reached
                    if silence_status['show_check_in'] and st.session_state.part1_check_in_message:
                        st.info(f"{st.session_state.part1_check_in_message}")
                    
                    # Handle auto-skip if timeout reached
                    if silence_status['should_skip']:
                        # Store "No response" in conversation history
                        st.session_state.part1_conversation_history.append({
                            'role': 'candidate',
                            'content': '[No response - timed out]'
                        })
                        # Move to next question - clear state properly
                        st.session_state.part1_waiting_for_answer = False
                        st.session_state.part1_current_question = ""
                        st.session_state.part1_acknowledgment = ""
                        st.session_state.part1_redirect_count = 0
                        st.session_state.part1_should_build_off = False
                        st.session_state.part1_last_relevant_answer = ""
                        st.session_state.part1_voice_audio_data = None  # Clear audio data
                        reset_silence_timer("part1")
                        st.rerun()
                
                # Text input for user's answer
                if st.session_state.part1_waiting_for_answer:
                    # Use st.form() so Enter key will submit the form
                    with st.form(key="answer_form", clear_on_submit=True):
                        st.caption("Max words: 65")
                        user_answer = st.text_input("Your answer:", key="part1_answer_input")
                        form_submitted = st.form_submit_button("Submit Answer")
                    
                    # Check if form was submitted (either by button click or Enter key)
                    if form_submitted:
                        if user_answer.strip():
                            # Check word count limit
                            word_count = len(user_answer.split())
                            if word_count > 65:
                                st.error(f"Your answer is {word_count} words. Please reduce it to 65 words or less.")
                                st.rerun()
                            
                            # ALWAYS check relevance first
                            context = format_conversation_history(st.session_state.part1_conversation_history[-4:])
                            is_relevant, relevance_score = check_relevance(
                                user_answer,
                                st.session_state.part1_current_question,
                                context
                            )
                            
                            # If answer is relevant, process normally (regardless of redirect count)
                            if is_relevant or relevance_score >= 0.7:
                                # Response is relevant - process normally
                                # Add user's answer to history
                                st.session_state.part1_conversation_history.append({
                                    'role': 'user',
                                    'content': user_answer
                                })
                                
                                # Reset redirect count since answer is relevant
                                st.session_state.part1_redirect_count = 0
                                
                                # Store this answer to build off for next question (if not the last question)
                                target_questions = st.session_state.part1_questions_per_topic[st.session_state.part1_current_topic_index]
                                if st.session_state.part1_questions_asked < target_questions:
                                    st.session_state.part1_last_relevant_answer = user_answer
                                    st.session_state.part1_should_build_off = True
                                else:
                                    # This is the last question for this topic, don't build off
                                    st.session_state.part1_should_build_off = False
                                    st.session_state.part1_last_relevant_answer = ""
                                
                                # Get GPT's acknowledgment
                                with st.spinner("Processing..."):
                                    # Create prompt specifically for acknowledging an answer
                                    current_topic = st.session_state.part1_topics[st.session_state.part1_current_topic_index]
                                    system_prompt = f"""You are a friendly English speaking test examiner conducting Part 1 of an IELTS-style speaking test.

Current topic: {current_topic}

Your task: Give a brief, natural acknowledgment of the user's last answer.

Guidelines:
- Keep it SHORT (1-2 sentences max)
- Be encouraging and friendly
- DO NOT ask any questions
- DO NOT mention moving to other topics
- Just acknowledge what they said naturally

Previous conversation:
{format_conversation_history(st.session_state.part1_conversation_history)}

Now, give a brief acknowledgment."""
                                    
                                    examiner_response = client.chat.completions.create(
                                        model="gpt-4o-mini",
                                        messages=[
                                            {"role": "system", "content": system_prompt},
                                            {"role": "user", "content": "Please acknowledge my answer."}
                                        ],
                                        temperature=0.7,
                                        max_tokens=50
                                    ).choices[0].message.content
                                    
                                    # Add examiner's acknowledgment to history
                                    st.session_state.part1_conversation_history.append({
                                        'role': 'examiner',
                                        'content': examiner_response
                                    })
                                    
                                    # Store acknowledgment to display on next render
                                    st.session_state.part1_acknowledgment = examiner_response
                                    
                                    # Reset question state to prepare for next question
                                    st.session_state.part1_current_question = ""
                                    st.session_state.part1_waiting_for_answer = False
                                    st.session_state.part1_voice_audio_data = None  # Clear audio data
                                    reset_silence_timer("part1")  # Reset timer after answer
                                    st.rerun()
                            # If not relevant and we've already redirected once, accept and move on
                            elif st.session_state.part1_redirect_count >= 1:
                                # Already redirected once - move on
                                st.session_state.part1_conversation_history.append({
                                    'role': 'user',
                                    'content': user_answer
                                })
                                
                                # Add thank you message
                                st.session_state.part1_conversation_history.append({
                                    'role': 'examiner',
                                    'content': "Thank you. Let's move on."
                                })
                                
                                # Reset redirect count and move to next question
                                st.session_state.part1_redirect_count = 0
                                st.session_state.part1_current_question = ""
                                st.session_state.part1_acknowledgment = ""  # FIX: Clear acknowledgment when moving on
                                st.session_state.part1_waiting_for_answer = False
                                # Don't build off this answer since it was irrelevant
                                st.session_state.part1_should_build_off = False
                                st.session_state.part1_last_relevant_answer = ""
                                st.session_state.part1_voice_audio_data = None  # Clear audio data
                                reset_silence_timer("part1")  # Reset timer after moving on
                                st.rerun()
                            # If not relevant and first try, send redirect
                            else:
                                # First redirect - send polite nudge
                                # First, add the user's irrelevant answer to history
                                st.session_state.part1_conversation_history.append({
                                    'role': 'user',
                                    'content': user_answer
                                })
                                
                                redirect_message = generate_redirect_message(st.session_state.part1_current_question)
                                st.session_state.part1_redirect_count = 1
                                
                                # Add redirect to history
                                st.session_state.part1_conversation_history.append({
                                    'role': 'examiner',
                                    'content': redirect_message
                                })
                                
                                # Show redirect message - CLEAR acknowledgment so it doesn't concatenate
                                st.session_state.part1_acknowledgment = ""  # FIX: Clear old acknowledgment
                                st.session_state.part1_current_question = redirect_message
                                st.session_state.part1_waiting_for_answer = True
                                reset_silence_timer("part1")  # Reset timer for redirect question
                                st.rerun()
            
            elif st.session_state.test_mode == 'voice':
                # ===== VOICE MODE =====
                # Audio only (no question text in voice mode)
                if st.session_state.part1_current_question:
                    # Determine what to speak (acknowledgment + question if both exist)
                    question_to_speak = st.session_state.part1_current_question
                    if st.session_state.part1_acknowledgment:
                        question_to_speak = st.session_state.part1_acknowledgment + " " + st.session_state.part1_current_question
                    
                    # Generate TTS audio if not already generated for this question
                    if st.session_state.part1_voice_audio_data is None:
                        with st.spinner("Generating audio..."):
                            st.session_state.part1_voice_audio_data = text_to_speech(question_to_speak)
                    
                    # Auto-play the audio (no text display - audio only)
                    if st.session_state.part1_voice_audio_data:
                        st.audio(st.session_state.part1_voice_audio_data, format="audio/mp3", autoplay=True)
                        st.caption("Audio: Question")
                        
                
                # Voice input for user's answer
                if st.session_state.part1_waiting_for_answer:
                    st.write("")
                    st.write("**Time Limit: 30 seconds**")
                    
                    # Check voice timer (actual limit: 40 seconds, but we tell them 30)
                    if st.session_state.part1_voice_timer_start is not None:
                        expired, elapsed, remaining = check_voice_timer_expired(
                            st.session_state.part1_voice_timer_start, 
                            40  # Actual time limit (10s buffer)
                        )
                        
                        # Auto-skip if expired (no countdown shown)
                        if expired:
                            st.warning("Time's up! Moving to next question...")
                            # Store "No response" in conversation history
                            st.session_state.part1_conversation_history.append({
                                'role': 'candidate',
                                'content': '[No response - timed out]'
                            })
                            # Move to next question
                            st.session_state.part1_waiting_for_answer = False
                            st.session_state.part1_current_question = ""
                            st.session_state.part1_acknowledgment = ""
                            st.session_state.part1_redirect_count = 0
                            st.session_state.part1_should_build_off = False
                            st.session_state.part1_last_relevant_answer = ""
                            st.session_state.part1_voice_timer_start = None
                            st.session_state.part1_voice_audio_data = None
                            time.sleep(1)
                            st.rerun()
                    
                    # Audio recording widget - use unique key based on question number to reset widget
                    question_key = f"part1_t{st.session_state.part1_current_topic_index}_q{st.session_state.part1_questions_asked}_r{st.session_state.part1_redirect_count}"
                    audio_input = st.audio_input("Record your answer", key=question_key)
                    
                    # Start timer when audio widget appears
                    if st.session_state.part1_voice_timer_start is None:
                        st.session_state.part1_voice_timer_start = time.time()
                    
                    # Process audio when user stops recording
                    if audio_input is not None:
                        # Transcribe the audio with timestamps
                        with st.spinner("Transcribing your answer..."):
                            result = transcribe_audio(audio_input, include_timestamps=True)
                            user_answer = result['text'] if isinstance(result, dict) else result
                        
                        if user_answer:
                            # Show simple confirmation (no transcription text - more realistic)
                            st.success("Answer transcribed successfully")
                            
                            # Submit button - use unique key to avoid conflicts
                            if st.button("Submit Answer", key=f"{question_key}_submit"):
                                # Check word count limit
                                word_count = len(user_answer.split())
                                if word_count > 65:
                                    st.error(f"Your answer is {word_count} words. Please record again with 65 words or less.")
                                    st.rerun()
                                
                                # Check relevance
                                context = format_conversation_history(st.session_state.part1_conversation_history[-4:])
                                is_relevant, relevance_score = check_relevance(
                                    user_answer,
                                    st.session_state.part1_current_question,
                                    context
                                )
                                
                                # If answer is relevant, process normally
                                if is_relevant or relevance_score >= 0.7:
                                    # Response is relevant
                                    st.session_state.part1_conversation_history.append({
                                        'role': 'user',
                                        'content': user_answer
                                    })
                                    
                                    # Store timing data
                                    store_voice_timing_data('Part 1', st.session_state.part1_current_question, user_answer, result)
                                    
                                    st.session_state.part1_redirect_count = 0
                                    
                                    # Store answer for build-off logic (if not the last question)
                                    target_questions = st.session_state.part1_questions_per_topic[st.session_state.part1_current_topic_index]
                                    if st.session_state.part1_questions_asked < target_questions:
                                        st.session_state.part1_last_relevant_answer = user_answer
                                        st.session_state.part1_should_build_off = True
                                    else:
                                        st.session_state.part1_should_build_off = False
                                        st.session_state.part1_last_relevant_answer = ""
                                    
                                    # Get GPT's acknowledgment
                                    with st.spinner("Processing..."):
                                        current_topic = st.session_state.part1_topics[st.session_state.part1_current_topic_index]
                                        system_prompt = f"""You are a friendly English speaking test examiner conducting Part 1 of an IELTS-style speaking test.

Current topic: {current_topic}

Your task: Give a brief, natural acknowledgment of the user's last answer.

Guidelines:
- Keep it SHORT (1-2 sentences max)
- Be encouraging and friendly
- DO NOT ask any questions
- DO NOT mention moving to other topics
- Just acknowledge what they said naturally

Previous conversation:
{format_conversation_history(st.session_state.part1_conversation_history)}

Now, give a brief acknowledgment."""
                                        
                                        examiner_response = client.chat.completions.create(
                                            model="gpt-4o-mini",
                                            messages=[
                                                {"role": "system", "content": system_prompt},
                                                {"role": "user", "content": "Please acknowledge my answer."}
                                            ],
                                            temperature=0.7,
                                            max_tokens=50
                                        ).choices[0].message.content
                                        
                                        st.session_state.part1_conversation_history.append({
                                            'role': 'examiner',
                                            'content': examiner_response
                                        })
                                        
                                        st.session_state.part1_acknowledgment = examiner_response
                                        st.session_state.part1_current_question = ""
                                        st.session_state.part1_waiting_for_answer = False
                                        st.session_state.part1_voice_timer_start = None
                                        st.session_state.part1_voice_audio_data = None
                                        st.rerun()
                                
                                # If not relevant and already redirected, move on
                                elif st.session_state.part1_redirect_count >= 1:
                                    st.session_state.part1_conversation_history.append({
                                        'role': 'user',
                                        'content': user_answer
                                    })
                                    
                                    # Store timing data (even for irrelevant answers)
                                    store_voice_timing_data('Part 1', st.session_state.part1_current_question, user_answer, result)
                                    
                                    st.session_state.part1_conversation_history.append({
                                        'role': 'examiner',
                                        'content': "Thank you. Let's move on."
                                    })
                                    
                                    st.session_state.part1_redirect_count = 0
                                    st.session_state.part1_current_question = ""
                                    st.session_state.part1_acknowledgment = ""
                                    st.session_state.part1_waiting_for_answer = False
                                    st.session_state.part1_should_build_off = False
                                    st.session_state.part1_last_relevant_answer = ""
                                    st.session_state.part1_voice_timer_start = None
                                    st.session_state.part1_voice_audio_data = None
                                    st.rerun()
                                
                                # First redirect
                                else:
                                    # First, add the user's irrelevant answer to history
                                    st.session_state.part1_conversation_history.append({
                                        'role': 'user',
                                        'content': user_answer
                                    })
                                    
                                    # Store timing data (even for irrelevant first answer)
                                    store_voice_timing_data('Part 1 (Irrelevant)', st.session_state.part1_current_question, user_answer, result)
                                    
                                    redirect_message = generate_redirect_message(st.session_state.part1_current_question)
                                    st.session_state.part1_redirect_count = 1
                                    
                                    st.session_state.part1_conversation_history.append({
                                        'role': 'examiner',
                                        'content': redirect_message
                                    })
                                    
                                    st.session_state.part1_acknowledgment = ""
                                    st.session_state.part1_current_question = redirect_message
                                    st.session_state.part1_waiting_for_answer = True
                                    st.session_state.part1_voice_timer_start = None
                                    st.session_state.part1_voice_audio_data = None
                                    st.rerun()
                    
                    # Auto-refresh after 40 seconds to check for timeout
                    if st.session_state.part1_voice_timer_start is not None and audio_input is None:
                        st_autorefresh(interval=40000, key="part1_voice_timer")
    
    elif st.session_state.step == "PART_2":
        # Initialize Part 2 when we first enter
        initialize_part2()
        
        # Voice mode: Show intro page first, then transition to main content
        if st.session_state.test_mode == 'voice' and st.session_state.part2_showing_intro:
            st.write("### Part 2: The Long Turn")
            st.write("")
            st.write("")
            
            # Generate and play instruction audio (only once)
            if not st.session_state.part2_instruction_audio_played:
                instruction_text = "In this part, you'll speak for 1 to 2 minutes about a topic. You'll have 60 seconds to prepare."
                instruction_audio = text_to_speech(instruction_text)
                if instruction_audio:
                    st.audio(instruction_audio, format="audio/mp3", autoplay=True)
                    st.caption("Audio: Instructions")
                    st.session_state.part2_instruction_audio_played = True
            
            # Check if intro time is up (6 seconds to allow 5-second audio to play)
            if st.session_state.part2_intro_start_time:
                elapsed = time.time() - st.session_state.part2_intro_start_time
                if elapsed >= 6:
                    # Transition to main Part 2 content
                    st.session_state.part2_showing_intro = False
                    st.session_state.part2_prep_start_time = time.time()
                    st.rerun()
                else:
                    # Refresh after 7 seconds (once) to allow audio to play uninterrupted
                    st_autorefresh(interval=7000, limit=2, key="part2_intro_check")
        
        # Main Part 2 content (text mode or voice mode after intro)
        elif not st.session_state.part2_showing_intro:
            st.write("### Part 2: The Long Turn")
            
            # Instructions: only show for text mode (voice mode already played audio)
            if st.session_state.test_mode == 'text':
                st.write("In this part, you'll speak for 1-2 minutes about a topic. You'll have 60 seconds to prepare.")
            
            # Show prompt card (both text and voice modes)
            if st.session_state.part2_prompt_card:
                st.write("---")
                st.write("### Your Prompt Card")
                st.write(f"**{st.session_state.part2_prompt_card.get('main_prompt', '')}**")
                st.write("")
                st.write("You should say:")
                for bullet in st.session_state.part2_prompt_card.get('bullet_points', []):
                    st.write(f"• {bullet}")
                st.write("")
                st.write("*You will have to talk about the topic for 1 to 2 minutes. You have 60 seconds to think about what you're going to say. You can make some notes to help you if you wish.*")
                st.write("---")
            
            # Preparation phase (60 seconds) - smooth countdown (1 second updates)
            if not st.session_state.part2_prep_complete:
                # Calculate elapsed time
                if st.session_state.part2_prep_start_time:
                    elapsed = int(time.time() - st.session_state.part2_prep_start_time)
                    remaining = max(0, 60 - elapsed)
                    
                if remaining > 0:
                    st.info(f"**Preparation Time:** {remaining} seconds remaining")
                    st.progress(1 - (remaining / 60))
                    
                    # Add skip button
                    if st.button("Skip Preparation and Start Now"):
                        st.session_state.part2_prep_complete = True
                        st.rerun()
                    
                    # Auto-refresh every second for smooth countdown
                    time.sleep(1)
                    st.rerun()
                else:
                    # Preparation time is up
                    st.session_state.part2_prep_complete = True
                    st.session_state.part2_prep_elapsed = 60
                    reset_silence_timer("part2_long")  # Start timer for long response
                    st.rerun()
            
            # After preparation, show speaking prompt
            if st.session_state.part2_prep_complete and not st.session_state.part2_long_response:
                st.success("Preparation time complete!")
                st.write("**Now, please tell me about the topic. Speak for about 1-2 minutes.**")
                
                # Show redirect message if available
                if st.session_state.part2_long_response_redirect_message:
                    st.write("---")
                    st.warning(f"**Examiner:** {st.session_state.part2_long_response_redirect_message}")
                    st.info("Please revise your response to better address the prompt card above.")
                    st.write("---")
                
                # ===== MODE-SPECIFIC INPUT FOR LONG RESPONSE =====
                if st.session_state.test_mode == 'text':
                    # ===== TEXT MODE =====
                    # Silence detection for Part 2 long response
                    silence_status = check_silence_and_update("part2_long", 60)  # 60s check-in, 120s auto-skip
                
                    # Show check-in message if threshold reached
                    if silence_status['show_check_in'] and st.session_state.part2_long_check_in_message:
                        st.info(f"{st.session_state.part2_long_check_in_message}")
                
                    # Handle auto-skip if timeout reached
                    if silence_status['should_skip']:
                        st.session_state.part2_conversation_history.append({
                            'role': 'candidate',
                            'content': '[No response - timed out]'
                        })
                        st.session_state.part2_long_response = "[No response provided]"
                    
                        completion_message = generate_part_completion_message(2, st.session_state.part2_conversation_history)
                        st.session_state.part2_completion_message = completion_message
                        st.session_state.part2_showing_completion = True
                        st.session_state.part2_conversation_history.append({
                            'role': 'examiner',
                            'content': completion_message
                        })
                    
                        st.session_state.part2_complete = True
                        reset_silence_timer("part2_long")
                        st.rerun()
                
                    # Large text area for long response
                    with st.form(key="part2_long_response_form", clear_on_submit=True):
                        st.caption("Max words: 400")
                        long_response = st.text_area(
                            "Your response (aim for 1-2 minutes):",
                            height=200,
                            key="part2_response_input",
                            help="Take your time and organize your thoughts. Cover all the bullet points if possible."
                        )
                    
                        form_submitted = st.form_submit_button("Submit Response")
                
                    if form_submitted:
                        # Save the response immediately before form clears
                        submitted_response = long_response.strip() if long_response else ""
                    
                        if submitted_response:
                            # Calculate word count
                            word_count = len(submitted_response.split())
                        
                            # Hard limit: block if over 400 words
                            if word_count > 400:
                                st.error(f"Your response is {word_count} words. Please reduce it to 400 words or less before submitting.")
                            else:
                                # Get main prompt for relevance checking
                                main_prompt = st.session_state.part2_prompt_card.get('main_prompt', '')
                            
                                # Always check relevance first (even after redirect)
                                bullet_points = "\n".join(st.session_state.part2_prompt_card.get('bullet_points', []))
                                prompt_context = f"{main_prompt}\n{bullet_points}"
                            
                                is_relevant, relevance_score = check_relevance(
                                    submitted_response,
                                    main_prompt,
                                    prompt_context
                                )
                            
                                # If we've already redirected once AND answer is still not relevant, skip to completion message
                                if st.session_state.part2_long_response_redirect_count >= 1 and (not is_relevant and relevance_score < 0.7):
                                    # Already redirected and STILL irrelevant - show completion message
                                    st.session_state.part2_long_response = submitted_response
                                    st.session_state.part2_long_response_redirect_count = 0
                                    st.session_state.part2_long_response_redirect_message = ""
                                
                                    # Add response to history
                                    st.session_state.part2_conversation_history.append({
                                        'role': 'user',
                                        'content': submitted_response
                                    })
                                
                                    # Generate completion message
                                    completion_message = generate_part_completion_message(2, st.session_state.part2_conversation_history)
                                    st.session_state.part2_completion_message = completion_message
                                    st.session_state.part2_showing_completion = True
                                    st.session_state.part2_conversation_history.append({
                                        'role': 'examiner',
                                        'content': completion_message
                                    })
                                
                                    st.session_state.part2_complete = True
                                    reset_silence_timer("part2_long")
                                    st.rerun()
                            
                                # If already redirected but answer IS now relevant, proceed to rounding-off
                                elif st.session_state.part2_long_response_redirect_count >= 1 and (is_relevant or relevance_score >= 0.7):
                                    # Answer is now relevant after redirect - proceed normally
                                    st.session_state.part2_long_response = submitted_response
                                    st.session_state.part2_long_response_redirect_count = 0
                                    st.session_state.part2_long_response_redirect_message = ""
                                
                                    # Add response to history
                                    st.session_state.part2_conversation_history.append({
                                        'role': 'user',
                                        'content': submitted_response
                                    })
                                
                                    # Generate GPT acknowledgment
                                    with st.spinner("Processing..."):
                                        examiner_prompt = get_examiner_prompt_part2(
                                            st.session_state.part2_conversation_history,
                                            phase="long_response"
                                        )
                                        examiner_response = get_examiner_response(examiner_prompt, st.session_state.part2_conversation_history)
                                    
                                        st.session_state.part2_conversation_history.append({
                                            'role': 'examiner',
                                            'content': examiner_response
                                        })
                                    
                                        st.session_state.part2_long_response_acknowledgment = examiner_response
                                
                                    # Generate rounding off questions
                                    with st.spinner("Generating follow-up questions..."):
                                        try:
                                            rounding_questions = generate_rounding_off_questions(
                                                submitted_response,
                                                st.session_state.part2_prompt_card.get('main_prompt', '')
                                            )
                                            if rounding_questions and len(rounding_questions) > 0:
                                                st.session_state.part2_rounding_off_questions = rounding_questions
                                            else:
                                                st.session_state.part2_rounding_off_questions = ["Was that easy to talk about?", "Is that still important to you?"]
                                        except Exception as e:
                                            st.error(f"Error generating questions: {str(e)}")
                                            st.session_state.part2_rounding_off_questions = ["Was that easy to talk about?", "Is that still important to you?"]
                                
                                    # Reset states for rounding questions
                                    st.session_state.part2_rounding_question_index = 0
                                    st.session_state.part2_rounding_questions_answered = 0
                                    st.session_state.part2_waiting_for_rounding_answer = False
                                    st.session_state.part2_rounding_redirect_count = 0
                                    st.session_state.part2_current_rounding_question = ""
                                    st.session_state.part2_rounding_acknowledgment = ""
                                    reset_silence_timer("part2_long")
                                    st.rerun()
                                else:
                                    # First submission (no redirect yet) - relevance already checked above
                                    # If not relevant, redirect once
                                    if not is_relevant and relevance_score < 0.7:
                                        # First redirect - send polite nudge
                                        # First, add the user's irrelevant answer to history
                                        st.session_state.part2_conversation_history.append({
                                            'role': 'user',
                                            'content': submitted_response
                                        })
                                        
                                        redirect_message = generate_redirect_message(main_prompt)
                                        st.session_state.part2_long_response_redirect_count = 1
                                    
                                        # Add redirect to history
                                        st.session_state.part2_conversation_history.append({
                                            'role': 'examiner',
                                            'content': redirect_message
                                        })
                                    
                                        # Store redirect message to display persistently
                                        st.session_state.part2_long_response_redirect_message = redirect_message
                                        # Don't save response yet - let them resubmit
                                        reset_silence_timer("part2_long")  # Reset timer for redirect
                                        st.rerun()
                                    else:
                                        # Response is relevant - process normally
                                        st.session_state.part2_long_response = submitted_response
                                    
                                        # Clear redirect message and reset redirect count since answer is relevant
                                        st.session_state.part2_long_response_redirect_message = ""
                                        st.session_state.part2_long_response_redirect_count = 0
                                    
                                        # Add to conversation history
                                        st.session_state.part2_conversation_history.append({
                                            'role': 'user',
                                            'content': submitted_response
                                        })
                                    
                                        # Generate GPT acknowledgment first
                                        with st.spinner("Processing..."):
                                            examiner_prompt = get_examiner_prompt_part2(
                                                st.session_state.part2_conversation_history,
                                                phase="long_response"
                                            )
                                            examiner_response = get_examiner_response(examiner_prompt, st.session_state.part2_conversation_history)
                                        
                                            # Add examiner's acknowledgment to history
                                            st.session_state.part2_conversation_history.append({
                                                'role': 'examiner',
                                                'content': examiner_response
                                            })
                                        
                                            # Store the acknowledgment to show it
                                            st.session_state.part2_long_response_acknowledgment = examiner_response
                                    
                                        # Generate rounding off questions
                                        try:
                                            with st.spinner("Generating follow-up questions..."):
                                                rounding_questions = generate_rounding_off_questions(
                                                    submitted_response,
                                                    st.session_state.part2_prompt_card.get('main_prompt', '')
                                                )
                                                if rounding_questions and len(rounding_questions) > 0:
                                                    st.session_state.part2_rounding_off_questions = rounding_questions
                                                else:
                                                    # Use fallback if GPT returns empty
                                                    st.session_state.part2_rounding_off_questions = ["Was that easy to talk about?", "Is that still important to you?"]
                                        except Exception as e:
                                            st.error(f"Error generating questions: {str(e)}")
                                            # Use fallback questions on error
                                            st.session_state.part2_rounding_off_questions = ["Was that easy to talk about?", "Is that still important to you?"]
                                    
                                        # Reset states for rounding questions
                                        st.session_state.part2_rounding_question_index = 0
                                        st.session_state.part2_rounding_questions_answered = 0
                                        st.session_state.part2_waiting_for_rounding_answer = False
                                        st.session_state.part2_rounding_redirect_count = 0
                                        st.session_state.part2_current_rounding_question = ""
                                        st.session_state.part2_rounding_acknowledgment = ""
                                        reset_silence_timer("part2_long")  # Reset timer after long response
                                        st.rerun()
                        else:
                            st.warning("Please provide a response before submitting.")
            
                elif st.session_state.test_mode == 'voice':
                    # ===== VOICE MODE FOR LONG RESPONSE =====
                    st.write("")
                    st.write("**Time Limit: 120 seconds (2 minutes)**")
                
                    # Voice timer logic (actual limit: 130 seconds, but we tell them 120)
                    if st.session_state.part2_voice_timer_start is not None:
                        expired, elapsed, remaining = check_voice_timer_expired(
                            st.session_state.part2_voice_timer_start,
                            130  # Actual time limit (10s buffer)
                        )
                    
                        # Auto-skip if expired (no countdown shown)
                        if expired:
                            st.warning("Time's up! Moving to next section...")
                            st.session_state.part2_conversation_history.append({
                                'role': 'candidate',
                                'content': '[No response - timed out]'
                            })
                            st.session_state.part2_long_response = "[No response provided]"
                        
                            completion_message = generate_part_completion_message(2, st.session_state.part2_conversation_history)
                            st.session_state.part2_completion_message = completion_message
                            st.session_state.part2_showing_completion = True
                            st.session_state.part2_conversation_history.append({
                                'role': 'examiner',
                                'content': completion_message
                            })
                        
                            st.session_state.part2_complete = True
                            st.session_state.part2_voice_timer_start = None
                            time.sleep(1)
                            st.rerun()
                
                    # Audio recording - use unique key based on redirect count to reset widget
                    audio_key = f"part2_long_r{st.session_state.part2_long_response_redirect_count}"
                    audio_input = st.audio_input("Record your response (1-2 minutes)", key=audio_key)
                
                    if st.session_state.part2_voice_timer_start is None:
                        st.session_state.part2_voice_timer_start = time.time()
                
                    if audio_input is not None:
                        with st.spinner("Transcribing..."):
                            result = transcribe_audio(audio_input, include_timestamps=True)
                            submitted_response = result['text'] if isinstance(result, dict) else result
                    
                        if submitted_response:
                            # Show simple confirmation (no transcription text or word count - more realistic)
                            st.success("Answer transcribed successfully")
                        
                            if st.button("Submit Response", key=f"{audio_key}_submit"):
                                word_count = len(submitted_response.split())
                                if word_count > 400:
                                    st.error(f"Your response is {word_count} words. Please record again with 400 words or less.")
                                    st.rerun()
                            
                                # Check relevance
                                main_prompt = st.session_state.part2_prompt_card.get('main_prompt', '')
                                bullet_points = "\n".join(st.session_state.part2_prompt_card.get('bullet_points', []))
                                prompt_context = f"{main_prompt}\n{bullet_points}"
                            
                                is_relevant, relevance_score = check_relevance(
                                    submitted_response,
                                    main_prompt,
                                    prompt_context
                                )
                            
                                # Handle relevance (same logic as text mode)
                                if st.session_state.part2_long_response_redirect_count >= 1 and (not is_relevant and relevance_score < 0.7):
                                    # Show completion after second irrelevant
                                    st.session_state.part2_long_response = submitted_response
                                    st.session_state.part2_conversation_history.append({'role': 'user', 'content': submitted_response})
                                    
                                    # Store timing data
                                    store_voice_timing_data('Part 2 Long Response (Irrelevant)', main_prompt, submitted_response, result)
                                
                                    completion_message = generate_part_completion_message(2, st.session_state.part2_conversation_history)
                                    st.session_state.part2_completion_message = completion_message
                                    st.session_state.part2_showing_completion = True
                                    st.session_state.part2_conversation_history.append({'role': 'examiner', 'content': completion_message})
                                
                                    st.session_state.part2_complete = True
                                    st.session_state.part2_voice_timer_start = None
                                    st.rerun()
                            
                                elif st.session_state.part2_long_response_redirect_count >= 1 and (is_relevant or relevance_score >= 0.7):
                                    # Proceed to rounding after relevant answer
                                    st.session_state.part2_long_response = submitted_response
                                    st.session_state.part2_conversation_history.append({'role': 'user', 'content': submitted_response})
                                    
                                    # Store timing data
                                    store_voice_timing_data('Part 2 Long Response', main_prompt, submitted_response, result)
                                
                                    with st.spinner("Processing..."):
                                        examiner_prompt = get_examiner_prompt_part2(st.session_state.part2_conversation_history, phase="long_response")
                                        examiner_response = get_examiner_response(examiner_prompt, st.session_state.part2_conversation_history)
                                        st.session_state.part2_conversation_history.append({'role': 'examiner', 'content': examiner_response})
                                        st.session_state.part2_long_response_acknowledgment = examiner_response
                                
                                    with st.spinner("Generating follow-up questions..."):
                                        try:
                                            rounding_questions = generate_rounding_off_questions(submitted_response, main_prompt)
                                            st.session_state.part2_rounding_off_questions = rounding_questions if rounding_questions else ["Was that easy to talk about?", "Is that still important to you?"]
                                        except:
                                            st.session_state.part2_rounding_off_questions = ["Was that easy to talk about?", "Is that still important to you?"]
                                
                                    st.session_state.part2_rounding_question_index = 0
                                    st.session_state.part2_rounding_questions_answered = 0
                                    st.session_state.part2_voice_timer_start = None
                                    st.rerun()
                            
                                elif not is_relevant and relevance_score < 0.7:
                                    # First redirect - add user's answer first, then redirect
                                    st.session_state.part2_conversation_history.append({'role': 'user', 'content': submitted_response})
                                    
                                    # Store timing data
                                    store_voice_timing_data('Part 2 Long Response (Irrelevant - 1st attempt)', main_prompt, submitted_response, result)
                                    
                                    redirect_message = generate_redirect_message(main_prompt)
                                    st.session_state.part2_long_response_redirect_count = 1
                                    st.session_state.part2_conversation_history.append({'role': 'examiner', 'content': redirect_message})
                                    st.session_state.part2_long_response_redirect_message = redirect_message
                                    st.session_state.part2_voice_timer_start = None
                                    st.rerun()
                            
                                else:
                                    # Relevant, proceed normally
                                    st.session_state.part2_long_response = submitted_response
                                    st.session_state.part2_conversation_history.append({'role': 'user', 'content': submitted_response})
                                    
                                    # Store timing data
                                    store_voice_timing_data('Part 2 Long Response', main_prompt, submitted_response, result)
                                
                                    with st.spinner("Processing..."):
                                        examiner_prompt = get_examiner_prompt_part2(st.session_state.part2_conversation_history, phase="long_response")
                                        examiner_response = get_examiner_response(examiner_prompt, st.session_state.part2_conversation_history)
                                        st.session_state.part2_conversation_history.append({'role': 'examiner', 'content': examiner_response})
                                        st.session_state.part2_long_response_acknowledgment = examiner_response
                                
                                    with st.spinner("Generating follow-up questions..."):
                                        try:
                                            rounding_questions = generate_rounding_off_questions(submitted_response, main_prompt)
                                            st.session_state.part2_rounding_off_questions = rounding_questions if rounding_questions else ["Was that easy to talk about?", "Is that still important to you?"]
                                        except:
                                            st.session_state.part2_rounding_off_questions = ["Was that easy to talk about?", "Is that still important to you?"]
                                
                                    st.session_state.part2_rounding_question_index = 0
                                    st.session_state.part2_rounding_questions_answered = 0
                                    st.session_state.part2_voice_timer_start = None
                                    st.rerun()
                
                    # Auto-refresh after 130 seconds to check for timeout
                    if st.session_state.part2_voice_timer_start is not None and audio_input is None:
                        st_autorefresh(interval=130000, key="part2_voice_timer")
        
            # Show completion message if Part 2 is done (check this FIRST before showing rounding questions)
            if st.session_state.part2_showing_completion and st.session_state.part2_completion_message:
                st.write("---")
                st.write(f"**Examiner:** {st.session_state.part2_completion_message}")
                st.write("")
                if st.button("Continue to Part 3", key="part2_continue_button"):
                    initialize_part3()
                    st.session_state.step = "PART_3"
                    st.rerun()
            # Rounding off questions phase
            elif st.session_state.part2_long_response:
                # Show GPT's acknowledgment of the long response if available
                if st.session_state.part2_long_response_acknowledgment:
                    st.write("---")
                    st.write(f"**Examiner:** {st.session_state.part2_long_response_acknowledgment}")
                    st.write("---")
                    # Clear it so it doesn't show again
                    st.session_state.part2_long_response_acknowledgment = ""
            
                # Ensure we have rounding off questions (use fallback if missing)
                if not st.session_state.part2_rounding_off_questions or len(st.session_state.part2_rounding_off_questions) == 0:
                    st.session_state.part2_rounding_off_questions = ["Was that easy to talk about?", "Is that still important to you?"]
            
                # Check if we've answered 2 questions total (including redirects)
                if st.session_state.part2_rounding_questions_answered < 2:
                    # Show GPT's acknowledgment of previous rounding answer if available (FIRST, before showing new question)
                    if st.session_state.part2_rounding_acknowledgment:
                        st.write("---")
                        st.write(f"**Examiner:** {st.session_state.part2_rounding_acknowledgment}")
                        st.write("---")
                        # Clear it so it doesn't show again
                        st.session_state.part2_rounding_acknowledgment = ""
                
                    # If we don't have a current question, or we're ready for a new question
                    if not st.session_state.part2_waiting_for_rounding_answer and st.session_state.part2_current_rounding_question == "":
                        # FIRST: Check if we've already asked 2 questions
                        if st.session_state.part2_rounding_questions_answered >= 2:
                            # Part 2 is complete
                            completion_message = generate_part_completion_message(2, st.session_state.part2_conversation_history)
                            st.session_state.part2_completion_message = completion_message
                            st.session_state.part2_showing_completion = True
                        
                            st.session_state.part2_conversation_history.append({
                                'role': 'examiner',
                                'content': completion_message
                            })
                            st.rerun()
                        else:
                            # Get current question (use index to cycle through questions if needed)
                            if st.session_state.part2_rounding_question_index >= len(st.session_state.part2_rounding_off_questions):
                                st.session_state.part2_rounding_question_index = 0
                        
                            current_question = st.session_state.part2_rounding_off_questions[st.session_state.part2_rounding_question_index]
                        
                            # Set as current question
                            st.session_state.part2_current_rounding_question = current_question
                        
                            # Add question to history
                            st.session_state.part2_conversation_history.append({
                                'role': 'examiner',
                                'content': current_question
                            })
                        
                            # Set waiting state
                            st.session_state.part2_waiting_for_rounding_answer = True
                            st.session_state.part2_rounding_redirect_count = 0  # Reset redirect count for new question
                            reset_silence_timer("part2_rounding")  # Reset timer for new question
                            st.rerun()
                
                    # Display the current question (text mode only)
                    if st.session_state.part2_current_rounding_question and st.session_state.test_mode == 'text':
                        st.write("---")
                        st.write("### Rounding Off Questions")
                        st.write("I'll ask you some follow-up questions. Please respond with brief, conversational responses.")
                        st.write(f"**Examiner:** {st.session_state.part2_current_rounding_question}")
                
                    # Silence detection for Part 2 rounding-off questions (TEXT MODE ONLY)
                    if st.session_state.test_mode == 'text' and st.session_state.part2_waiting_for_rounding_answer and st.session_state.part2_current_rounding_question:
                        silence_status = check_silence_and_update("part2_rounding", 30)  # 30s check-in, 60s auto-skip
                    
                        # Show check-in message if threshold reached
                        if silence_status['show_check_in'] and st.session_state.part2_rounding_check_in_message:
                            st.info(f"{st.session_state.part2_rounding_check_in_message}")
                    
                        # Handle auto-skip if timeout reached
                        if silence_status['should_skip']:
                            # Store "No response" in conversation history
                            st.session_state.part2_conversation_history.append({
                                'role': 'candidate',
                                'content': '[No response - timed out]'
                            })
                            # Move to next question
                            st.session_state.part2_current_rounding_question = ""
                            st.session_state.part2_waiting_for_rounding_answer = False
                            st.session_state.part2_rounding_questions_answered += 1
                            st.session_state.part2_rounding_question_index += 1
                            st.session_state.part2_rounding_redirect_count = 0
                            reset_silence_timer("part2_rounding")
                            st.rerun()
                
                    # Input for rounding off answer
                    if st.session_state.part2_waiting_for_rounding_answer:
                        if st.session_state.test_mode == 'text':
                            with st.form(key=f"rounding_answer_{st.session_state.part2_rounding_question_index}", clear_on_submit=True):
                                st.caption("Max words: 65")
                                rounding_answer = st.text_input("Your answer:", key=f"rounding_input_{st.session_state.part2_rounding_question_index}")
                                form_submitted = st.form_submit_button("Submit Answer")
                        
                            if form_submitted:
                                if rounding_answer.strip():
                                    # Check word count limit
                                    word_count = len(rounding_answer.split())
                                    if word_count > 65:
                                        st.error(f"Your answer is {word_count} words. Please reduce it to 65 words or less.")
                                        st.rerun()
                                
                                    current_question = st.session_state.part2_current_rounding_question
                                
                                    # Check if we've already redirected once - if so, move on regardless of relevance
                                    if st.session_state.part2_rounding_redirect_count >= 1:
                                        # Already redirected once - move on to next question regardless of relevance
                                        st.session_state.part2_conversation_history.append({
                                            'role': 'user',
                                            'content': rounding_answer
                                        })
                                    
                                        # Add thank you message
                                        st.session_state.part2_conversation_history.append({
                                            'role': 'examiner',
                                            'content': "Thank you. Let's move on."
                                        })
                                    
                                        # Reset redirect count and move to next question
                                        st.session_state.part2_rounding_redirect_count = 0
                                        st.session_state.part2_current_rounding_question = ""
                                        st.session_state.part2_waiting_for_rounding_answer = False
                                        st.session_state.part2_rounding_questions_answered += 1
                                        st.session_state.part2_rounding_question_index += 1  # Move to next question
                                    
                                        # Check if we've completed Part 2
                                        if st.session_state.part2_rounding_questions_answered >= 2:
                                            completion_message = generate_part_completion_message(2, st.session_state.part2_conversation_history)
                                            st.session_state.part2_completion_message = completion_message
                                            st.session_state.part2_showing_completion = True
                                        
                                            st.session_state.part2_conversation_history.append({
                                                'role': 'examiner',
                                                'content': completion_message
                                            })
                                    
                                        reset_silence_timer("part2_rounding")  # Reset timer after answer
                                        st.rerun()
                                    else:
                                        # Check relevance before processing
                                        context = format_conversation_history(st.session_state.part2_conversation_history[-4:])
                                        is_relevant, relevance_score = check_relevance(
                                            rounding_answer,
                                            current_question,
                                            context
                                        )
                                    
                                        # If not relevant, redirect once
                                        if not is_relevant and relevance_score < 0.7:
                                            # First redirect - send polite nudge
                                            # First, add the user's irrelevant answer to history
                                            st.session_state.part2_conversation_history.append({
                                                'role': 'user',
                                                'content': rounding_answer
                                            })
                                            
                                            redirect_message = generate_redirect_message(current_question)
                                            st.session_state.part2_rounding_redirect_count = 1
                                        
                                            # Add redirect to history
                                            st.session_state.part2_conversation_history.append({
                                                'role': 'examiner',
                                                'content': redirect_message
                                            })
                                        
                                            # Show redirect message
                                            st.session_state.part2_current_rounding_question = redirect_message
                                            st.session_state.part2_waiting_for_rounding_answer = True
                                            reset_silence_timer("part2_rounding")  # Reset timer for redirect
                                            st.rerun()
                                        else:
                                            # Response is relevant - process normally
                                            # Add answer to history
                                            st.session_state.part2_conversation_history.append({
                                                'role': 'user',
                                                'content': rounding_answer
                                            })
                                        
                                            # Reset redirect count since answer is relevant
                                            st.session_state.part2_rounding_redirect_count = 0
                                        
                                            # Generate GPT acknowledgment
                                            with st.spinner("Processing..."):
                                                examiner_prompt = get_examiner_prompt_part2(
                                                    st.session_state.part2_conversation_history,
                                                    phase="rounding_off"
                                                )
                                            
                                                examiner_response = get_examiner_response(examiner_prompt, st.session_state.part2_conversation_history)
                                            
                                                # Add examiner's response to history
                                                st.session_state.part2_conversation_history.append({
                                                    'role': 'examiner',
                                                    'content': examiner_response
                                                })
                                            
                                                # Store acknowledgment to show on next render
                                                st.session_state.part2_rounding_acknowledgment = examiner_response
                                            
                                                # Count question as answered and reset for next
                                                st.session_state.part2_rounding_questions_answered += 1
                                                st.session_state.part2_rounding_question_index += 1  # Move to next question
                                                st.session_state.part2_current_rounding_question = ""
                                                st.session_state.part2_waiting_for_rounding_answer = False
                                            
                                                # Check if we've completed Part 2
                                                if st.session_state.part2_rounding_questions_answered >= 2:
                                                    completion_message = generate_part_completion_message(2, st.session_state.part2_conversation_history)
                                                    st.session_state.part2_completion_message = completion_message
                                                    st.session_state.part2_showing_completion = True
                                                
                                                    st.session_state.part2_conversation_history.append({
                                                        'role': 'examiner',
                                                        'content': completion_message
                                                    })
                                            
                                                reset_silence_timer("part2_rounding")  # Reset timer after answer
                                                st.rerun()
                    
                        elif st.session_state.test_mode == 'voice':
                            # ===== VOICE MODE FOR ROUNDING OFF QUESTIONS =====
                            st.write("")
                            st.write("**Time Limit: 30 seconds**")
                        
                            # Play question audio (autoplay only once per question, but keep player visible)
                            if st.session_state.part2_current_rounding_question:
                                # Create unique key for this question
                                current_audio_key = f"p2r_q{st.session_state.part2_rounding_question_index}_r{st.session_state.part2_rounding_redirect_count}"
                                
                                # Generate audio
                                question_audio_file = text_to_speech(st.session_state.part2_current_rounding_question)
                                if question_audio_file:
                                    # Only autoplay if we haven't played this question yet
                                    should_autoplay = st.session_state.get('part2_rounding_audio_played_key') != current_audio_key
                                    st.audio(question_audio_file, format="audio/mp3", autoplay=should_autoplay)
                                    st.caption("Audio: Question")
                                    
                                    # Mark as played after first time
                                    if should_autoplay:
                                        st.session_state.part2_rounding_audio_played_key = current_audio_key
                        
                            # Voice timer logic (actual limit: 40 seconds, but we tell them 30)
                            if st.session_state.part2_rounding_voice_timer_start is not None:
                                expired, elapsed, remaining = check_voice_timer_expired(
                                    st.session_state.part2_rounding_voice_timer_start,
                                    40  # Actual time limit (10s buffer)
                                )
                            
                                # Auto-skip if expired (no countdown shown)
                                if expired:
                                    st.warning("Time's up! Moving to next question...")
                                    st.session_state.part2_conversation_history.append({
                                        'role': 'candidate',
                                        'content': '[No response - timed out]'
                                    })
                                    # Move to next question
                                    st.session_state.part2_current_rounding_question = ""
                                    st.session_state.part2_waiting_for_rounding_answer = False
                                    st.session_state.part2_rounding_questions_answered += 1
                                    st.session_state.part2_rounding_question_index += 1
                                    st.session_state.part2_rounding_redirect_count = 0
                                    st.session_state.part2_rounding_voice_timer_start = None
                                    st.session_state.part2_rounding_voice_audio_data = None
                                    st.session_state.part2_rounding_audio_played_key = None  # Clear audio key
                                    time.sleep(1)
                                    st.rerun()
                        
                            # Audio recording widget
                            audio_key = f"part2_rounding_q{st.session_state.part2_rounding_question_index}_r{st.session_state.part2_rounding_redirect_count}"
                            audio_input = st.audio_input("Record your answer", key=audio_key)
                        
                            # Start timer when audio widget appears
                            if st.session_state.part2_rounding_voice_timer_start is None:
                                st.session_state.part2_rounding_voice_timer_start = time.time()
                        
                            # Process audio when user stops recording
                            if audio_input is not None:
                                # Transcribe the audio with timestamps
                                with st.spinner("Transcribing your answer..."):
                                    result = transcribe_audio(audio_input, include_timestamps=True)
                                    rounding_answer = result['text'] if isinstance(result, dict) else result
                            
                                if rounding_answer:
                                    # Show simple confirmation (no transcription text - more realistic)
                                    st.success("Answer transcribed successfully")
                                
                                    # Submit button
                                    if st.button("Submit Answer", key=f"{audio_key}_submit"):
                                        # Clear audio data and timer
                                        st.session_state.part2_rounding_voice_timer_start = None
                                        st.session_state.part2_rounding_voice_audio_data = None
                                    
                                        # Check word count limit
                                        word_count = len(rounding_answer.split())
                                        if word_count > 65:
                                            st.error(f"Your answer is {word_count} words. Please record again with 65 words or less.")
                                            st.rerun()
                                    
                                        current_question = st.session_state.part2_current_rounding_question
                                    
                                        # Check if we've already redirected once
                                        if st.session_state.part2_rounding_redirect_count >= 1:
                                            # Already redirected - move on
                                            st.session_state.part2_conversation_history.append({
                                                'role': 'user',
                                                'content': rounding_answer
                                            })
                                            
                                            # Store timing data
                                            store_voice_timing_data('Part 2 Rounding-off', current_question, rounding_answer, result)
                                        
                                            st.session_state.part2_conversation_history.append({
                                                'role': 'examiner',
                                                'content': "Thank you. Let's move on."
                                            })
                                        
                                            st.session_state.part2_rounding_redirect_count = 0
                                            st.session_state.part2_current_rounding_question = ""
                                            st.session_state.part2_waiting_for_rounding_answer = False
                                            st.session_state.part2_rounding_questions_answered += 1
                                            st.session_state.part2_rounding_question_index += 1
                                            st.session_state.part2_rounding_audio_played_key = None  # Clear audio key
                                        
                                            if st.session_state.part2_rounding_questions_answered >= 2:
                                                completion_message = generate_part_completion_message(2, st.session_state.part2_conversation_history)
                                                st.session_state.part2_completion_message = completion_message
                                                st.session_state.part2_showing_completion = True
                                            
                                                st.session_state.part2_conversation_history.append({
                                                    'role': 'examiner',
                                                    'content': completion_message
                                                })
                                        
                                            st.rerun()
                                        else:
                                            # First answer - check relevance
                                            context = format_conversation_history(st.session_state.part2_conversation_history[-6:])
                                            is_relevant, relevance_score = check_relevance(
                                                rounding_answer,
                                                current_question,
                                                context
                                            )
                                        
                                            if is_relevant or relevance_score >= 0.7:
                                                # Relevant answer
                                                st.session_state.part2_conversation_history.append({
                                                    'role': 'user',
                                                    'content': rounding_answer
                                                })
                                                
                                                # Store timing data
                                                store_voice_timing_data('Part 2 Rounding-off', current_question, rounding_answer, result)
                                            
                                                # Generate acknowledgment
                                                examiner_prompt = get_examiner_prompt_part2(
                                                    st.session_state.part2_conversation_history,
                                                    phase="rounding_off"
                                                )
                                                acknowledgment = get_examiner_response(examiner_prompt, st.session_state.part2_conversation_history)
                                                st.session_state.part2_rounding_acknowledgment = acknowledgment
                                                st.session_state.part2_conversation_history.append({
                                                    'role': 'examiner',
                                                    'content': acknowledgment
                                                })
                                            
                                                # Move to next question
                                                st.session_state.part2_rounding_redirect_count = 0
                                                st.session_state.part2_current_rounding_question = ""
                                                st.session_state.part2_waiting_for_rounding_answer = False
                                                st.session_state.part2_rounding_questions_answered += 1
                                                st.session_state.part2_rounding_question_index += 1
                                                st.session_state.part2_rounding_audio_played_key = None  # Clear audio key
                                            
                                                if st.session_state.part2_rounding_questions_answered >= 2:
                                                    completion_message = generate_part_completion_message(2, st.session_state.part2_conversation_history)
                                                    st.session_state.part2_completion_message = completion_message
                                                    st.session_state.part2_showing_completion = True
                                                
                                                    st.session_state.part2_conversation_history.append({
                                                        'role': 'examiner',
                                                        'content': completion_message
                                                    })
                                            
                                                st.rerun()
                                            else:
                                                # Irrelevant answer - send redirect, store timing data
                                                st.session_state.part2_rounding_redirect_count += 1
                                            
                                                st.session_state.part2_conversation_history.append({
                                                    'role': 'user',
                                                    'content': rounding_answer
                                                })
                                                
                                                # Store timing data
                                                store_voice_timing_data('Part 2 Rounding-off (Irrelevant)', current_question, rounding_answer, result)
                                            
                                                redirect_message = generate_redirect_message(current_question)
                                                st.session_state.part2_conversation_history.append({
                                                    'role': 'examiner',
                                                    'content': redirect_message
                                                })
                                            
                                                st.session_state.part2_current_rounding_question = redirect_message
                                                st.session_state.part2_waiting_for_rounding_answer = True
                                                st.session_state.part2_rounding_audio_played_key = None  # Clear audio key for new question
                                                st.rerun()
                        
                            # Auto-refresh after 40 seconds to check for timeout
                            if st.session_state.part2_rounding_voice_timer_start is not None and audio_input is None:
                                st_autorefresh(interval=40000, key="part2_rounding_voice_timer")
    
    elif st.session_state.step == "PART_3":
        st.write("### Part 3: The Discussion")
        st.write("I’ll ask you some questions related to Part 2. Please respond with thoughtful, detailed responses.")
        
        # Initialize Part 3 if needed
        if not st.session_state.part3_initialized:
            initialize_part3()
        
        # Show completion message and button if Part 3 is done
        if st.session_state.part3_showing_completion:
            st.success(st.session_state.part3_completion_message)
            if st.button("View Results"):
                st.session_state.step = "SCORING"
                st.rerun()
        else:
            # Display theme
            st.info(f"**Discussion Topic:** {st.session_state.part3_theme}")
            
            # Check if we need to generate a new question (first question OR after skip/completion of previous)
            if not st.session_state.part3_current_question and not st.session_state.part3_waiting_for_answer and st.session_state.part3_questions_asked < 3:
                with st.spinner("Thinking of a question..."):
                    question = generate_part3_question(
                        st.session_state.part3_theme,
                        st.session_state.part3_questions_asked,
                        st.session_state.part3_conversation_history,
                        question_type="main_question"
                    )
                    st.session_state.part3_current_question = question
                    st.session_state.part3_conversation_history.append({
                        'role': 'examiner',
                        'content': question
                    })
                    st.session_state.part3_waiting_for_answer = True
                    st.session_state.part3_audio_played_key = None  # Reset audio played tracker
                    reset_silence_timer("part3")  # Reset timer for new question
                    st.rerun()
            
            # Display the current question (text mode only)
            if st.session_state.part3_current_question and st.session_state.test_mode == 'text':
                # If there's an acknowledgment, show it first, then the question
                if st.session_state.part3_acknowledgment:
                    combined_response = st.session_state.part3_acknowledgment + " " + st.session_state.part3_current_question
                    st.write("**Examiner:** " + combined_response)
                    # Don't clear acknowledgment here - it will be cleared when next acknowledgment is generated
                else:
                    st.write("**Examiner:** " + st.session_state.part3_current_question)
            
            # Silence detection for Part 3 (TEXT MODE ONLY)
            if st.session_state.test_mode == 'text' and st.session_state.part3_waiting_for_answer and st.session_state.part3_current_question:
                silence_status = check_silence_and_update("part3", 40)  # 40s check-in, 80s auto-skip
                
                # Show check-in message if threshold reached
                if silence_status['show_check_in'] and st.session_state.part3_check_in_message:
                    st.info(f"{st.session_state.part3_check_in_message}")
                
                # Handle auto-skip if timeout reached
                if silence_status['should_skip']:
                    # Store "No response" in conversation history
                    st.session_state.part3_conversation_history.append({
                        'role': 'candidate',
                        'content': '[No response - timed out]'
                    })
                    # Move to next question
                    st.session_state.part3_questions_asked += 1
                    st.session_state.part3_followups_asked = 0
                    st.session_state.part3_first_answer_word_count = 0
                    st.session_state.part3_current_question = ""
                    st.session_state.part3_waiting_for_answer = False
                    st.session_state.part3_redirect_count = 0
                    st.session_state.part3_acknowledgment = ""
                    reset_silence_timer("part3")
                    st.rerun()
            
            # Check if we've completed all 3 questions
            if st.session_state.part3_questions_asked >= 3:
                # Generate completion message
                st.session_state.part3_completion_message = "Thank you for your responses; that completes the speaking test!"
                st.session_state.part3_showing_completion = True
                st.rerun()
            
            # Text input for user's answer
            if st.session_state.part3_waiting_for_answer:
                if st.session_state.test_mode == 'text':
                    with st.form(key="part3_answer_form", clear_on_submit=True):
                        st.caption("Max words: 150")
                        user_answer = st.text_input("Your answer:", key="part3_answer_input")
                        form_submitted = st.form_submit_button("Submit Answer")
                    
                    # Check if form was submitted
                    if form_submitted:
                        if user_answer.strip():
                            # Check word count limit
                            word_count = len(user_answer.split())
                            if word_count > 150:
                                st.error(f"Your answer is {word_count} words. Please reduce it to 150 words or less.")
                                st.rerun()
                            
                            # Check relevance
                            context = format_conversation_history(st.session_state.part3_conversation_history[-6:])
                            is_relevant, relevance_score = check_relevance(
                                user_answer,
                                st.session_state.part3_current_question,
                                context
                            )
                            
                            # If answer is relevant, process normally
                            if is_relevant or relevance_score >= 0.7:
                                # Add user's answer to history
                                st.session_state.part3_conversation_history.append({
                                    'role': 'user',
                                    'content': user_answer
                                })
                                
                                # Reset redirect count
                                st.session_state.part3_redirect_count = 0
                                
                                # Generate acknowledgment
                                with st.spinner("Thinking..."):
                                    acknowledgment = generate_part3_acknowledgment(
                                        st.session_state.part3_theme,
                                        st.session_state.part3_conversation_history
                                    )
                                    st.session_state.part3_acknowledgment = acknowledgment
                                    
                                    # Word count-based follow-up logic
                                    # First answer >= 30 words: Only 1 follow-up
                                    # First answer < 30 words: 1-2 follow-ups based on follow-up 1 length
                                    
                                    if st.session_state.part3_followups_asked == 0:
                                        # First answer to main question - store word count and ALWAYS ask follow-up
                                        st.session_state.part3_first_answer_word_count = word_count
                                        
                                        follow_up_question = generate_part3_question(
                                            st.session_state.part3_theme,
                                            st.session_state.part3_questions_asked,
                                            st.session_state.part3_conversation_history,
                                            question_type="followup_question"
                                        )
                                        st.session_state.part3_current_question = follow_up_question
                                        st.session_state.part3_conversation_history.append({
                                            'role': 'examiner',
                                            'content': follow_up_question
                                        })
                                        st.session_state.part3_followups_asked = 1
                                    
                                    elif st.session_state.part3_followups_asked == 1:
                                        # Second answer (to follow-up 1)
                                        # Check if first answer was thorough (>= 30 words)
                                        if st.session_state.part3_first_answer_word_count >= 30:
                                            # First answer was detailed - move to next question regardless of this answer
                                            st.session_state.part3_questions_asked += 1
                                            st.session_state.part3_followups_asked = 0
                                            st.session_state.part3_first_answer_word_count = 0
                                            
                                            # Check if we've completed 3 questions
                                            if st.session_state.part3_questions_asked >= 3:
                                                # Done with Part 3
                                                st.session_state.part3_waiting_for_answer = False
                                                st.session_state.part3_current_question = ""
                                                st.session_state.part3_completion_message = "Thank you for your responses; that completes the speaking test!"
                                                st.session_state.part3_showing_completion = True
                                            else:
                                                # Generate new main question
                                                new_question = generate_part3_question(
                                                    st.session_state.part3_theme,
                                                    st.session_state.part3_questions_asked,
                                                    st.session_state.part3_conversation_history,
                                                    question_type="main_question"
                                                )
                                                st.session_state.part3_current_question = new_question
                                                st.session_state.part3_conversation_history.append({
                                                    'role': 'examiner',
                                                    'content': new_question
                                                })
                                        else:
                                            # First answer was brief - check this answer's length
                                            if word_count >= 20:
                                                # Follow-up answer is substantial - move to new main question
                                                st.session_state.part3_questions_asked += 1
                                                st.session_state.part3_followups_asked = 0
                                                st.session_state.part3_first_answer_word_count = 0
                                                
                                                # Check if we've completed 3 questions
                                                if st.session_state.part3_questions_asked >= 3:
                                                    # Done with Part 3
                                                    st.session_state.part3_waiting_for_answer = False
                                                    st.session_state.part3_current_question = ""
                                                    st.session_state.part3_completion_message = "Thank you for your responses; that completes the speaking test!"
                                                    st.session_state.part3_showing_completion = True
                                                else:
                                                    # Generate new main question
                                                    new_question = generate_part3_question(
                                                        st.session_state.part3_theme,
                                                        st.session_state.part3_questions_asked,
                                                        st.session_state.part3_conversation_history,
                                                        question_type="main_question"
                                                    )
                                                    st.session_state.part3_current_question = new_question
                                                    st.session_state.part3_conversation_history.append({
                                                        'role': 'examiner',
                                                        'content': new_question
                                                    })
                                            else:
                                                # Both answers were brief - ask second follow-up
                                                follow_up_question = generate_part3_question(
                                                    st.session_state.part3_theme,
                                                    st.session_state.part3_questions_asked,
                                                    st.session_state.part3_conversation_history,
                                                    question_type="followup_question"
                                                )
                                                st.session_state.part3_current_question = follow_up_question
                                                st.session_state.part3_conversation_history.append({
                                                    'role': 'examiner',
                                                    'content': follow_up_question
                                                })
                                                st.session_state.part3_followups_asked = 2
                                    
                                    else:  # followups_asked == 2
                                        # Third answer - always move to new main question
                                        st.session_state.part3_questions_asked += 1
                                        st.session_state.part3_followups_asked = 0  # Reset for next question
                                        st.session_state.part3_first_answer_word_count = 0  # Reset word count tracker
                                        
                                        # Check if we've completed 3 questions
                                        if st.session_state.part3_questions_asked >= 3:
                                            # Done with Part 3
                                            st.session_state.part3_waiting_for_answer = False
                                            st.session_state.part3_current_question = ""
                                            st.session_state.part3_completion_message = "Thank you for your responses; that completes the speaking test!"
                                            st.session_state.part3_showing_completion = True
                                        else:
                                            # Generate new main question
                                            new_question = generate_part3_question(
                                                st.session_state.part3_theme,
                                                st.session_state.part3_questions_asked,
                                                st.session_state.part3_conversation_history,
                                                question_type="main_question"
                                            )
                                            st.session_state.part3_current_question = new_question
                                            st.session_state.part3_conversation_history.append({
                                                'role': 'examiner',
                                                'content': new_question
                                            })
                                    
                                    st.rerun()
                        
                        # If answer is irrelevant and we've already redirected once, move on
                        elif st.session_state.part3_redirect_count >= 1:
                            # Second irrelevant answer - move on
                            st.session_state.part3_conversation_history.append({
                                'role': 'user',
                                'content': user_answer
                            })
                            
                            # Add thank you message
                            st.session_state.part3_conversation_history.append({
                                'role': 'examiner',
                                'content': "Thank you. Let's move on."
                            })
                            
                            # Reset redirect count and increment question counter
                            st.session_state.part3_redirect_count = 0
                            st.session_state.part3_questions_asked += 1
                            st.session_state.part3_followups_asked = 0  # Reset follow-ups for new question
                            st.session_state.part3_first_answer_word_count = 0  # Reset word count tracker
                            
                            # Check if we've completed 3 questions
                            if st.session_state.part3_questions_asked >= 3:
                                # Done with Part 3
                                st.session_state.part3_waiting_for_answer = False
                                st.session_state.part3_current_question = ""
                                st.session_state.part3_completion_message = "Thank you for your responses; that completes the speaking test!"
                                st.session_state.part3_showing_completion = True
                            else:
                                # Generate new main question
                                with st.spinner("Thinking of a question..."):
                                    new_question = generate_part3_question(
                                        st.session_state.part3_theme,
                                        st.session_state.part3_questions_asked,
                                        st.session_state.part3_conversation_history,
                                        question_type="main_question"
                                    )
                                    st.session_state.part3_current_question = new_question
                                    st.session_state.part3_acknowledgment = ""
                                    st.session_state.part3_conversation_history.append({
                                        'role': 'examiner',
                                        'content': new_question
                                    })
                            
                            reset_silence_timer("part3")  # Reset timer after answer
                            st.rerun()
                        
                        # If answer is irrelevant and first time, send redirect
                        else:
                            # First irrelevant answer - send redirect
                            st.session_state.part3_redirect_count += 1
                            
                            # Add user's off-topic answer to history
                            st.session_state.part3_conversation_history.append({
                                'role': 'user',
                                'content': user_answer
                            })
                            
                            # Generate redirect message
                            with st.spinner("Thinking..."):
                                redirect_message = generate_redirect_message(st.session_state.part3_current_question)
                                
                                # Update current question to be the redirect
                                st.session_state.part3_current_question = redirect_message
                                st.session_state.part3_acknowledgment = ""
                                st.session_state.part3_audio_played_key = None  # Reset audio played tracker
                                
                                # Add redirect to history
                                st.session_state.part3_conversation_history.append({
                                    'role': 'examiner',
                                    'content': redirect_message
                                })
                                
                                reset_silence_timer("part3")  # Reset timer for redirect question
                                st.rerun()
                
                elif st.session_state.test_mode == 'voice':
                    # ===== VOICE MODE FOR PART 3 =====
                    st.write("")
                    st.write("**Time Limit: 60 seconds**")
                    
                    # Auto-play question audio (only once per question)
                    if st.session_state.part3_current_question:
                        # Create unique key for this question combo
                        current_audio_key = f"p3_q{st.session_state.part3_questions_asked}_f{st.session_state.part3_followups_asked}_r{st.session_state.part3_redirect_count}"
                        
                        # Build the full text to speak (acknowledgment + question, like in text mode)
                        text_to_speak = st.session_state.part3_current_question
                        if st.session_state.part3_acknowledgment:
                            text_to_speak = st.session_state.part3_acknowledgment + " " + st.session_state.part3_current_question
                        
                        # Only generate and play audio if we haven't played this specific question yet
                        if st.session_state.part3_audio_played_key != current_audio_key:
                            question_audio_file = text_to_speech(text_to_speak)
                            if question_audio_file:
                                st.audio(question_audio_file, format="audio/mp3", autoplay=True)
                                st.caption("Audio: Question")
                                st.session_state.part3_audio_played_key = current_audio_key
                        else:
                            # Audio already played, show it without autoplay
                            question_audio_file = text_to_speech(text_to_speak)
                            if question_audio_file:
                                st.audio(question_audio_file, format="audio/mp3", autoplay=False)
                                st.caption("Audio: Question")
                    
                    # Voice timer logic (actual limit: 70 seconds, but we tell them 60)
                    if st.session_state.part3_voice_timer_start is not None:
                        expired, elapsed, remaining = check_voice_timer_expired(
                            st.session_state.part3_voice_timer_start,
                            70  # Actual time limit (10s buffer)
                        )
                        
                        # Auto-skip if expired (no countdown shown)
                        if expired:
                            st.warning("Time's up! Moving to next question...")
                            st.session_state.part3_conversation_history.append({
                                'role': 'candidate',
                                'content': '[No response - timed out]'
                            })
                            # Move to next question
                            st.session_state.part3_questions_asked += 1
                            st.session_state.part3_followups_asked = 0
                            st.session_state.part3_first_answer_word_count = 0
                            st.session_state.part3_current_question = ""
                            st.session_state.part3_waiting_for_answer = False
                            st.session_state.part3_redirect_count = 0
                            st.session_state.part3_acknowledgment = ""
                            st.session_state.part3_voice_timer_start = None
                            st.session_state.part3_voice_audio_data = None
                            st.session_state.part3_audio_played_key = None  # Reset audio played tracker
                            st.session_state.part3_transcribed_answer = None  # Clear transcription
                            time.sleep(1)
                            st.rerun()
                    
                    # Audio recording widget - use unique key based on question and redirect to reset widget
                    audio_key = f"part3_q{st.session_state.part3_questions_asked}_f{st.session_state.part3_followups_asked}_r{st.session_state.part3_redirect_count}"
                    audio_input = st.audio_input("Record your answer", key=audio_key)
                    
                    # Start timer when audio widget appears
                    if st.session_state.part3_voice_timer_start is None:
                        st.session_state.part3_voice_timer_start = time.time()
                    
                    # Process audio when user stops recording
                    if audio_input is not None and st.session_state.part3_transcribed_answer is None:
                        # Transcribe the audio (only once) with timestamps
                        with st.spinner("Transcribing your answer..."):
                            result = transcribe_audio(audio_input, include_timestamps=True)
                            user_answer = result['text'] if isinstance(result, dict) else result
                            if user_answer:
                                st.session_state.part3_transcribed_answer = user_answer
                                st.session_state.part3_timing_result = result  # Store for later
                                st.rerun()
                    
                    # Show simple confirmation and submit button if we have a transcribed answer
                    if st.session_state.part3_transcribed_answer:
                        st.success("Answer transcribed successfully")
                        
                        # Submit button
                        if st.button("Submit Answer", key=f"{audio_key}_submit"):
                            user_answer = st.session_state.part3_transcribed_answer
                            
                            # Clear audio data, timer, and transcription
                            st.session_state.part3_voice_timer_start = None
                            st.session_state.part3_voice_audio_data = None
                            st.session_state.part3_transcribed_answer = None
                            
                            # Check word count limit
                            word_count = len(user_answer.split())
                            if word_count > 150:
                                st.error(f"Your answer is {word_count} words. Please record again with 150 words or less.")
                                st.rerun()
                            
                            # Check relevance
                            context = format_conversation_history(st.session_state.part3_conversation_history[-6:])
                            is_relevant, relevance_score = check_relevance(
                                user_answer,
                                st.session_state.part3_current_question,
                                context
                            )
                            
                            # If answer is relevant, process normally
                            if is_relevant or relevance_score >= 0.7:
                                # Add user's answer to history
                                st.session_state.part3_conversation_history.append({
                                    'role': 'user',
                                    'content': user_answer
                                })
                                
                                # Store timing data
                                if st.session_state.get('part3_timing_result'):
                                    store_voice_timing_data('Part 3', st.session_state.part3_current_question, user_answer, st.session_state.part3_timing_result)
                                
                                # Reset redirect count
                                st.session_state.part3_redirect_count = 0
                                
                                # Generate acknowledgment
                                with st.spinner("Thinking..."):
                                        acknowledgment = generate_part3_acknowledgment(
                                            st.session_state.part3_theme,
                                            st.session_state.part3_conversation_history
                                        )
                                        st.session_state.part3_acknowledgment = acknowledgment
                                        
                                        # Word count-based follow-up logic (same as text mode)
                                        if st.session_state.part3_followups_asked == 0:
                                            st.session_state.part3_first_answer_word_count = word_count
                                            
                                            follow_up_question = generate_part3_question(
                                                st.session_state.part3_theme,
                                                st.session_state.part3_questions_asked,
                                                st.session_state.part3_conversation_history,
                                                question_type="followup_question"
                                            )
                                            st.session_state.part3_current_question = follow_up_question
                                            st.session_state.part3_conversation_history.append({
                                                'role': 'examiner',
                                                'content': follow_up_question
                                            })
                                            st.session_state.part3_followups_asked = 1
                                            st.session_state.part3_audio_played_key = None  # Reset audio for new question
                                            st.rerun()
                                        
                                        elif st.session_state.part3_followups_asked == 1:
                                            if st.session_state.part3_first_answer_word_count >= 30:
                                                st.session_state.part3_questions_asked += 1
                                                st.session_state.part3_followups_asked = 0
                                                st.session_state.part3_first_answer_word_count = 0
                                                
                                                if st.session_state.part3_questions_asked >= 3:
                                                    st.session_state.part3_waiting_for_answer = False
                                                    st.session_state.part3_current_question = ""
                                                    st.session_state.part3_completion_message = "Thank you for your responses; that completes the speaking test!"
                                                    st.session_state.part3_showing_completion = True
                                                else:
                                                    new_question = generate_part3_question(
                                                        st.session_state.part3_theme,
                                                        st.session_state.part3_questions_asked,
                                                        st.session_state.part3_conversation_history,
                                                        question_type="main_question"
                                                    )
                                                    st.session_state.part3_current_question = new_question
                                                    st.session_state.part3_conversation_history.append({
                                                        'role': 'examiner',
                                                        'content': new_question
                                                    })
                                                    st.session_state.part3_audio_played_key = None  # Reset audio for new question
                                                    st.rerun()
                                            else:
                                                if word_count >= 20:
                                                    st.session_state.part3_questions_asked += 1
                                                    st.session_state.part3_followups_asked = 0
                                                    st.session_state.part3_first_answer_word_count = 0
                                                    
                                                    if st.session_state.part3_questions_asked >= 3:
                                                        st.session_state.part3_waiting_for_answer = False
                                                        st.session_state.part3_current_question = ""
                                                        st.session_state.part3_completion_message = "Thank you for your responses; that completes the speaking test!"
                                                        st.session_state.part3_showing_completion = True
                                                        st.rerun()
                                                    else:
                                                        new_question = generate_part3_question(
                                                            st.session_state.part3_theme,
                                                            st.session_state.part3_questions_asked,
                                                            st.session_state.part3_conversation_history,
                                                            question_type="main_question"
                                                        )
                                                        st.session_state.part3_current_question = new_question
                                                        st.session_state.part3_conversation_history.append({
                                                            'role': 'examiner',
                                                            'content': new_question
                                                        })
                                                        st.session_state.part3_audio_played_key = None  # Reset audio for new question
                                                        st.rerun()
                                                else:
                                                    follow_up_question = generate_part3_question(
                                                        st.session_state.part3_theme,
                                                        st.session_state.part3_questions_asked,
                                                        st.session_state.part3_conversation_history,
                                                        question_type="followup_question"
                                                    )
                                                    st.session_state.part3_current_question = follow_up_question
                                                    st.session_state.part3_conversation_history.append({
                                                        'role': 'examiner',
                                                        'content': follow_up_question
                                                    })
                                                    st.session_state.part3_followups_asked = 2
                                                    st.session_state.part3_audio_played_key = None  # Reset audio for new question
                                                    st.rerun()
                                        
                                        else:  # followups_asked == 2
                                            st.session_state.part3_questions_asked += 1
                                            st.session_state.part3_followups_asked = 0
                                            st.session_state.part3_first_answer_word_count = 0
                                            
                                            if st.session_state.part3_questions_asked >= 3:
                                                st.session_state.part3_waiting_for_answer = False
                                                st.session_state.part3_current_question = ""
                                                st.session_state.part3_completion_message = "Thank you for your responses; that completes the speaking test!"
                                                st.session_state.part3_showing_completion = True
                                                st.rerun()
                                            else:
                                                new_question = generate_part3_question(
                                                    st.session_state.part3_theme,
                                                    st.session_state.part3_questions_asked,
                                                    st.session_state.part3_conversation_history,
                                                    question_type="main_question"
                                                )
                                                st.session_state.part3_current_question = new_question
                                                st.session_state.part3_conversation_history.append({
                                                    'role': 'examiner',
                                                    'content': new_question
                                                })
                                        
                                                # Clear transcription and audio for next question
                                                st.session_state.part3_transcribed_answer = None
                                                st.session_state.part3_audio_played_key = None
                                                st.rerun()
                            
                            # If answer is irrelevant and we've already redirected once, move on
                            elif st.session_state.part3_redirect_count >= 1:
                                st.session_state.part3_conversation_history.append({
                                    'role': 'user',
                                    'content': user_answer
                                })
                                
                                # Store timing data (even for irrelevant)
                                if st.session_state.get('part3_timing_result'):
                                    store_voice_timing_data('Part 3 (Irrelevant)', st.session_state.part3_current_question, user_answer, st.session_state.part3_timing_result)
                                
                                st.session_state.part3_conversation_history.append({
                                    'role': 'examiner',
                                    'content': "Thank you. Let's move on."
                                })
                                
                                st.session_state.part3_redirect_count = 0
                                st.session_state.part3_questions_asked += 1
                                st.session_state.part3_followups_asked = 0
                                st.session_state.part3_first_answer_word_count = 0
                                
                                if st.session_state.part3_questions_asked >= 3:
                                    st.session_state.part3_waiting_for_answer = False
                                    st.session_state.part3_current_question = ""
                                    st.session_state.part3_completion_message = "Thank you for your responses; that completes the speaking test!"
                                    st.session_state.part3_showing_completion = True
                                    st.rerun()
                                else:
                                    with st.spinner("Thinking of a question..."):
                                        new_question = generate_part3_question(
                                            st.session_state.part3_theme,
                                            st.session_state.part3_questions_asked,
                                            st.session_state.part3_conversation_history,
                                            question_type="main_question"
                                        )
                                        st.session_state.part3_current_question = new_question
                                        st.session_state.part3_acknowledgment = ""
                                        st.session_state.part3_conversation_history.append({
                                            'role': 'examiner',
                                            'content': new_question
                                        })
                                
                                # Clear transcription and audio for next question
                                st.session_state.part3_transcribed_answer = None
                                st.session_state.part3_audio_played_key = None
                                st.rerun()
                            
                            # If answer is irrelevant and first time, send redirect
                            else:
                                st.session_state.part3_redirect_count += 1
                                
                                st.session_state.part3_conversation_history.append({
                                    'role': 'user',
                                    'content': user_answer
                                })
                                
                                # Store timing data (even for irrelevant first answer)
                                if st.session_state.get('part3_timing_result'):
                                    store_voice_timing_data('Part 3 (Irrelevant - 1st attempt)', st.session_state.part3_current_question, user_answer, st.session_state.part3_timing_result)
                                
                                with st.spinner("Thinking..."):
                                    redirect_message = generate_redirect_message(st.session_state.part3_current_question)
                                    
                                    st.session_state.part3_current_question = redirect_message
                                    st.session_state.part3_acknowledgment = ""
                                    st.session_state.part3_audio_played_key = None  # Reset audio played tracker
                                    st.session_state.part3_transcribed_answer = None  # Clear transcription
                                    
                                    st.session_state.part3_conversation_history.append({
                                        'role': 'examiner',
                                        'content': redirect_message
                                    })
                                    
                                    st.rerun()
                    
                    # Auto-refresh after 70 seconds to check for timeout
                    if st.session_state.part3_voice_timer_start is not None and audio_input is None:
                        st_autorefresh(interval=70000, key="part3_voice_timer")
    
    elif st.session_state.step == "SCORING":
        st.write("# Your Speaking Assessment Results")
        st.write("---")
        
        # Display Full Conversation History (for debugging/verification)
        with st.expander("View Full Conversation History", expanded=False):
            st.write("### Part 1: The Interview")
            if st.session_state.get('part1_conversation_history'):
                for entry in st.session_state.part1_conversation_history:
                    if entry['role'] == 'examiner':
                        st.write(f"**Examiner:** {entry['content']}")
                    elif entry['role'] in ['user', 'candidate']:
                        st.write(f"**You:** {entry['content']}")
                    st.write("")
            else:
                st.write("*No Part 1 conversation data*")
            
            st.write("---")
            st.write("### Part 2: The Long Turn")
            if st.session_state.get('part2_conversation_history'):
                for entry in st.session_state.part2_conversation_history:
                    if entry['role'] == 'examiner':
                        st.write(f"**Examiner:** {entry['content']}")
                    elif entry['role'] in ['user', 'candidate']:
                        st.write(f"**You:** {entry['content']}")
                    st.write("")
            else:
                st.write("*No Part 2 conversation data*")
            
            st.write("---")
            st.write("### Part 3: Discussion")
            if st.session_state.get('part3_conversation_history'):
                for entry in st.session_state.part3_conversation_history:
                    if entry['role'] == 'examiner':
                        st.write(f"**Examiner:** {entry['content']}")
                    elif entry['role'] in ['user', 'candidate']:
                        st.write(f"**You:** {entry['content']}")
                    st.write("")
            else:
                st.write("*No Part 3 conversation data*")
        
        st.write("")
        st.write("---")
        
        # Calculate and cache scores on first render
        if 'calculated_scores' not in st.session_state:
            with st.spinner("Analyzing your performance... This may take 10-15 seconds."):
                # Gather all data
                part1_hist = st.session_state.get('part1_conversation_history', [])
                part2_hist = st.session_state.get('part2_conversation_history', [])
                part3_hist = st.session_state.get('part3_conversation_history', [])
                voice_data = st.session_state.get('voice_timing_data', [])
                test_mode = st.session_state.get('test_mode', 'text')
                
                # Generate metrics
                metrics = generate_metrics_summary(
                    part1_hist, 
                    part2_hist, 
                    part3_hist, 
                    voice_data, 
                    test_mode
                )
                
                # Score the test with GPT
                scores = score_speaking_test(
                    part1_hist,
                    part2_hist,
                    part3_hist,
                    metrics,
                    test_mode
                )
                
                st.session_state.calculated_scores = scores
        
        # Display scores
        scores = st.session_state.calculated_scores
        
        # Overall Score Display (prominent)
        st.write("## Your IELTS Speaking Band Score")
        
        # Large, prominent display of final band
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            st.markdown(f"<h1 style='text-align: center; color: #1f77b4;'>{scores['final_band']}</h1>", unsafe_allow_html=True)
        
        cefr_level = scores['cefr_level']
        cefr_description = get_cefr_description(cefr_level)
        st.info(f"**CEFR Level:** {cefr_level} - {cefr_description}")
        st.write(scores.get('overall_feedback', ''))
        
        st.write("")
        st.write("---")
        
        # Detailed Criterion Scores
        st.write("## Detailed Score Breakdown")
        st.write("")
        
        criterion_info = [
            ('fluency_coherence', 'Fluency & Coherence', 25),
            ('lexical_resource', 'Lexical Resource (Vocabulary)', 20),
            ('grammatical_range', 'Grammatical Range & Accuracy', 20),
            ('coherence_cohesion', 'Coherence & Cohesion', 15),
            ('task_achievement', 'Task Achievement', 20)
        ]
        
        for key, name, weight in criterion_info:
            score_data = scores['scores'].get(key, {})
            score = score_data.get('score', 0)
            justification = score_data.get('justification', 'No assessment available')
            
            with st.expander(f"{score}/9 - {name} ({weight}% weight)", expanded=False):
                st.write(f"**Score:** {score} / 9.0")
                st.write(f"**Weight:** {weight}% of total score")
                st.write("")
                st.write(f"**Assessment:**")
                st.write(justification)
                
                # Additional details if available
                if key == 'lexical_resource' and score_data.get('notable_vocabulary'):
                    st.write("")
                    st.write("**Notable Vocabulary:**")
                    st.write(", ".join(score_data['notable_vocabulary']))
                
                if key == 'grammatical_range' and score_data.get('complex_attempts'):
                    st.write("")
                    st.write("**Complex Structures Attempted:**")
                    for attempt in score_data['complex_attempts']:
                        st.write(f"- {attempt}")
                
                if key == 'coherence_cohesion' and score_data.get('cohesive_devices_used'):
                    st.write("")
                    st.write("**Cohesive Devices Used:**")
                    st.write(", ".join(score_data['cohesive_devices_used']))
                
                if key == 'task_achievement':
                    st.write("")
                    base_score = score_data.get('base_score_before_penalties', score)
                    penalties = score_data.get('penalties_applied', 0)
                    if penalties > 0:
                        st.write(f"**Base score:** {base_score}")
                        st.write(f"**Penalties:** -{penalties}")
                        st.write(f"**Final score:** {score}")
        
        st.write("")
        st.write("---")
        
        # Strengths and Areas for Improvement
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Your Strengths")
            strengths = scores.get('strengths', [])
            if strengths:
                for strength in strengths:
                    st.write(f"- {strength}")
            else:
                st.write("*No strengths identified*")
        
        with col2:
            st.write("### Areas for Improvement")
            improvements = scores.get('areas_for_improvement', [])
            if improvements:
                for improvement in improvements:
                    st.write(f"- {improvement}")
            else:
                st.write("*No specific areas identified*")
        
        st.write("")
        st.write("---")
        
        # CEFR Levels Explanation
        st.write("## Understanding CEFR Levels")
        st.write("""
The **Common European Framework of Reference (CEFR)** is an international standard for describing language ability. Here's what each level means:
        """)
        
        # Create columns for better layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**A1 - Beginner**")
            st.write("Can understand and use familiar everyday expressions and very basic phrases.")
            st.write("")
            
            st.write("**A2 - Elementary**")
            st.write("Can communicate in simple and routine tasks requiring a direct exchange of information.")
            st.write("")
            
            st.write("**B1 - Intermediate**")
            st.write("Can deal with most situations likely to arise whilst travelling. Can describe experiences, events, dreams, hopes and ambitions.")
        
        with col2:
            st.write("**B2 - Upper Intermediate**")
            st.write("Can interact with a degree of fluency and spontaneity. Can produce clear, detailed text on a wide range of subjects.")
            st.write("")
            
            st.write("**C1 - Advanced**")
            st.write("Can express ideas fluently and spontaneously. Can use language flexibly and effectively for social, academic and professional purposes.")
            st.write("")
            
            st.write("**C2 - Proficiency**")
            st.write("Can understand with ease virtually everything heard or read. Can express themselves spontaneously, very fluently and precisely.")
        
        st.write("")
        st.write("---")
        
        # Tips for Improvement Section
        st.write("## Tips for Improvement")
        st.write("""
Here are evidence-based strategies to help you improve your speaking skills:
        """)
        
        st.write("### Delivery & Fluency")
        st.write("""
- **Pacing + Clarity:** Don't speak too fast or too slow; aim for balance and intelligibility
- **Reduce Filler Words:** Minimize "um," "like," "you know" — replace with a short silent pause or a neutral phrase like "That's interesting—let me think…"
- **Thinking Time is Allowed:** You can pause briefly, ask to repeat the question, or use stalling phrases if needed
        """)
        
        st.write("### Content & Relevance")
        st.write("""
- **Stay On-Topic:** Actually answer the question asked — more words don't help if you drift
- **Avoid Memorized Answers:** Sound natural and engaged rather than using "ready-made" responses
- **Don't Use Unfamiliar Big Words:** Accuracy and appropriateness matter more than impressive vocabulary
        """)
        
        st.write("### Practice Methods")
        st.write("""
- **Do Sample Questions:** Practice with real IELTS-style prompts regularly
- **Speak Daily:** Find opportunities to speak English every day, even if just to yourself
- **Listen & Read Aloud:** Expose yourself to natural English and practice pronunciation
- **Think in English:** Try to formulate thoughts in English rather than translating
- **Record Yourself:** Listen back to identify areas for improvement
- **Learn Phrases (Chunks):** Focus on learning common phrases, not just individual words
- **Act Confident:** Confidence helps fluency — don't be afraid to make mistakes
        """)
        
        st.write("")
        st.write("---")
        
        # Additional Resources
        st.write("## Additional Resources")
        st.write("""
For more comprehensive IELTS Speaking tips and practice strategies, visit:
        """)
        st.markdown("[**IELTS Speaking Tips: Complete Guide**](https://global-exam.com/blog/en/ielts-speaking-tips-all-you-need-to-prepare-for-the-oral-test/)")
        
        st.write("")
        st.write("---")
        
        # Option to retake
        if st.button("Take Test Again"):
                # Reset all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    
    # Auto-refresh for silence detection - interval matches check-in time for each part
    # This minimizes form interference while ensuring precise timing
    refresh_interval = None
    
    if st.session_state.step == "PART_1" and st.session_state.get('part1_waiting_for_answer', False):
        refresh_interval = 30000  # 30 seconds for Part 1
    elif st.session_state.step == "PART_2" and st.session_state.get('part2_prep_complete', False) and not st.session_state.get('part2_long_response', ''):
        refresh_interval = 60000  # 60 seconds for Part 2 long response
    elif st.session_state.step == "PART_2" and st.session_state.get('part2_waiting_for_rounding_answer', False):
        refresh_interval = 30000  # 30 seconds for Part 2 rounding-off
    elif st.session_state.step == "PART_3" and st.session_state.get('part3_waiting_for_answer', False):
        refresh_interval = 40000  # 40 seconds for Part 3
    
    if refresh_interval:
        st_autorefresh(interval=refresh_interval, key="silence_timer_refresh")

if __name__ == "__main__":
    main()