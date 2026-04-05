"""
Session state management and initialization functions.
"""

import random
import time
from config import PART1_TOPICS, PART2_CATEGORIES
from llm_functions import generate_part2_prompt_card, extract_theme_from_part2


def initialize_part1(session):
    """Select 3 random topics and set up Part 1

    Args:
        session: Session dict (replaces st.session_state)
    """
    if not session.get('part1_initialized'):
        # Randomly select 3 topics
        session['part1_topics'] = random.sample(PART1_TOPICS, 3)
        # 2 questions per topic
        session['part1_questions_per_topic'] = [2, 2, 2]
        session['part1_initialized'] = True
        session['part1_current_topic_index'] = 0
        session['part1_questions_asked'] = 0
        session['part1_conversation_history'] = []
        session['part1_waiting_for_answer'] = False
        session['part1_current_question'] = ""


def initialize_part2(session):
    """Initialize Part 2: select category and generate prompt card

    Args:
        session: Session dict (replaces st.session_state)
    """
    if not session.get('part2_initialized'):
        # Randomly select one category
        session['part2_category'] = random.choice(PART2_CATEGORIES)

        # Generate prompt card with GPT
        prompt_card = generate_part2_prompt_card(session['part2_category'])
        session['part2_prompt_card'] = prompt_card

        session['part2_initialized'] = True
        session['part2_prep_start_time'] = None
        session['part2_prep_elapsed'] = 0
        session['part2_prep_complete'] = False
        session['part2_long_response'] = ""
        session['part2_rounding_off_questions'] = []
        session['part2_rounding_question_index'] = 0
        session['part2_rounding_questions_answered'] = 0
        session['part2_waiting_for_rounding_answer'] = False
        session['part2_conversation_history'] = []
        session['part2_long_response_redirect_count'] = 0
        session['part2_rounding_redirect_count'] = 0
        session['part2_long_response_redirect_message'] = ""
        session['part2_instruction_audio_played'] = False
        session['part2_rounding_audio_played_key'] = None
        # For voice mode: show intro page first, for text mode: go straight to prep
        if session.get('test_mode') == 'voice':
            session['part2_showing_intro'] = True
            session['part2_intro_start_time'] = time.time()
        else:
            session['part2_showing_intro'] = False
            session['part2_prep_start_time'] = time.time()


def initialize_part3(session):
    """Initialize Part 3: Extract theme from Part 2 and set up the discussion

    Args:
        session: Session dict (replaces st.session_state)
    """
    if not session.get('part3_initialized'):
        # Extract theme from Part 2's prompt
        part2_prompt = session.get('part2_prompt_card', {}).get('main_prompt', '')

        # If Part 2 wasn't completed, use a default
        if not part2_prompt:
            session['part3_theme'] = "general life experiences"
        else:
            session['part3_theme'] = extract_theme_from_part2(part2_prompt)

        # Reset Part 3 state
        session['part3_initialized'] = True
        session['part3_questions_asked'] = 0
        session['part3_followups_asked'] = 0
        session['part3_first_answer_word_count'] = 0
        session['part3_conversation_history'] = []
        session['part3_waiting_for_answer'] = False
        session['part3_current_question'] = ""
        session['part3_redirect_count'] = 0
        session['part3_acknowledgment'] = ""
