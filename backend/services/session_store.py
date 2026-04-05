"""
In-memory session store keyed by UUID.
Replaces Streamlit's st.session_state with plain dicts.
"""

import uuid
from typing import Dict, Any, Optional


_sessions: Dict[str, Dict[str, Any]] = {}


def _default_session() -> Dict[str, Any]:
    """Return a fresh session dict with all default state variables."""
    return {
        # Core state
        "step": "START",
        "onboarding_step": 0,
        "test_mode": None,

        # Part 1
        "part1_initialized": False,
        "part1_topics": [],
        "part1_current_topic_index": 0,
        "part1_questions_asked": 0,
        "part1_questions_per_topic": [],
        "part1_conversation_history": [],
        "part1_waiting_for_answer": False,
        "part1_current_question": "",
        "part1_completion_message": "",
        "part1_showing_completion": False,
        "part1_redirect_count": 0,
        "part1_acknowledgment": "",
        "part1_last_relevant_answer": "",
        "part1_should_build_off": False,

        # Part 1 silence detection (text mode)
        "part1_question_start_time": None,
        "part1_check_in_shown": False,
        "part1_check_in_message": "",

        # Part 1 voice mode
        "part1_voice_timer_start": None,
        "part1_voice_audio_data": None,
        "part1_transcribed_answer": None,
        "part1_timing_result": None,

        # Voice timing data (all parts)
        "voice_timing_data": [],

        # Part 2
        "part2_initialized": False,
        "part2_category": "",
        "part2_prompt_card": {},
        "part2_prep_start_time": None,
        "part2_prep_elapsed": 0,
        "part2_prep_complete": False,
        "part2_long_response": "",
        "part2_rounding_off_questions": [],
        "part2_current_rounding_question": "",
        "part2_rounding_question_index": 0,
        "part2_rounding_questions_answered": 0,
        "part2_waiting_for_rounding_answer": False,
        "part2_conversation_history": [],
        "part2_completion_message": "",
        "part2_showing_completion": False,
        "part2_long_response_redirect_count": 0,
        "part2_rounding_redirect_count": 0,
        "part2_long_response_acknowledgment": "",
        "part2_rounding_acknowledgment": "",
        "part2_long_response_redirect_message": "",
        "part2_instruction_audio_played": False,
        "part2_showing_intro": False,
        "part2_intro_start_time": None,
        "part2_rounding_audio_played_key": None,

        # Part 2 long response silence detection (text mode)
        "part2_long_question_start_time": None,
        "part2_long_check_in_shown": False,
        "part2_long_check_in_message": "",

        # Part 2 rounding-off silence detection (text mode)
        "part2_rounding_question_start_time": None,
        "part2_rounding_check_in_shown": False,
        "part2_rounding_check_in_message": "",

        # Part 2 voice mode
        "part2_voice_timer_start": None,
        "part2_voice_audio_data": None,
        "part2_rounding_voice_timer_start": None,
        "part2_rounding_voice_audio_data": None,
        "part2_long_transcribed_answer": None,
        "part2_long_timing_result": None,
        "part2_rounding_transcribed_answer": None,
        "part2_rounding_timing_result": None,

        # Part 3
        "part3_initialized": False,
        "part3_theme": "",
        "part3_questions_asked": 0,
        "part3_followups_asked": 0,
        "part3_first_answer_word_count": 0,
        "part3_conversation_history": [],
        "part3_current_question": "",
        "part3_waiting_for_answer": False,
        "part3_redirect_count": 0,
        "part3_acknowledgment": "",
        "part3_completion_message": "",
        "part3_showing_completion": False,

        # Part 3 silence detection (text mode)
        "part3_question_start_time": None,
        "part3_check_in_shown": False,
        "part3_check_in_message": "",

        # Part 3 voice mode
        "part3_voice_timer_start": None,
        "part3_voice_audio_data": None,
        "part3_audio_played_key": None,
        "part3_transcribed_answer": None,
    }


def create_session() -> str:
    """Create a new session and return its ID."""
    sid = str(uuid.uuid4())
    _sessions[sid] = _default_session()
    return sid


def get_session(sid: str) -> Optional[Dict[str, Any]]:
    """Get a session by ID. Returns None if not found."""
    return _sessions.get(sid)


def delete_session(sid: str) -> bool:
    """Delete a session. Returns True if it existed."""
    return _sessions.pop(sid, None) is not None


def reset_session(sid: str) -> bool:
    """Reset a session to default state (for retake). Returns True if session existed."""
    if sid in _sessions:
        _sessions[sid] = _default_session()
        return True
    return False
