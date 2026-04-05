"""
Utility functions for the IELTS Speaking Assessment application.
"""

import time
import random


def format_conversation_history(history):
    """Format conversation history for the prompt"""
    if not history:
        return "No previous conversation yet."
    formatted = []
    for item in history:
        if item['role'] == 'examiner':
            formatted.append(f"Examiner: {item['content']}")
        elif item['role'] == 'user':
            formatted.append(f"User: {item['content']}")
    return "\n".join(formatted)


def generate_part_completion_message(part_number, conversation_history):
    """Generate a completion message when a part is finished"""
    next_part = part_number + 1
    return f"Thank you for your responses; that completes Part {part_number}. Now, let's move on to Part {next_part}."


# ===== SILENCE DETECTION HELPER FUNCTIONS =====

def get_check_in_message():
    """Get a random supportive check-in message"""
    messages = [
        "Take your time. You can start whenever you're ready.",
        "No rush—begin when you've gathered your thoughts.",
        "It's okay to pause and think. Start when you're comfortable."
    ]
    return random.choice(messages)


def reset_silence_timer(session, part):
    """Reset silence detection timer for a specific part

    Args:
        session: Session dict (replaces st.session_state)
        part: String identifier (e.g., 'part1', 'part2_long', 'part2_rounding', 'part3')
    """
    start_time_key = f"{part}_question_start_time"
    check_in_shown_key = f"{part}_check_in_shown"
    check_in_message_key = f"{part}_check_in_message"

    session[start_time_key] = None
    session[check_in_shown_key] = False
    session[check_in_message_key] = ""


def check_silence_and_update(session, part, threshold):
    """
    Check if user has been silent for too long and determine what action to take.

    Args:
        session: Session dict (replaces st.session_state)
        part: String identifier for the part (e.g., "part1", "part2_long", "part2_rounding", "part3")
        threshold: Time in seconds before showing check-in (auto-skip happens at threshold * 2)

    Returns:
        dict with:
            - 'show_check_in': True if check-in message should be displayed
            - 'should_skip': True if we should auto-skip to next question
            - 'elapsed_time': Current elapsed time in seconds
    """
    start_time_key = f"{part}_question_start_time"
    check_in_shown_key = f"{part}_check_in_shown"
    check_in_message_key = f"{part}_check_in_message"

    # Initialize timer if not set
    if session.get(start_time_key) is None:
        session[start_time_key] = time.time()
        session[check_in_shown_key] = False
        session[check_in_message_key] = ""

    # Calculate elapsed time
    elapsed_time = time.time() - session[start_time_key]

    # Check if we should auto-skip (after threshold * 2)
    if elapsed_time >= (threshold * 2):
        return {
            'show_check_in': True,
            'should_skip': True,
            'elapsed_time': elapsed_time
        }

    # Check if we should show check-in (after threshold)
    show_check_in = False
    if elapsed_time >= threshold:
        if not session[check_in_shown_key]:
            # First time reaching threshold - store the message
            session[check_in_shown_key] = True
            session[check_in_message_key] = get_check_in_message()
        show_check_in = True

    return {
        'show_check_in': show_check_in,
        'should_skip': False,
        'elapsed_time': elapsed_time
    }
