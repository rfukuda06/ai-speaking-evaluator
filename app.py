import streamlit as st
import os
import random
import time
from dotenv import load_dotenv
from openai import OpenAI
from streamlit_autorefresh import st_autorefresh

# 1. Load your secret keys
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_css():
    """Load custom CSS from style.css file"""
    try:
        with open("style.css") as f:
            css_content = f.read()
            # Inject CSS if there's actual CSS rules (not just comments)
            if css_content.strip():
                st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # CSS file doesn't exist, that's okay
        pass

# Available topics for Part 1
PART1_TOPICS = [
    "Family",
    "Hobbies",
    "Work and Studies",
    "Going out",
    "Hometown",
    "Daily routine",
    "Friends",
    "Food"
]

# Topic categories for Part 2
PART2_CATEGORIES = [
    "a person",
    "a place",
    "an object",
    "an event/experience",
    "an activity/hobby",
    "a piece of media",
    "a decision/change",
    "a journey"
]

# 2. Setup the "Memory" of the app
# 'step' tracks which major section we're in (START, ONBOARDING, PART_1, etc.)
if 'step' not in st.session_state:
    st.session_state.step = "START"

# 'onboarding_step' tracks which onboarding message to show (0, 1, or 2)
# We need this because onboarding has 3 separate messages
if 'onboarding_step' not in st.session_state:
    st.session_state.onboarding_step = 0

# Part 1 state variables
if 'part1_initialized' not in st.session_state:
    st.session_state.part1_initialized = False
if 'part1_topics' not in st.session_state:
    st.session_state.part1_topics = []
if 'part1_current_topic_index' not in st.session_state:
    st.session_state.part1_current_topic_index = 0
if 'part1_questions_asked' not in st.session_state:
    st.session_state.part1_questions_asked = 0  # Questions asked for current topic
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
# Part 1 silence detection
if 'part1_question_start_time' not in st.session_state:
    st.session_state.part1_question_start_time = None
if 'part1_check_in_shown' not in st.session_state:
    st.session_state.part1_check_in_shown = False
if 'part1_check_in_message' not in st.session_state:
    st.session_state.part1_check_in_message = ""

# Part 2 long response silence detection
if 'part2_long_question_start_time' not in st.session_state:
    st.session_state.part2_long_question_start_time = None
if 'part2_long_check_in_shown' not in st.session_state:
    st.session_state.part2_long_check_in_shown = False
if 'part2_long_check_in_message' not in st.session_state:
    st.session_state.part2_long_check_in_message = ""

# Part 2 rounding-off silence detection
if 'part2_rounding_question_start_time' not in st.session_state:
    st.session_state.part2_rounding_question_start_time = None
if 'part2_rounding_check_in_shown' not in st.session_state:
    st.session_state.part2_rounding_check_in_shown = False
if 'part2_rounding_check_in_message' not in st.session_state:
    st.session_state.part2_rounding_check_in_message = ""

# Part 3 silence detection
if 'part3_question_start_time' not in st.session_state:
    st.session_state.part3_question_start_time = None
if 'part3_check_in_shown' not in st.session_state:
    st.session_state.part3_check_in_shown = False
if 'part3_check_in_message' not in st.session_state:
    st.session_state.part3_check_in_message = ""

def initialize_part1():
    """Select 3 random topics and set up Part 1"""
    if not st.session_state.part1_initialized:
        # Randomly select 3 topics
        st.session_state.part1_topics = random.sample(PART1_TOPICS, 3)
        st.session_state.part1_initialized = True
        st.session_state.part1_current_topic_index = 0
        st.session_state.part1_questions_asked = 0
        st.session_state.part1_conversation_history = []
        st.session_state.part1_waiting_for_answer = False
        st.session_state.part1_current_question = ""

def get_examiner_prompt(current_topic, questions_asked, conversation_history):
    """Create the system prompt for the Examiner LLM"""
    system_prompt = f"""You are a friendly English speaking test examiner conducting Part 1 of an IELTS-style speaking test.

Current topic: {current_topic}
You have asked {questions_asked} question(s) about this topic so far.

Your role:
- When asking a question: Keep it simple, conversational, and related to {current_topic}
- When acknowledging an answer: Give a brief, natural acknowledgment (1-2 sentences max)
- Be encouraging and friendly
- DO NOT ask follow-up questions in your acknowledgments
- DO NOT mention moving to other topics or transitioning
- ONLY ask questions when explicitly prompted to do so
- ONLY acknowledge answers when the user has just responded

Previous conversation:
{format_conversation_history(conversation_history)}

Now, generate your response. Be brief and natural."""
    
    return system_prompt

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

def generate_part2_prompt_card(category):
    """Generate a Part 2 prompt card using GPT"""
    system_prompt = f"""You are creating a Part 2 speaking test prompt card for an IELTS-style test.

Category: {category}

Your task:
1. Create a main prompt that starts with "Describe" and asks about a specific topic within this category
2. Generate 3-4 bullet point assistive questions that help structure the response

Format your response EXACTLY as JSON:
{{
    "main_prompt": "Describe [specific topic]",
    "bullet_points": [
        "question 1",
        "question 2",
        "question 3",
        "question 4"
    ]
}}

Examples:
- Category: "a person" → "Describe a teacher who influenced you"
- Category: "an object" → "Describe something you own which is very important to you"
- Category: "a place" → "Describe a place you visited that made an impression on you"

Make the prompt specific and personal. The bullet points should guide the speaker to cover: what/who, when/where, how, and why.

Return ONLY valid JSON, no other text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            temperature=0.8,
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        # Fallback if GPT fails
        return {
            "main_prompt": f"Describe {category} that is important to you",
            "bullet_points": [
                "what or who it is",
                "when or where you encountered it",
                "what you do with it or how it affects you",
                "why it is important to you"
            ]
        }

def generate_rounding_off_questions(long_response, main_prompt):
    """Generate exactly 2 brief rounding off questions after the long turn"""
    system_prompt = f"""You are an IELTS examiner. The candidate just completed a 2-minute long turn about: {main_prompt}

Their response was: "{long_response[:2600]}"  (truncated to 400 words max for context)

Now generate exactly 2 very brief, conversational "rounding off" questions. These should be:
- Short (one sentence max)
- Natural follow-ups to what they said
- Examples: "Was that easy to talk about?" or "Do you still have that object?" or "Would you like to visit that place again?"

Format as JSON:
{{
    "questions": ["question 1", "question 2"]
}}

You must return exactly 2 questions. Return ONLY valid JSON, no other text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result.get("questions", [])
    except Exception as e:
        # Fallback questions
        return ["Was that easy to talk about?", "Is that still important to you?"]

def check_relevance(user_response, current_question, conversation_context=""):
    """Check if user's response is relevant to the current question"""
    system_prompt = f"""You are an IELTS examiner checking if a candidate's response is relevant to the question asked.

Current question: "{current_question}"
User's response: "{user_response}"
Previous context: "{conversation_context[:500] if conversation_context else 'None'}"

Determine if the user's response is relevant to the question. Consider:
- Did they answer the question asked?
- Are they staying on topic?
- Is their response related to what was asked?

Respond with ONLY a JSON object:
{{
    "relevant": true or false,
    "relevance_score": 0.0 to 1.0,
    "reason": "brief explanation"
}}

Return ONLY valid JSON, no other text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result.get("relevant", True), result.get("relevance_score", 0.5)
    except Exception as e:
        # If check fails, assume relevant (don't block user)
        return True, 0.7

def generate_redirect_message(current_question):
    """Generate a polite redirect message when user goes off-topic"""
    system_prompt = f"""You are a friendly IELTS examiner. The candidate has gone off-topic from this question: "{current_question}"

Generate a brief, polite redirect message that:
- Acknowledges what they said briefly
- Gently redirects them back to the question
- Is encouraging and friendly
- Is 1 sentence max

Example: "That's interesting, but let's focus on [the question topic]. Can you tell me more about that?"

Return ONLY the redirect message text, no JSON, no quotes."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            temperature=0.7,
            max_tokens=80
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Fallback redirect
        return "That's interesting, but let's get back to the question. Can you tell me more about that?"

def generate_part_completion_message(part_number, conversation_history):
    """Generate a completion message when a part is finished"""
    # Simple fixed message format
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

def reset_silence_timer(part):
    """Reset silence detection timer for a specific part
    
    Args:
        part: String identifier (e.g., 'part1', 'part2_long', 'part2_rounding', 'part3')
    """
    start_time_key = f"{part}_question_start_time"
    check_in_shown_key = f"{part}_check_in_shown"
    check_in_message_key = f"{part}_check_in_message"
    
    st.session_state[start_time_key] = None
    st.session_state[check_in_shown_key] = False
    st.session_state[check_in_message_key] = ""

def check_silence_and_update(part, threshold):
    """
    Check if user has been silent for too long and determine what action to take.
    
    Args:
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
    if st.session_state.get(start_time_key) is None:
        st.session_state[start_time_key] = time.time()
        st.session_state[check_in_shown_key] = False
        st.session_state[check_in_message_key] = ""
    
    # Calculate elapsed time
    elapsed_time = time.time() - st.session_state[start_time_key]
    
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
        if not st.session_state[check_in_shown_key]:
            # First time reaching threshold - store the message
            st.session_state[check_in_shown_key] = True
            st.session_state[check_in_message_key] = get_check_in_message()
        show_check_in = True
    
    return {
        'show_check_in': show_check_in,
        'should_skip': False,
        'elapsed_time': elapsed_time
    }

# ===== END SILENCE DETECTION HELPER FUNCTIONS =====

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
        st.session_state.part2_prep_start_time = time.time()
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

def get_examiner_prompt_part2(conversation_history, phase="long_response"):
    """Create the system prompt for the Examiner LLM in Part 2"""
    if phase == "long_response":
        system_prompt = f"""You are a friendly English speaking test examiner conducting Part 2 of an IELTS-style speaking test.

Your role:
- The candidate has just finished their 1-2 minute long turn
- Acknowledge their response briefly and naturally
- Be encouraging and friendly
- Keep your response SHORT (1-2 sentences max)
- Then transition to asking rounding-off questions

Guidelines:
- Briefly acknowledge what they said (e.g., "Thank you for that detailed description" or "That's interesting, thank you")
- Keep it conversational and natural
- Don't ask questions yet - just acknowledge and prepare to ask follow-up questions

Previous conversation:
{format_conversation_history(conversation_history)}

Now, generate your acknowledgment response. Be brief and natural."""
    else:  # phase == "rounding_off"
        system_prompt = f"""You are a friendly English speaking test examiner conducting Part 2 of an IELTS-style speaking test.

Your role:
- The candidate has just answered a rounding-off question
- Acknowledge their answer briefly and naturally
- Be encouraging and friendly
- Keep your response SHORT (1-2 sentences max)
- If there are more rounding-off questions, briefly acknowledge and prepare to ask the next one
- If this was the last question, briefly acknowledge and prepare to move on

Guidelines:
- Briefly acknowledge what they said
- Keep it conversational and natural
- Don't ask the next question yet - just acknowledge

Previous conversation:
{format_conversation_history(conversation_history)}

Now, generate your acknowledgment response. Be brief and natural."""
    
    return system_prompt

def get_examiner_prompt_part2(conversation_history, phase="long_response"):
    """Create the system prompt for the Examiner LLM in Part 2"""
    if phase == "long_response":
        system_prompt = f"""You are a friendly English speaking test examiner conducting Part 2 of an IELTS-style speaking test.

Your role:
- The candidate has just finished their 1-2 minute long turn
- Acknowledge their response briefly and naturally
- Be encouraging and friendly
- Keep your response SHORT (1-2 sentences max)
- Then transition to asking rounding-off questions

Guidelines:
- Briefly acknowledge what they said (e.g., "Thank you for that detailed description" or "That's interesting, thank you")
- Keep it conversational and natural
- Don't ask questions yet - just acknowledge and prepare to ask follow-up questions

Previous conversation:
{format_conversation_history(conversation_history)}

Now, generate your acknowledgment response. Be brief and natural."""
    else:  # phase == "rounding_off"
        system_prompt = f"""You are a friendly English speaking test examiner conducting Part 2 of an IELTS-style speaking test.

Your role:
- The candidate has just answered a rounding-off question
- Acknowledge their answer briefly and naturally
- Be encouraging and friendly
- Keep your response SHORT (1-2 sentences max)
- If there are more rounding-off questions, briefly acknowledge and prepare to ask the next one
- If this was the last question, briefly acknowledge and prepare to move on

Guidelines:
- Briefly acknowledge what they said
- Keep it conversational and natural
- Don't ask the next question yet - just acknowledge

Previous conversation:
{format_conversation_history(conversation_history)}

Now, generate your acknowledgment response. Be brief and natural."""
    
    return system_prompt

def get_examiner_response(prompt, conversation_history):
    """Call OpenAI API to get examiner's question/response"""
    try:
        # Build messages for the API
        messages = [
            {"role": "system", "content": prompt},
        ]
        
        # Add conversation history
        for item in conversation_history[-6:]:  # Last 6 exchanges for context
            if item['role'] == 'examiner':
                messages.append({"role": "assistant", "content": item['content']})
            elif item['role'] == 'user':
                messages.append({"role": "user", "content": item['content']})
        
        # Call OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def initialize_part3():
    """Initialize Part 3: Extract theme from Part 2 and set up the discussion"""
    if not st.session_state.part3_initialized:
        # Extract theme from Part 2's prompt
        part2_prompt = st.session_state.part2_prompt_card.get('main_prompt', '')
        
        # If Part 2 wasn't completed (e.g., user skipped directly to Part 3), use a default
        if not part2_prompt:
            st.warning("⚠️ Part 2 was not completed. Using a default theme for testing.")
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

def extract_theme_from_part2(part2_prompt):
    """Extract the general theme from Part 2's prompt for Part 3 discussion"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """You are analyzing a speaking test prompt. 
Extract the general theme/topic in 2-4 words.

Examples:
- "Describe a festival you attended" → "celebrations and festivals"
- "Describe a piece of technology you use" → "technology"
- "Describe a memorable journey" → "travel and journeys"
- "Describe a person who influenced you" → "influential people"

Return ONLY the theme, nothing else."""},
                {"role": "user", "content": f"Part 2 prompt: {part2_prompt}"}
            ],
            temperature=0.7,
            max_tokens=20
        )
        
        theme = response.choices[0].message.content.strip()
        return theme if theme else "the topic we discussed"
    except Exception as e:
        return "the topic we discussed"

def get_examiner_prompt_part3(theme, questions_asked, conversation_history, task="main_question"):
    """Create the system prompt for Part 3 examiner"""
    if task == "main_question":
        system_prompt = f"""You are an examiner conducting Part 3 of an IELTS-style speaking test.

Part 2 was about: {theme}
Main questions asked so far: {questions_asked}/3

Your role:
- Ask SIMPLE, CLEAR questions about {theme} at a general/societal level
- Use straightforward language - avoid overly complex or wordy phrasing
- Questions should be opinion-based and analytical, but easy to understand
- IMPORTANT: Build your next question off what the candidate just said - reference their answer and explore a related angle

Question types to use:
- Comparison: "Have things changed since your parents' time?"
- Opinion: "Why do you think [topic] is important?"
- Prediction: "Do you think [aspect] will change in the future?"
- Evaluation: "What are the advantages of [topic]?"
- Society: "How does [topic] affect people in your country?"

Good examples:
- "Why do you think celebrations are important in society?"
- "Do you think advertising influences what people buy?"
- "What kind of things give status to people in your country?"
- "Have things changed since your parents' time?"
- "Do you think celebrations are experienced differently by different generations?"

BAD examples (too complex/wordy):
- "How do you think advancements in technology have changed the way we perceive and interact with art and culture compared to previous generations?"
- "What are the multifaceted implications of globalization on traditional cultural practices?"

Previous conversation:
{format_conversation_history(conversation_history)}

IMPORTANT: Look at the candidate's last answer. Your next question should naturally flow from what they just said, exploring a different aspect or angle of the same topic. Don't jump to a completely unrelated question.

Generate ONE simple, clear question that builds off their previous answer. Keep it conversational and direct. Return ONLY the question, nothing else."""
    
    elif task == "followup_question":
        system_prompt = f"""You are an examiner conducting Part 3 of an IELTS-style speaking test.

Part 2 was about: {theme}

Your role:
- Ask a SHORT follow-up question to get the candidate to expand, clarify, or elaborate on their last answer
- Keep the question BRIEF and CONVERSATIONAL
- The question should stay on the same topic as the previous question
- Don't introduce a new angle or topic

Good follow-up examples:
- "Can you give an example of that?"
- "Why do you think that is?"
- "Can you tell me more about that?"
- "What do you mean by that?"
- "How does that work?"
- "Can you elaborate on that point?"

Previous conversation:
{format_conversation_history(conversation_history)}

Look at the candidate's last answer. Ask ONE short follow-up question to get them to expand or clarify. Return ONLY the question, nothing else."""
    
    elif task == "acknowledgment":
        system_prompt = f"""You are an examiner in Part 3 of a speaking test.

Theme: {theme}

Your role:
- The candidate just gave an answer
- Acknowledge their response briefly and naturally (1-2 sentences max)
- Be encouraging and show you're listening
- DO NOT ask the next question yet - just acknowledge

Previous conversation:
{format_conversation_history(conversation_history)}

Generate a brief acknowledgment. Return ONLY the acknowledgment, nothing else."""
    
    elif task == "decide_followup":
        system_prompt = f"""You are an examiner in Part 3 of a speaking test.

Theme: {theme}
Main questions asked: {questions_asked}/5

Your task:
- The candidate just answered a question
- Decide: Should you ask a FOLLOW-UP question (to dig deeper on the same topic), or MOVE ON to a new main question?

Guidelines:
- Ask follow-up if: answer feels incomplete, candidate made an interesting point worth exploring, or you want clarification
- Move on if: answer was complete and thorough, you've already asked a follow-up on this topic, or it's time for a new angle

Previous conversation:
{format_conversation_history(conversation_history)}

Respond in JSON format:
{{
    "action": "follow_up" or "new_question",
    "reason": "brief explanation"
}}"""
    
    return system_prompt

def decide_followup_or_new_question(theme, questions_asked, conversation_history):
    """Ask GPT to decide if we should ask a follow-up or move to a new main question"""
    try:
        prompt = get_examiner_prompt_part3(theme, questions_asked, conversation_history, task="decide_followup")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=100
        )
        
        import json
        decision = json.loads(response.choices[0].message.content)
        return decision.get("action", "new_question")  # Default to new question if unclear
    
    except Exception as e:
        # If GPT call fails, default to moving on to new question
        return "new_question"

def generate_part3_question(theme, questions_asked, conversation_history, question_type="main_question"):
    """Generate a Part 3 question using GPT"""
    try:
        prompt = get_examiner_prompt_part3(theme, questions_asked, conversation_history, task=question_type)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=100 if question_type == "main_question" else 50
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        # Fallback question
        if question_type == "followup_question":
            return "Can you tell me more about that?"
        else:
            return f"What do you think about the role of {theme} in modern society?"

def generate_part3_acknowledgment(theme, conversation_history):
    """Generate a brief acknowledgment for Part 3 answers"""
    try:
        prompt = get_examiner_prompt_part3(theme, 0, conversation_history, task="acknowledgment")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=50
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return "I see, thank you."

def main():
    # Load custom CSS styles
    load_css()
    
    st.title("🎙️ English Speaking Test")
    
    # Debug controls (temporary)
    with st.expander("🛠️ Debug Controls (Skip to Part)"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Skip to Part 1"):
                st.session_state.step = "PART_1"
                initialize_part1()
                st.rerun()
        with col2:
            if st.button("Skip to Part 2"):
                st.session_state.step = "PART_2"
                st.rerun()
        with col3:
            if st.button("Skip to Part 3"):
                st.session_state.step = "PART_3"
                # Reset Part 3 state for fresh start
                st.session_state.part3_initialized = False
                st.rerun()
        with col4:
            if st.button("Skip to Results"):
                st.session_state.step = "SCORING"
                st.rerun()

    if st.session_state.step == "START":
        st.write("Hello Renzo! Ready to start your English test?")
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
                    # User consented, move to Part 1
                    st.session_state.step = "PART_1"
                    st.rerun()
            with col2:
                if st.button("Go back"):
                    # User wants to go back, return to START
                    st.session_state.step = "START"
                    st.session_state.onboarding_step = 0
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
                st.info(f"📌 Current topic: **{current_topic}**")
            
            # If we haven't asked the first question yet, or we're ready for a new question
            if not st.session_state.part1_waiting_for_answer and st.session_state.part1_current_question == "":
                # FIRST: Check if we've already asked 3 questions for this topic
                if st.session_state.part1_questions_asked >= 3:
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
                        st.rerun()
            
            # Display the current question (with acknowledgment if available)
            if st.session_state.part1_current_question:
                # If there's an acknowledgment, show it first, then the question
                if st.session_state.part1_acknowledgment:
                    combined_response = st.session_state.part1_acknowledgment + " " + st.session_state.part1_current_question
                    st.write("**Examiner:** " + combined_response)
                    # Don't clear acknowledgment here - it will be cleared when next acknowledgment is generated
                else:
                    st.write("**Examiner:** " + st.session_state.part1_current_question)
            
            # Silence detection for Part 1
            if st.session_state.part1_waiting_for_answer and st.session_state.part1_current_question:
                silence_status = check_silence_and_update("part1", 30)  # 30s check-in, 60s auto-skip
                
                # Show check-in message if threshold reached
                if silence_status['show_check_in'] and st.session_state.part1_check_in_message:
                    st.info(f"💭 {st.session_state.part1_check_in_message}")
                
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
                            
                            # Store this answer to build off for next question (if not the 3rd question)
                            if st.session_state.part1_questions_asked < 3:
                                st.session_state.part1_last_relevant_answer = user_answer
                                st.session_state.part1_should_build_off = True
                            else:
                                # This is the 3rd question, don't build off
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
                            reset_silence_timer("part1")  # Reset timer after moving on
                            st.rerun()
                        # If not relevant and first try, send redirect
                        else:
                            # First redirect - send polite nudge
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
    
    elif st.session_state.step == "PART_2":
        # Initialize Part 2 when we first enter
        initialize_part2()
        
        st.write("### Part 2: The Long Turn")
        st.write("In this part, you'll speak for 1-2 minutes about a topic. You'll have 5 seconds to prepare. (Testing mode)")
        
        # Show prompt card
        if st.session_state.part2_prompt_card:
            st.write("---")
            st.write("### 📋 Your Prompt Card")
            st.write(f"**{st.session_state.part2_prompt_card.get('main_prompt', '')}**")
            st.write("")
            st.write("You should say:")
            for bullet in st.session_state.part2_prompt_card.get('bullet_points', []):
                st.write(f"• {bullet}")
            st.write("")
            st.write("*You will have to talk about the topic for 1 to 2 minutes. You have 5 seconds to think about what you're going to say. (Testing mode) You can make some notes to help you if you wish.*")
            st.write("---")
        
        # Preparation phase (5 seconds for testing)
        if not st.session_state.part2_prep_complete:
            # Calculate elapsed time
            if st.session_state.part2_prep_start_time:
                elapsed = int(time.time() - st.session_state.part2_prep_start_time)
                remaining = max(0, 5 - elapsed)
                
                if remaining > 0:
                    st.info(f"⏱️ **Preparation time:** {remaining} seconds remaining")
                    st.progress(1 - (remaining / 5))
                    
                    # Add skip button
                    if st.button("⏩ Skip preparation time and start now"):
                        st.session_state.part2_prep_complete = True
                        st.rerun()
                    
                    # Auto-refresh every second to update timer
                    time.sleep(1)
                    st.rerun()
                else:
                    # Preparation time is up
                    st.session_state.part2_prep_complete = True
                    st.session_state.part2_prep_elapsed = 5
                    reset_silence_timer("part2_long")  # Start timer for long response
                    st.rerun()
        
        # After preparation, show speaking prompt
        if st.session_state.part2_prep_complete and not st.session_state.part2_long_response:
            st.success("⏱️ Preparation time is up!")
            st.write("**Now, please tell me about the topic. Speak for about 1-2 minutes.**")
            
            # Show redirect message if available
            if st.session_state.part2_long_response_redirect_message:
                st.write("---")
                st.warning(f"**Examiner:** {st.session_state.part2_long_response_redirect_message}")
                st.info("Please revise your response to better address the prompt card above.")
                st.write("---")
            
            # Silence detection for Part 2 long response
            silence_status = check_silence_and_update("part2_long", 60)  # 60s check-in, 120s auto-skip (refresh every 60s)
            
            # Show check-in message if threshold reached
            if silence_status['show_check_in'] and st.session_state.part2_long_check_in_message:
                st.info(f"💭 {st.session_state.part2_long_check_in_message}")
            
            # Handle auto-skip if timeout reached - show completion message
            if silence_status['should_skip']:
                # Store "No response" in conversation history
                st.session_state.part2_conversation_history.append({
                    'role': 'candidate',
                    'content': '[No response - timed out]'
                })
                # Skip rounding-off questions and show completion message
                st.session_state.part2_long_response = "[No response provided]"
                
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
                
                # Display the current question
                if st.session_state.part2_current_rounding_question:
                    st.write("---")
                    st.write("### Rounding Off Questions")
                    st.write("I'll ask you some follow-up questions. Please respond with brief, conversational responses.")
                    st.write(f"**Examiner:** {st.session_state.part2_current_rounding_question}")
                
                # Silence detection for Part 2 rounding-off questions
                if st.session_state.part2_waiting_for_rounding_answer and st.session_state.part2_current_rounding_question:
                    silence_status = check_silence_and_update("part2_rounding", 30)  # 30s check-in, 60s auto-skip
                    
                    # Show check-in message if threshold reached
                    if silence_status['show_check_in'] and st.session_state.part2_rounding_check_in_message:
                        st.info(f"💭 {st.session_state.part2_rounding_check_in_message}")
                    
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
    
    elif st.session_state.step == "PART_3":
        st.write("### Part 3: The Discussion")
        st.write("I’ll ask you some questions related to Part 2. Please respond with thoughtful, detailed responses.")
        
        # Initialize Part 3 if needed
        if not st.session_state.part3_initialized:
            initialize_part3()
        
        # Debug: Show Part 2 prompt and extracted theme
        with st.expander("🐛 Debug Info (Part 3)"):
            st.write(f"**Part 2 prompt:** {st.session_state.part2_prompt_card.get('main_prompt', 'NOT SET')}")
            st.write(f"**Extracted theme:** {st.session_state.part3_theme}")
            st.write(f"**Main questions asked:** {st.session_state.part3_questions_asked}/3")
            st.write(f"**Follow-ups asked for current question:** {st.session_state.part3_followups_asked}/2")
            st.write(f"**First answer word count:** {st.session_state.part3_first_answer_word_count} words (>= 30 = only 1 follow-up)")
        
        # Show completion message and button if Part 3 is done
        if st.session_state.part3_showing_completion:
            st.success(st.session_state.part3_completion_message)
            if st.button("View Results"):
                st.session_state.step = "SCORING"
                st.rerun()
        else:
            # Display theme
            st.info(f"📋 **Discussion Topic:** {st.session_state.part3_theme}")
            
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
                    reset_silence_timer("part3")  # Reset timer for new question
                    st.rerun()
            
            # Display the current question (with acknowledgment if available)
            if st.session_state.part3_current_question:
                # If there's an acknowledgment, show it first, then the question
                if st.session_state.part3_acknowledgment:
                    combined_response = st.session_state.part3_acknowledgment + " " + st.session_state.part3_current_question
                    st.write("**Examiner:** " + combined_response)
                    # Don't clear acknowledgment here - it will be cleared when next acknowledgment is generated
                else:
                    st.write("**Examiner:** " + st.session_state.part3_current_question)
            
            # Silence detection for Part 3
            if st.session_state.part3_waiting_for_answer and st.session_state.part3_current_question:
                silence_status = check_silence_and_update("part3", 40)  # 40s check-in, 80s auto-skip
                
                # Show check-in message if threshold reached
                if silence_status['show_check_in'] and st.session_state.part3_check_in_message:
                    st.info(f"💭 {st.session_state.part3_check_in_message}")
                
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
                                
                                reset_silence_timer("part3")  # Reset timer after answer/new question
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
                                
                                # Add redirect to history
                                st.session_state.part3_conversation_history.append({
                                    'role': 'examiner',
                                    'content': redirect_message
                                })
                                
                                reset_silence_timer("part3")  # Reset timer for redirect question
                                st.rerun()
    
    elif st.session_state.step == "SCORING":
        st.write("# 📊 Your Speaking Assessment Results")
        st.write("---")
        
        # CEFR Level Assessment Section
        st.write("## Your Estimated Level")
        st.success("### 🎯 B1 (Intermediate)")
        st.write("*Note: This is a preliminary assessment. In future versions, we will analyze your conversation data to provide a more precise level determination.*")
        
        st.write("")
        st.write("---")
        
        # CEFR Levels Explanation
        st.write("## 📚 Understanding CEFR Levels")
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
            
            st.write("**B1 - Intermediate** ⭐")
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
        st.write("## 💡 Tips for Improvement")
        st.write("""
Here are evidence-based strategies to help you improve your speaking skills:
        """)
        
        st.write("### 🎤 Delivery & Fluency")
        st.write("""
- **Pacing + Clarity:** Don't speak too fast or too slow; aim for balance and intelligibility
- **Reduce Filler Words:** Minimize "um," "like," "you know" — replace with a short silent pause or a neutral phrase like "That's interesting—let me think…"
- **Thinking Time is Allowed:** You can pause briefly, ask to repeat the question, or use stalling phrases if needed
        """)
        
        st.write("### 🎯 Content & Relevance")
        st.write("""
- **Stay On-Topic:** Actually answer the question asked — more words don't help if you drift
- **Avoid Memorized Answers:** Sound natural and engaged rather than using "ready-made" responses
- **Don't Use Unfamiliar Big Words:** Accuracy and appropriateness matter more than impressive vocabulary
        """)
        
        st.write("### 📈 Practice Methods")
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
        st.write("## 📖 Additional Resources")
        st.write("""
For more comprehensive IELTS Speaking tips and practice strategies, visit:
        """)
        st.markdown("[📘 **IELTS Speaking Tips: Complete Guide**](https://global-exam.com/blog/en/ielts-speaking-tips-all-you-need-to-prepare-for-the-oral-test/)")
        
        st.write("")
        st.write("---")
        
        # Option to retake
        st.write("### What's Next?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Take Test Again"):
                # Reset all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        with col2:
            st.write("*More features coming soon: detailed score breakdown, personalized feedback, and progress tracking!*")
    
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