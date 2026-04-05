"""
LLM/GPT interaction functions for the IELTS Speaking Assessment application.
Handles question generation, acknowledgments, relevance checking, and redirects.
"""

import json
from config import client, GPT_EXAMINER_MODEL, RELEVANCE_THRESHOLD
from utils import format_conversation_history


def get_examiner_prompt(current_topic, questions_asked, conversation_history):
    """Create the system prompt for the Examiner LLM in Part 1"""
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


def get_examiner_prompt_part3(theme, questions_asked, conversation_history, task="main_question"):
    """Create the system prompt for Part 3 examiner"""
    system_prompt = f"""You are a friendly English speaking test examiner conducting Part 3 of an IELTS-style speaking test.

Theme: {theme}
Questions asked so far: {questions_asked}

Your role depends on the task:
- If asking a main question: Generate a simple, clear, conversational question related to the theme
- If asking a follow-up: Build off what the candidate just said, exploring a related angle
- If acknowledging an answer: Give a brief, natural acknowledgment (1-2 sentences max)

Guidelines:
- Keep questions SIMPLE and CONVERSATIONAL (don't use overly advanced phrasing)
- Questions should be clear and easy to understand
- Build off the candidate's previous relevant responses when possible
- For acknowledgments: Be brief, encouraging, and natural
- DO NOT ask follow-up questions in your acknowledgments

Previous conversation:
{format_conversation_history(conversation_history)}

Task: {task}

Generate your response now. Be natural and conversational."""
    
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
            model=GPT_EXAMINER_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"


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
            model=GPT_EXAMINER_MODEL,
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            temperature=0.8,
            response_format={"type": "json_object"}
        )
        
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
            model=GPT_EXAMINER_MODEL,
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("questions", [])
    except Exception as e:
        # Fallback questions
        return ["Was that easy to talk about?", "Is that still important to you?"]


def extract_theme_from_part2(part2_prompt):
    """Extract the general theme from Part 2's prompt for Part 3 discussion"""
    try:
        response = client.chat.completions.create(
            model=GPT_EXAMINER_MODEL,
            messages=[
                {"role": "system", "content": """You are analyzing a speaking test prompt. 
Extract the general theme/topic in 2-4 words.

Examples:
- "Describe a festival you attended" → "celebrations and festivals"
- "Describe a book you enjoyed" → "books and reading"
- "Describe a difficult decision" → "decision making"
- "Describe a journey" → "travel and journeys"

Return ONLY the theme, no other text."""},
                {"role": "user", "content": part2_prompt}
            ],
            temperature=0.5,
            max_tokens=20
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Fallback theme
        return "life experiences"


def generate_part3_question(theme, questions_asked, conversation_history, question_type="main_question"):
    """Generate a Part 3 question (main or follow-up)"""
    system_prompt = get_examiner_prompt_part3(theme, questions_asked, conversation_history, task=question_type)
    
    try:
        response = client.chat.completions.create(
            model=GPT_EXAMINER_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please generate a {question_type}."}
            ],
            temperature=0.7,
            max_tokens=80
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Fallback question
        return f"Can you tell me more about {theme}?"


def generate_part3_acknowledgment(theme, conversation_history):
    """Generate a brief acknowledgment for Part 3 answers"""
    system_prompt = get_examiner_prompt_part3(theme, 0, conversation_history, task="acknowledge")
    
    try:
        response = client.chat.completions.create(
            model=GPT_EXAMINER_MODEL,
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            temperature=0.7,
            max_tokens=80
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Fallback acknowledgment
        return "I see, thank you."


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
            model=GPT_EXAMINER_MODEL,
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
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
            model=GPT_EXAMINER_MODEL,
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
