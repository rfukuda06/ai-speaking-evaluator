"""
Session state management and initialization functions.
"""

import streamlit as st
import random
import time
from config import PART1_TOPICS, PART2_CATEGORIES
from llm_functions import generate_part2_prompt_card, extract_theme_from_part2


def initialize_part1():
    """Select 3 random topics and set up Part 1"""
    if not st.session_state.part1_initialized:
        # Randomly select 3 topics
        st.session_state.part1_topics = random.sample(PART1_TOPICS, 3)
        # Randomly assign 2 or 3 questions for each topic (50/50 chance)
        st.session_state.part1_questions_per_topic = [random.choice([2, 3]) for _ in range(3)]
        st.session_state.part1_initialized = True
        st.session_state.part1_current_topic_index = 0
        st.session_state.part1_questions_asked = 0
        st.session_state.part1_conversation_history = []
        st.session_state.part1_waiting_for_answer = False
        st.session_state.part1_current_question = ""


def initialize_part2():
    """Initialize Part 2: select category and generate prompt card"""
    if not st.session_state.part2_initialized:
        # Randomly select one category
        st.session_state.part2_category = random.choice(PART2_CATEGORIES)
        
        # Generate prompt card with GPT
        with st.spinner("Generating your prompt card..."):
            prompt_card = generate_part2_prompt_card(st.session_state.part2_category)
            st.session_state.part2_prompt_card = prompt_card
        
        st.session_state.part2_initialized = True
        st.session_state.part2_prep_start_time = None  # Will be set after intro (voice) or immediately (text)
        st.session_state.part2_prep_elapsed = 0
        st.session_state.part2_prep_complete = False
        st.session_state.part2_long_response = ""
        st.session_state.part2_rounding_off_questions = []
        st.session_state.part2_rounding_question_index = 0
        st.session_state.part2_rounding_questions_answered = 0
        st.session_state.part2_waiting_for_rounding_answer = False
        st.session_state.part2_conversation_history = []
        st.session_state.part2_long_response_redirect_count = 0
        st.session_state.part2_rounding_redirect_count = 0
        st.session_state.part2_long_response_redirect_message = ""
        st.session_state.part2_instruction_audio_played = False
        st.session_state.part2_rounding_audio_played_key = None  # Track audio playback for rounding questions
        # For voice mode: show intro page first, for text mode: go straight to prep
        if st.session_state.test_mode == 'voice':
            st.session_state.part2_showing_intro = True
            st.session_state.part2_intro_start_time = time.time()
        else:
            st.session_state.part2_showing_intro = False
            st.session_state.part2_prep_start_time = time.time()


def initialize_part3():
    """Initialize Part 3: Extract theme from Part 2 and set up the discussion"""
    if not st.session_state.part3_initialized:
        # Extract theme from Part 2's prompt
        part2_prompt = st.session_state.part2_prompt_card.get('main_prompt', '')
        
        # If Part 2 wasn't completed (e.g., user skipped directly to Part 3), use a default
        if not part2_prompt:
            st.warning("Part 2 was not completed. Using a default theme for testing.")
            st.session_state.part3_theme = "general life experiences"
        else:
            st.session_state.part3_theme = extract_theme_from_part2(part2_prompt)
        
        # Reset Part 3 state
        st.session_state.part3_initialized = True
        st.session_state.part3_questions_asked = 0
        st.session_state.part3_followups_asked = 0
        st.session_state.part3_first_answer_word_count = 0
        st.session_state.part3_conversation_history = []
        st.session_state.part3_waiting_for_answer = False
        st.session_state.part3_current_question = ""
        st.session_state.part3_redirect_count = 0
        st.session_state.part3_acknowledgment = ""
