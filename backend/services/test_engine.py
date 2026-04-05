"""
Test engine — the core state machine extracted from app.py.
All business logic for Part 1, Part 2, Part 3, and Scoring lives here.
UI rendering is handled entirely by the frontend.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import RELEVANCE_THRESHOLD
from llm_functions import (
    get_examiner_prompt, get_examiner_prompt_part2, get_examiner_prompt_part3,
    get_examiner_response, check_relevance, generate_redirect_message,
    generate_rounding_off_questions, generate_part3_question, generate_part3_acknowledgment
)
from state_management import initialize_part1, initialize_part2, initialize_part3
from utils import generate_part_completion_message, reset_silence_timer
from voice_functions import store_voice_timing_data
from scoring import generate_metrics_summary, score_speaking_test


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_context(history, n=4):
    """Get last n exchanges as context string."""
    if not history:
        return ""
    recent = history[-n:]
    return " ".join(e['content'] for e in recent)


def _build_progress(session):
    """Build progress info for Part 1."""
    total = sum(session.get('part1_questions_per_topic', []))
    idx = session.get('part1_current_topic_index', 0)
    qpt = session.get('part1_questions_per_topic', [])
    prev = sum(qpt[:idx]) if idx < len(qpt) else total
    current = prev + session.get('part1_questions_asked', 0)
    pct = min((current / total) * 100, 100) if total > 0 else 0
    return {
        'current': min(current, total),
        'total': total,
        'percent': round(pct, 1)
    }


# ---------------------------------------------------------------------------
# Start test
# ---------------------------------------------------------------------------

def start_test(session, mode):
    """Set mode, initialize Part 1, return initial state."""
    session['test_mode'] = mode
    session['step'] = 'PART_1'
    initialize_part1(session)
    return generate_next_question_part1(session)


# ---------------------------------------------------------------------------
# PART 1
# ---------------------------------------------------------------------------

def generate_next_question_part1(session):
    """Generate the next Part 1 question (or detect completion)."""
    topics = session.get('part1_topics', [])
    idx = session.get('part1_current_topic_index', 0)
    qpt = session.get('part1_questions_per_topic', [])

    # Check if all topics are done
    if idx >= len(topics):
        msg = generate_part_completion_message(1, session.get('part1_conversation_history', []))
        session['part1_completion_message'] = msg
        session['part1_showing_completion'] = True
        return _part1_state(session, sub_state='part_complete')

    topic = topics[idx]
    asked = session.get('part1_questions_asked', 0)
    target = qpt[idx] if idx < len(qpt) else 2

    # If we've asked enough for current topic, advance
    if asked >= target:
        session['part1_current_topic_index'] = idx + 1
        session['part1_questions_asked'] = 0
        session['part1_redirect_count'] = 0
        session['part1_should_build_off'] = False
        session['part1_last_relevant_answer'] = ""
        return generate_next_question_part1(session)

    # Generate question via GPT
    history = session.get('part1_conversation_history', [])
    should_build = session.get('part1_should_build_off', False)
    last_answer = session.get('part1_last_relevant_answer', "")

    system_prompt = get_examiner_prompt(
        topic, asked, history
    )

    if should_build and last_answer:
        system_prompt += f"\n\nThe candidate just said: \"{last_answer[:200]}\". Briefly acknowledge what they said (1 short sentence) then ask your next question about {topic} that naturally connects to their response."

    # After a failed redirect, explicitly instruct GPT to ask a completely different question
    if session.pop('_skip_repeated_question', False):
        system_prompt += f"\n\nIMPORTANT: The candidate just gave irrelevant answers to the previous question. You MUST ask a completely DIFFERENT question about {topic}. Do NOT repeat or rephrase any question you already asked."

    question = get_examiner_response(system_prompt, history)

    session['part1_current_question'] = question
    session['part1_waiting_for_answer'] = True
    session['part1_questions_asked'] = asked + 1
    session['part1_redirect_count'] = 0
    reset_silence_timer(session, 'part1')

    # Add to history
    history.append({'role': 'examiner', 'content': question})
    session['part1_conversation_history'] = history

    return _part1_state(session, sub_state='waiting_for_answer')


def submit_answer_part1(session, answer):
    """Process a Part 1 answer (text or transcribed voice)."""
    # Trim to 65 words max
    words = answer.split()
    if len(words) > 65:
        answer = ' '.join(words[:65])

    question = session.get('part1_current_question', '')
    history = session.get('part1_conversation_history', [])
    context = _get_context(history)

    is_relevant, relevance_score = check_relevance(answer, question, context)
    relevant = is_relevant or relevance_score >= RELEVANCE_THRESHOLD

    if relevant:
        return _handle_relevant_part1(session, answer)
    elif session.get('part1_redirect_count', 0) >= 1:
        return _handle_second_irrelevant_part1(session, answer)
    else:
        return _handle_first_irrelevant_part1(session, answer)


def _handle_relevant_part1(session, answer):
    history = session.get('part1_conversation_history', [])
    history.append({'role': 'user', 'content': answer})
    session['part1_conversation_history'] = history
    session['part1_redirect_count'] = 0

    # Generate acknowledgment
    ack = _generate_acknowledgment(answer, session['part1_current_question'])
    session['part1_acknowledgment'] = ack

    # Determine if we should build off this answer for next question
    idx = session.get('part1_current_topic_index', 0)
    qpt = session.get('part1_questions_per_topic', [])
    asked = session.get('part1_questions_asked', 0)
    target = qpt[idx] if idx < len(qpt) else 2

    if asked < target:
        session['part1_should_build_off'] = True
        session['part1_last_relevant_answer'] = answer
    else:
        session['part1_should_build_off'] = False

    session['part1_waiting_for_answer'] = False
    session['part1_current_question'] = ""

    # Generate next question (or complete topic/part)
    return generate_next_question_part1(session)


def _handle_second_irrelevant_part1(session, answer):
    history = session.get('part1_conversation_history', [])
    history.append({'role': 'user', 'content': answer})
    history.append({'role': 'examiner', 'content': "Thank you. Let's move on."})
    session['part1_conversation_history'] = history
    session['part1_redirect_count'] = 0
    session['part1_current_question'] = ""
    session['part1_should_build_off'] = False
    session['part1_waiting_for_answer'] = False
    # Flag so the next question generation knows to ask something different
    session['_skip_repeated_question'] = True

    return generate_next_question_part1(session)


def _handle_first_irrelevant_part1(session, answer):
    history = session.get('part1_conversation_history', [])
    history.append({'role': 'user', 'content': answer})

    question = session.get('part1_current_question', '')
    redirect = generate_redirect_message(question)

    history.append({'role': 'examiner', 'content': redirect})
    session['part1_conversation_history'] = history
    session['part1_current_question'] = redirect
    session['part1_redirect_count'] = 1
    session['part1_waiting_for_answer'] = True

    return _part1_state(session, sub_state='waiting_for_answer', is_redirect=True)


def skip_answer_part1(session):
    """Handle timeout / no response for Part 1."""
    history = session.get('part1_conversation_history', [])
    history.append({'role': 'user', 'content': '[No response - timed out]'})
    session['part1_conversation_history'] = history
    session['part1_waiting_for_answer'] = False
    session['part1_current_question'] = ""
    session['part1_should_build_off'] = False
    session['_skip_repeated_question'] = True

    return generate_next_question_part1(session)


def _part1_state(session, sub_state='waiting_for_answer', is_redirect=False):
    topics = session.get('part1_topics', [])
    idx = session.get('part1_current_topic_index', 0)
    topic = topics[idx] if idx < len(topics) else ''

    return {
        'step': 'PART_1',
        'sub_state': sub_state,
        'question': session.get('part1_current_question', ''),
        'acknowledgment': session.get('part1_acknowledgment', ''),
        'is_redirect': is_redirect,
        'is_part_complete': session.get('part1_showing_completion', False),
        'completion_message': session.get('part1_completion_message', ''),
        'progress': _build_progress(session),
        'topic': topic,
        'time_limit': 30,
        'test_mode': session.get('test_mode'),
    }


# ---------------------------------------------------------------------------
# PART 2
# ---------------------------------------------------------------------------

def start_part2(session):
    """Initialize Part 2 and return initial state."""
    initialize_part2(session)
    return _part2_state(session, sub_state='prep')


def skip_prep(session):
    """Skip Part 2 preparation phase."""
    session['part2_prep_complete'] = True
    reset_silence_timer(session, 'part2_long')
    return _part2_state(session, sub_state='long_response')


def complete_prep(session):
    """Mark prep as complete (timer expired)."""
    session['part2_prep_complete'] = True
    reset_silence_timer(session, 'part2_long')
    return _part2_state(session, sub_state='long_response')


def submit_long_response(session, answer):
    """Process the Part 2 long response."""
    words = answer.split()
    if len(words) > 400:
        answer = ' '.join(words[:400])

    prompt_card = session.get('part2_prompt_card', {})
    main_prompt = prompt_card.get('main_prompt', '')
    bullets = prompt_card.get('bullet_points', [])
    context = f"{main_prompt} Points to cover: {', '.join(bullets)}" if bullets else main_prompt

    is_relevant, relevance_score = check_relevance(answer, main_prompt, context)
    relevant = is_relevant or relevance_score >= RELEVANCE_THRESHOLD
    redirect_count = session.get('part2_long_response_redirect_count', 0)

    if redirect_count >= 1 and not relevant:
        return _handle_long_response_second_irrelevant(session, answer)
    elif redirect_count >= 1 and relevant:
        return _handle_long_response_relevant(session, answer)
    elif not relevant:
        return _handle_long_response_first_irrelevant(session, answer)
    else:
        return _handle_long_response_relevant(session, answer)


def _handle_long_response_relevant(session, answer):
    history = session.get('part2_conversation_history', [])
    history.append({'role': 'user', 'content': answer})
    session['part2_long_response'] = answer
    session['part2_long_response_redirect_message'] = ""

    # Generate acknowledgment
    system = get_examiner_prompt_part2(history, phase="long_response")
    ack = get_examiner_response(system, history)
    session['part2_long_response_acknowledgment'] = ack
    history.append({'role': 'examiner', 'content': ack})
    session['part2_conversation_history'] = history

    # Generate rounding-off questions
    main_prompt = session.get('part2_prompt_card', {}).get('main_prompt', '')
    rounding_qs = generate_rounding_off_questions(answer, main_prompt)
    session['part2_rounding_off_questions'] = rounding_qs
    session['part2_rounding_question_index'] = 0
    session['part2_rounding_questions_answered'] = 0

    return _part2_state(session, sub_state='rounding')


def _handle_long_response_second_irrelevant(session, answer):
    history = session.get('part2_conversation_history', [])
    history.append({'role': 'user', 'content': answer})
    history.append({'role': 'examiner', 'content': "Thank you. Let's move on to the next part."})
    session['part2_conversation_history'] = history
    session['part2_long_response'] = answer

    msg = generate_part_completion_message(2, history)
    session['part2_completion_message'] = msg
    session['part2_showing_completion'] = True
    return _part2_state(session, sub_state='part_complete')


def _handle_long_response_first_irrelevant(session, answer):
    history = session.get('part2_conversation_history', [])
    history.append({'role': 'user', 'content': answer})

    main_prompt = session.get('part2_prompt_card', {}).get('main_prompt', '')
    redirect = generate_redirect_message(main_prompt)
    history.append({'role': 'examiner', 'content': redirect})

    session['part2_conversation_history'] = history
    session['part2_long_response_redirect_count'] = 1
    session['part2_long_response_redirect_message'] = redirect

    return _part2_state(session, sub_state='long_response', is_redirect=True)


def get_current_rounding_question(session):
    """Get the current rounding-off question and add to history if needed."""
    qs = session.get('part2_rounding_off_questions', [])
    idx = session.get('part2_rounding_question_index', 0)
    answered = session.get('part2_rounding_questions_answered', 0)

    if answered >= 2 or idx >= len(qs):
        msg = generate_part_completion_message(2, session.get('part2_conversation_history', []))
        session['part2_completion_message'] = msg
        session['part2_showing_completion'] = True
        return _part2_state(session, sub_state='part_complete')

    question = qs[idx]
    history = session.get('part2_conversation_history', [])

    # Only add to history if not already the last examiner message
    if not history or history[-1].get('content') != question:
        history.append({'role': 'examiner', 'content': question})
        session['part2_conversation_history'] = history

    session['part2_current_rounding_question'] = question
    session['part2_waiting_for_rounding_answer'] = True
    session['part2_rounding_redirect_count'] = 0
    reset_silence_timer(session, 'part2_rounding')

    return _part2_state(session, sub_state='rounding')


def submit_rounding_answer(session, answer):
    """Process a Part 2 rounding-off answer."""
    words = answer.split()
    if len(words) > 65:
        answer = ' '.join(words[:65])

    question = session.get('part2_current_rounding_question', '')
    history = session.get('part2_conversation_history', [])
    context = _get_context(history)
    redirect_count = session.get('part2_rounding_redirect_count', 0)

    if redirect_count >= 1:
        # Already redirected — accept and move on
        history.append({'role': 'user', 'content': answer})
        history.append({'role': 'examiner', 'content': "Thank you. Let's move on."})
        session['part2_conversation_history'] = history
        session['part2_rounding_questions_answered'] = session.get('part2_rounding_questions_answered', 0) + 1
        session['part2_rounding_question_index'] = session.get('part2_rounding_question_index', 0) + 1
        session['part2_waiting_for_rounding_answer'] = False
        return get_current_rounding_question(session)

    is_relevant, relevance_score = check_relevance(answer, question, context)
    relevant = is_relevant or relevance_score >= RELEVANCE_THRESHOLD

    if not relevant:
        history.append({'role': 'user', 'content': answer})
        redirect = generate_redirect_message(question)
        history.append({'role': 'examiner', 'content': redirect})
        session['part2_conversation_history'] = history
        session['part2_current_rounding_question'] = redirect
        session['part2_rounding_redirect_count'] = 1
        return _part2_state(session, sub_state='rounding', is_redirect=True)

    # Relevant
    history.append({'role': 'user', 'content': answer})

    # Generate acknowledgment
    ack = _generate_acknowledgment(answer, question)
    history.append({'role': 'examiner', 'content': ack})
    session['part2_rounding_acknowledgment'] = ack
    session['part2_conversation_history'] = history

    session['part2_rounding_questions_answered'] = session.get('part2_rounding_questions_answered', 0) + 1
    session['part2_rounding_question_index'] = session.get('part2_rounding_question_index', 0) + 1
    session['part2_waiting_for_rounding_answer'] = False

    return get_current_rounding_question(session)


def skip_answer_part2(session, phase):
    """Handle timeout for Part 2 (long_response or rounding)."""
    history = session.get('part2_conversation_history', [])
    history.append({'role': 'user', 'content': '[No response - timed out]'})
    session['part2_conversation_history'] = history

    if phase == 'long_response':
        session['part2_long_response'] = '[No response - timed out]'
        msg = generate_part_completion_message(2, history)
        session['part2_completion_message'] = msg
        session['part2_showing_completion'] = True
        return _part2_state(session, sub_state='part_complete')
    else:
        session['part2_rounding_questions_answered'] = session.get('part2_rounding_questions_answered', 0) + 1
        session['part2_rounding_question_index'] = session.get('part2_rounding_question_index', 0) + 1
        session['part2_waiting_for_rounding_answer'] = False
        return get_current_rounding_question(session)


def _part2_state(session, sub_state='prep', is_redirect=False):
    prompt_card = session.get('part2_prompt_card', {})
    answered = session.get('part2_rounding_questions_answered', 0)

    return {
        'step': 'PART_2',
        'sub_state': sub_state,
        'question': session.get('part2_current_rounding_question', ''),
        'acknowledgment': session.get('part2_rounding_acknowledgment', '') if sub_state == 'rounding' else session.get('part2_long_response_acknowledgment', ''),
        'is_redirect': is_redirect,
        'redirect_message': session.get('part2_long_response_redirect_message', '') if sub_state == 'long_response' else '',
        'is_part_complete': session.get('part2_showing_completion', False),
        'completion_message': session.get('part2_completion_message', ''),
        'prompt_card': prompt_card,
        'rounding_progress': {'current': answered, 'total': 2},
        'time_limit': 120 if sub_state == 'long_response' else 30,
        'test_mode': session.get('test_mode'),
    }


# ---------------------------------------------------------------------------
# PART 3
# ---------------------------------------------------------------------------

def start_part3(session):
    """Initialize Part 3 and generate first question."""
    initialize_part3(session)
    return generate_next_question_part3(session)


def generate_next_question_part3(session):
    """Generate the next Part 3 question (main or follow-up)."""
    asked = session.get('part3_questions_asked', 0)
    followups = session.get('part3_followups_asked', 0)

    if asked >= 3:
        session['part3_showing_completion'] = True
        session['part3_completion_message'] = "Thank you for your responses; that completes the speaking test!"
        return _part3_state(session, sub_state='part_complete')

    theme = session.get('part3_theme', '')
    history = session.get('part3_conversation_history', [])

    if followups == 0:
        q_type = "main_question"
    else:
        q_type = "follow_up"

    question = generate_part3_question(theme, asked, history, question_type=q_type)

    session['part3_current_question'] = question
    session['part3_waiting_for_answer'] = True
    session['part3_redirect_count'] = 0
    reset_silence_timer(session, 'part3')

    history.append({'role': 'examiner', 'content': question})
    session['part3_conversation_history'] = history

    return _part3_state(session, sub_state='waiting_for_answer')


def submit_answer_part3(session, answer):
    """Process a Part 3 answer."""
    words = answer.split()
    if len(words) > 150:
        answer = ' '.join(words[:150])

    question = session.get('part3_current_question', '')
    history = session.get('part3_conversation_history', [])
    context = _get_context(history)

    is_relevant, relevance_score = check_relevance(answer, question, context)
    relevant = is_relevant or relevance_score >= RELEVANCE_THRESHOLD

    if relevant:
        return _handle_relevant_part3(session, answer)
    elif session.get('part3_redirect_count', 0) >= 1:
        return _handle_second_irrelevant_part3(session, answer)
    else:
        return _handle_first_irrelevant_part3(session, answer)


def _handle_relevant_part3(session, answer):
    history = session.get('part3_conversation_history', [])
    history.append({'role': 'user', 'content': answer})
    session['part3_conversation_history'] = history
    session['part3_redirect_count'] = 0

    word_count = len(answer.split())
    followups = session.get('part3_followups_asked', 0)

    # Generate acknowledgment
    ack = generate_part3_acknowledgment(answer, session['part3_current_question'])
    session['part3_acknowledgment'] = ack
    history.append({'role': 'examiner', 'content': ack})
    session['part3_conversation_history'] = history

    if followups == 0:
        # First answer to main question — always do follow-up 1
        session['part3_first_answer_word_count'] = word_count
        session['part3_followups_asked'] = 1
        session['part3_current_question'] = ""
        session['part3_waiting_for_answer'] = False
        return generate_next_question_part3(session)

    elif followups == 1:
        first_wc = session.get('part3_first_answer_word_count', 0)
        if first_wc >= 30:
            # Detailed first answer — move to next main question
            return _advance_to_next_main_q_part3(session)
        else:
            # Brief first answer — check this follow-up answer
            if word_count >= 20:
                return _advance_to_next_main_q_part3(session)
            else:
                # Need follow-up 2
                session['part3_followups_asked'] = 2
                session['part3_current_question'] = ""
                session['part3_waiting_for_answer'] = False
                return generate_next_question_part3(session)

    else:
        # followups == 2 — always advance
        return _advance_to_next_main_q_part3(session)


def _advance_to_next_main_q_part3(session):
    session['part3_questions_asked'] = session.get('part3_questions_asked', 0) + 1
    session['part3_followups_asked'] = 0
    session['part3_first_answer_word_count'] = 0
    session['part3_current_question'] = ""
    session['part3_waiting_for_answer'] = False
    session['part3_acknowledgment'] = ""
    return generate_next_question_part3(session)


def _handle_second_irrelevant_part3(session, answer):
    history = session.get('part3_conversation_history', [])
    history.append({'role': 'user', 'content': answer})
    history.append({'role': 'examiner', 'content': "Thank you. Let's move on."})
    session['part3_conversation_history'] = history
    return _advance_to_next_main_q_part3(session)


def _handle_first_irrelevant_part3(session, answer):
    history = session.get('part3_conversation_history', [])
    history.append({'role': 'user', 'content': answer})

    question = session.get('part3_current_question', '')
    redirect = generate_redirect_message(question)
    history.append({'role': 'examiner', 'content': redirect})

    session['part3_conversation_history'] = history
    session['part3_current_question'] = redirect
    session['part3_redirect_count'] = 1
    session['part3_waiting_for_answer'] = True

    return _part3_state(session, sub_state='waiting_for_answer', is_redirect=True)


def skip_answer_part3(session):
    """Handle timeout for Part 3."""
    history = session.get('part3_conversation_history', [])
    history.append({'role': 'user', 'content': '[No response - timed out]'})
    session['part3_conversation_history'] = history
    return _advance_to_next_main_q_part3(session)


def _part3_state(session, sub_state='waiting_for_answer', is_redirect=False):
    asked = session.get('part3_questions_asked', 0)
    followups = session.get('part3_followups_asked', 0)

    return {
        'step': 'PART_3',
        'sub_state': sub_state,
        'question': session.get('part3_current_question', ''),
        'acknowledgment': session.get('part3_acknowledgment', ''),
        'is_redirect': is_redirect,
        'is_part_complete': session.get('part3_showing_completion', False),
        'completion_message': session.get('part3_completion_message', ''),
        'theme': session.get('part3_theme', ''),
        'progress': {'main_questions': asked, 'followups': followups, 'total_main': 3},
        'time_limit': 60,
        'test_mode': session.get('test_mode'),
    }


# ---------------------------------------------------------------------------
# SCORING
# ---------------------------------------------------------------------------

def calculate_scores(session):
    """Calculate final scores for the test."""
    p1 = session.get('part1_conversation_history', [])
    p2 = session.get('part2_conversation_history', [])
    p3 = session.get('part3_conversation_history', [])
    vtd = session.get('voice_timing_data', [])
    mode = session.get('test_mode', 'text')

    metrics = generate_metrics_summary(p1, p2, p3, vtd, mode)
    scores = score_speaking_test(p1, p2, p3, metrics, mode, vtd)

    session['step'] = 'RESULTS'
    session['scores'] = scores
    session['metrics'] = metrics

    return {
        'step': 'RESULTS',
        'scores': scores,
        'metrics': metrics,
    }


# ---------------------------------------------------------------------------
# Acknowledgment helper
# ---------------------------------------------------------------------------

def _generate_acknowledgment(answer, question):
    """Generate a brief examiner acknowledgment of the candidate's answer."""
    from config import client, GPT_EXAMINER_MODEL
    try:
        response = client.chat.completions.create(
            model=GPT_EXAMINER_MODEL,
            messages=[
                {"role": "system", "content": f"You are an IELTS examiner. The candidate was asked: \"{question}\". They answered: \"{answer[:300]}\". Give a brief, natural 1-sentence acknowledgment (e.g., 'That's interesting.' or 'I see, thank you.'). Do NOT ask a new question."},
            ],
            temperature=0.7,
            max_tokens=60,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "Thank you."
