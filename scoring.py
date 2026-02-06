"""
Scoring and metrics calculation functions for IELTS band score assessment.
"""

import json
from config import client, GPT_SCORER_MODEL, SCORING_WEIGHTS, IDEAL_WORD_COUNTS
from utils import format_conversation_history


def calculate_response_metrics(conversation_history):
    """
    Calculate basic response metrics from conversation history
    
    Returns dict with:
    - total_responses: total number of user responses
    - completed_responses: responses that aren't timeouts
    - timeout_count: number of timed out responses
    - avg_word_count: average words per completed response
    """
    if not conversation_history:
        return {
            'total_responses': 0,
            'completed_responses': 0,
            'timeout_count': 0,
            'avg_word_count': 0
        }
    
    user_responses = [
        entry for entry in conversation_history 
        if entry['role'] in ['user', 'candidate']
    ]
    
    # Separate real responses from timeouts
    real_responses = [
        r for r in user_responses 
        if not r['content'].startswith('[No response')
    ]
    
    timeout_count = len(user_responses) - len(real_responses)
    
    # Calculate average word count from real responses
    word_counts = [len(r['content'].split()) for r in real_responses]
    avg_word_count = sum(word_counts) / len(word_counts) if word_counts else 0
    
    return {
        'total_responses': len(user_responses),
        'completed_responses': len(real_responses),
        'timeout_count': timeout_count,
        'avg_word_count': round(avg_word_count, 1)
    }


def calculate_voice_metrics(voice_timing_data):
    """
    Calculate aggregated voice metrics from timing data
    
    Returns dict with WPM, pause statistics, etc.
    """
    if not voice_timing_data:
        return {
            'avg_wpm': 0,
            'wpm_min': 0,
            'wpm_max': 0,
            'total_pauses': 0,
            'avg_pause_length': 0,
            'long_pause_count': 0,
            'pause_frequency_per_min': 0,
            'total_speaking_time': 0
        }
    
    # Extract all WPM values
    wpm_values = [d['wpm'] for d in voice_timing_data if d['wpm'] > 0]
    
    # Total speaking time
    total_duration = sum(d['duration'] for d in voice_timing_data)
    
    # Total pauses
    total_pauses = sum(d['num_pauses'] for d in voice_timing_data)
    
    # All pause lengths
    all_pauses = []
    for d in voice_timing_data:
        all_pauses.extend(d['pauses'])
    
    # Long pauses
    long_pause_count = sum(d['long_pauses'] for d in voice_timing_data)
    
    # Pause frequency (pauses per minute)
    pause_freq = (total_pauses / total_duration * 60) if total_duration > 0 else 0
    
    return {
        'avg_wpm': round(sum(wpm_values) / len(wpm_values), 1) if wpm_values else 0,
        'wpm_min': round(min(wpm_values), 1) if wpm_values else 0,
        'wpm_max': round(max(wpm_values), 1) if wpm_values else 0,
        'total_pauses': total_pauses,
        'avg_pause_length': round(sum(all_pauses) / len(all_pauses), 2) if all_pauses else 0,
        'long_pause_count': long_pause_count,
        'pause_frequency_per_min': round(pause_freq, 1),
        'total_speaking_time': round(total_duration, 1)
    }


def calculate_part_specific_metrics(part1_history, part2_history, part3_history):
    """
    Calculate metrics specific to each part of the test
    
    Returns dict with average word counts per part and length assessments
    """
    def get_user_responses(history):
        return [
            entry['content'] for entry in history 
            if entry['role'] in ['user', 'candidate'] 
            and not entry['content'].startswith('[No response')
        ]
    
    # Part 1 responses
    part1_responses = get_user_responses(part1_history)
    part1_word_counts = [len(r.split()) for r in part1_responses]
    part1_avg = sum(part1_word_counts) / len(part1_word_counts) if part1_word_counts else 0
    
    # Part 2 - separate long response from rounding-off
    part2_responses = get_user_responses(part2_history)
    
    part2_long_words = 0
    part2_rounding_words = []
    
    if part2_responses:
        # Find the long response (usually the longest one or first substantial one)
        for i, response in enumerate(part2_responses):
            word_count = len(response.split())
            if word_count > 80:  # Likely the long response
                part2_long_words = word_count
                part2_rounding_words = [len(r.split()) for r in part2_responses[i+1:]]
                break
        
        # If no long response found, first is long, rest are rounding
        if part2_long_words == 0 and part2_responses:
            part2_long_words = len(part2_responses[0].split())
            part2_rounding_words = [len(r.split()) for r in part2_responses[1:]]
    
    part2_rounding_avg = sum(part2_rounding_words) / len(part2_rounding_words) if part2_rounding_words else 0
    
    # Part 3 responses
    part3_responses = get_user_responses(part3_history)
    part3_word_counts = [len(r.split()) for r in part3_responses]
    part3_avg = sum(part3_word_counts) / len(part3_word_counts) if part3_word_counts else 0
    
    return {
        'part1_avg_words': round(part1_avg, 1),
        'part1_count': len(part1_word_counts),
        'part1_assessment': 'good' if 20 <= part1_avg <= 50 else ('too_short' if part1_avg < 20 else 'too_long'),
        
        'part2_long_words': part2_long_words,
        'part2_long_assessment': 'good' if part2_long_words >= 150 else ('acceptable' if part2_long_words >= 100 else 'too_short'),
        
        'part2_rounding_avg': round(part2_rounding_avg, 1),
        'part2_rounding_count': len(part2_rounding_words),
        'part2_rounding_assessment': 'good' if 20 <= part2_rounding_avg <= 50 else ('too_short' if part2_rounding_avg < 20 else 'too_long'),
        
        'part3_avg_words': round(part3_avg, 1),
        'part3_count': len(part3_word_counts),
        'part3_assessment': 'good' if 50 <= part3_avg <= 100 else ('too_short' if part3_avg < 50 else 'too_long')
    }


def count_timeouts_and_relevance(conversation_history):
    """
    Count timeouts and irrelevant answers by analyzing conversation patterns
    
    Returns dict with counts for penalty calculation
    """
    if not conversation_history:
        return {'timeout_count': 0, 'irrelevant_count': 0}
    
    timeout_count = 0
    irrelevant_count = 0
    
    for i, entry in enumerate(conversation_history):
        # Check for timeouts
        if entry['role'] in ['user', 'candidate'] and entry['content'].startswith('[No response'):
            timeout_count += 1
        
        # Check for irrelevant answers (followed by redirect or "Let's move on")
        if entry['role'] == 'examiner':
            content_lower = entry['content'].lower()
            # Redirect indicators
            if ('could you' in content_lower and 'please' in content_lower) or \
               ('let me rephrase' in content_lower) or \
               ('let\'s try' in content_lower and 'again' in content_lower):
                # Previous user response was irrelevant
                # Look back to find it
                for j in range(i-1, -1, -1):
                    if conversation_history[j]['role'] in ['user', 'candidate']:
                        if not conversation_history[j]['content'].startswith('[No response'):
                            irrelevant_count += 1
                        break
    
    return {
        'timeout_count': timeout_count,
        'irrelevant_count': irrelevant_count
    }


def generate_metrics_summary(part1_history, part2_history, part3_history, voice_timing_data, test_mode):
    """
    Master function that generates comprehensive metrics for scoring
    
    Args:
        part1_history: Part 1 conversation history
        part2_history: Part 2 conversation history
        part3_history: Part 3 conversation history
        voice_timing_data: Voice timing data (empty list for text mode)
        test_mode: 'text' or 'voice'
    
    Returns:
        Comprehensive metrics dict for scoring
    """
    # Combine histories for overall metrics
    all_history = []
    if part1_history:
        all_history.extend(part1_history)
    if part2_history:
        all_history.extend(part2_history)
    if part3_history:
        all_history.extend(part3_history)
    
    # Calculate all metrics
    response_metrics = calculate_response_metrics(all_history)
    part_metrics = calculate_part_specific_metrics(part1_history, part2_history, part3_history)
    timeout_relevance = count_timeouts_and_relevance(all_history)
    
    # Voice metrics if available
    voice_metrics = {}
    if test_mode == 'voice' and voice_timing_data:
        voice_metrics = calculate_voice_metrics(voice_timing_data)
    
    # Combine all metrics
    metrics = {
        'test_mode': test_mode,
        **response_metrics,
        **part_metrics,
        **timeout_relevance,
        **voice_metrics
    }
    
    return metrics


def combine_conversation_histories(part1_history, part2_history, part3_history):
    """
    Combine all conversation histories with part labels
    
    Returns list of dicts with added 'part' field
    """
    combined = []
    
    if part1_history:
        for entry in part1_history:
            combined.append({**entry, 'part': 'Part 1'})
    
    if part2_history:
        for entry in part2_history:
            combined.append({**entry, 'part': 'Part 2'})
    
    if part3_history:
        for entry in part3_history:
            combined.append({**entry, 'part': 'Part 3'})
    
    return combined


def format_metrics_for_prompt(metrics):
    """
    Format metrics dict into readable text for GPT prompt
    """
    lines = []
    
    # Test mode
    lines.append(f"Test Mode: {metrics.get('test_mode', 'unknown').upper()}")
    lines.append("")
    
    # Response metrics
    lines.append("RESPONSE METRICS:")
    lines.append(f"- Total responses: {metrics.get('completed_responses', 0)}/{metrics.get('total_responses', 0)}")
    lines.append(f"- Average word count: {metrics.get('avg_word_count', 0)} words")
    lines.append("")
    
    # Part-specific metrics
    lines.append("PART-SPECIFIC METRICS:")
    lines.append(f"- Part 1: Avg {metrics.get('part1_avg_words', 0)} words ({metrics.get('part1_count', 0)} responses) - {metrics.get('part1_assessment', 'N/A')}")
    lines.append(f"- Part 2 Long Response: {metrics.get('part2_long_words', 0)} words - {metrics.get('part2_long_assessment', 'N/A')}")
    lines.append(f"- Part 2 Rounding-off: Avg {metrics.get('part2_rounding_avg', 0)} words ({metrics.get('part2_rounding_count', 0)} responses) - {metrics.get('part2_rounding_assessment', 'N/A')}")
    lines.append(f"- Part 3: Avg {metrics.get('part3_avg_words', 0)} words ({metrics.get('part3_count', 0)} responses) - {metrics.get('part3_assessment', 'N/A')}")
    lines.append("")
    
    # Penalties
    lines.append("PENALTIES:")
    lines.append(f"- Timeouts: {metrics.get('timeout_count', 0)} (each = -0.5 from Task Achievement)")
    lines.append(f"- Irrelevant answers: {metrics.get('irrelevant_count', 0)} (each = -0.5 from Task Achievement)")
    lines.append(f"- TOTAL PENALTY: -{(metrics.get('timeout_count', 0) + metrics.get('irrelevant_count', 0)) * 0.5} bands from Task Achievement")
    lines.append("")
    
    # Voice metrics if available
    if metrics.get('test_mode') == 'voice' and metrics.get('avg_wpm', 0) > 0:
        lines.append("VOICE/FLUENCY METRICS:")
        lines.append(f"- Speaking rate: {metrics.get('avg_wpm', 0)} WPM (ideal: 120-160 WPM)")
        lines.append(f"- WPM range: {metrics.get('wpm_min', 0)} - {metrics.get('wpm_max', 0)} WPM")
        lines.append(f"- Total speaking time: {metrics.get('total_speaking_time', 0)}s")
        lines.append(f"- Total pauses: {metrics.get('total_pauses', 0)}")
        lines.append(f"- Average pause length: {metrics.get('avg_pause_length', 0)}s")
        lines.append(f"- Long pauses (>1.5s): {metrics.get('long_pause_count', 0)}")
        lines.append(f"- Pause frequency: {metrics.get('pause_frequency_per_min', 0)} pauses/min")
        lines.append("")
    
    return "\n".join(lines)


def format_full_conversation(combined_history, voice_timing_data=None):
    """
    Format combined conversation history for GPT prompt
    
    Args:
        combined_history: List of conversation entries
        voice_timing_data: Optional list of voice timing data to add pause markers
    """
    if not combined_history:
        return "No conversation history available."
    
    lines = []
    current_part = None
    
    for entry in combined_history:
        # Add part header when it changes
        if entry.get('part') != current_part:
            current_part = entry.get('part')
            if lines:  # Add spacing between parts
                lines.append("")
            lines.append(f"=== {current_part} ===")
            lines.append("")
        
        # Format the exchange
        if entry['role'] == 'examiner':
            lines.append(f"Examiner: {entry['content']}")
        elif entry['role'] in ['user', 'candidate']:
            lines.append(f"Candidate: {entry['content']}")
    
    return "\n".join(lines)


def map_band_to_cefr(band_score):
    """
    Map IELTS band score (1-9) to CEFR level
    """
    if band_score >= 9:
        return "C2"
    elif band_score >= 7:
        return "C1"
    elif band_score >= 6:
        return "B2"
    elif band_score >= 5:
        return "B1"
    elif band_score >= 3:
        return "A2"
    else:
        return "A1"


def get_cefr_description(cefr_level):
    """
    Get description for CEFR level
    """
    descriptions = {
        "C2": "Proficiency",
        "C1": "Advanced",
        "B2": "Upper Intermediate",
        "B1": "Intermediate",
        "A2": "Elementary",
        "A1": "Beginner"
    }
    return descriptions.get(cefr_level, "Unknown")


def score_speaking_test(part1_history, part2_history, part3_history, metrics, test_mode, voice_timing_data=None):
    """
    Score the speaking test using GPT-4 with detailed IELTS rubric
    
    Args:
        part1_history: Part 1 conversation history
        part2_history: Part 2 conversation history
        part3_history: Part 3 conversation history
        metrics: Dict of calculated metrics
        test_mode: 'text' or 'voice'
        voice_timing_data: Optional list of voice timing data with word-level timestamps
    
    Returns:
        Dict with scores, final_band, cefr_level, feedback, etc.
    """
    try:
        # Combine and format conversation
        combined_history = combine_conversation_histories(part1_history, part2_history, part3_history)
        formatted_conversation = format_full_conversation(combined_history, voice_timing_data)
        formatted_metrics = format_metrics_for_prompt(metrics)
        
        # Calculate total penalty
        total_penalty = (metrics.get('timeout_count', 0) + metrics.get('irrelevant_count', 0)) * 0.5
        
        # Build comprehensive scoring prompt
        scoring_prompt = f"""You are an experienced IELTS Speaking examiner. Score this speaking test on the IELTS 1-9 band scale.

{formatted_metrics}

FULL CONVERSATION TRANSCRIPT:
{formatted_conversation}

NOTE: For voice mode responses, [pause: X.Xs] markers show actual pause locations and durations (0.5s+ shown).
- Pauses between sentences or at natural clause boundaries are NORMAL and should NOT be penalized
- Pauses mid-clause or mid-phrase suggest processing difficulty (more concerning for fluency)
- Consider BOTH pause frequency AND placement when assessing fluency

---

SCORING CRITERIA (IELTS 1-9 Band Scale):

1. FLUENCY & COHERENCE (25% of total score):
   - Pace: 120-160 WPM = high score; <100 or >180 = lower
   - Pauses: Few, well-placed at clause/sentence boundaries = high; frequent mid-clause pauses = lower
   - Hesitation and repetition: Minimal = high
   - Natural speech rhythm and flow
   
   Band 9: Speaks fluently with minimal hesitation. Develops topics fully and coherently.
   Band 7: Speaks at length with few hesitations. Shows some flexibility. Uses cohesion but may be mechanical.
   Band 5: Maintains flow but has noticeable effort. Overuses certain connectors. May repeat and self-correct.
   Band 3: Frequently pauses. Limited ability to link simple sentences. Gives only simple responses.

2. LEXICAL RESOURCE (20% of total score):
   - Range APPROPRIATE to topics (not random advanced words out of context)
   - Natural word choice and collocation
   - Paraphrasing ability
   - Precision and naturalness
   
   Band 9: Uses vocabulary with full flexibility and precision. Uses idiomatic language naturally.
   Band 7: Uses vocabulary resource flexibly to discuss topics at length. Uses some less common items with awareness of style/collocation.
   Band 5: Manages to talk about familiar and unfamiliar topics. Makes noticeable errors but meaning is clear.
   Band 3: Uses simple vocabulary for simple topics. Has insufficient vocabulary for unfamiliar topics.

3. GRAMMATICAL RANGE & ACCURACY (20% of total score):
   - Simple structures used accurately
   - Complex structures attempted (errors acceptable if message is clear)
   - Variety of tenses and structures
   - Overall effectiveness despite errors
   
   Band 9: Uses full range of structures naturally and appropriately. Rare errors.
   Band 7: Uses range of complex structures with flexibility. Frequent error-free sentences, though some errors persist.
   Band 5: Produces basic sentence forms and some complex structures. Makes frequent errors but meaning is usually clear.
   Band 3: Attempts basic sentence forms but errors are frequent and may impede meaning.

4. COHERENCE & COHESION (15% of total score):
   - Linking words: because, however, for example, also, then, first, additionally, etc.
   - Logical organization and idea progression
   - Clear referencing and topic development
   
   Band 9: Develops topics fully and appropriately. Uses cohesion skillfully.
   Band 7: Manages cohesion well though occasional inappropriacies. Logical organization.
   Band 5: Overuses or inappropriately uses cohesive devices. May not always be clear or logical.
   Band 3: Presents information simply with limited cohesion. Disconnected ideas.

5. TASK ACHIEVEMENT (20% of total score):
   - Addresses questions fully and relevantly
   - Appropriate response length for each part
   - Extends and develops responses when required
   
   IDEAL LENGTH TARGETS:
   - Part 1 questions: 20-50 words (too short if <10)
   - Part 2 Long Response: 150+ words ideal, 100+ acceptable (too short if <100)
   - Part 2 Rounding-off: 20-50 words (too short if <10)
   - Part 3 questions: 50-100 words (too short if <30)
   
   PENALTIES (already calculated, apply to final Task Achievement score):
   - Irrelevant answers: {metrics.get('irrelevant_count', 0)} × -0.5 = -{metrics.get('irrelevant_count', 0) * 0.5} bands
   - Timeouts: {metrics.get('timeout_count', 0)} × -0.5 = -{metrics.get('timeout_count', 0) * 0.5} bands
   - TOTAL PENALTY: -{total_penalty} bands
   
   Band 9: Fully addresses all tasks with well-developed, extended responses. No irrelevant content.
   Band 7: Addresses all tasks. Some development and detail. Mostly relevant.
   Band 5: Addresses questions but with limited development. Some responses too brief.
   Band 3: Minimal responses, often too brief. May not fully address questions.
   
   IMPORTANT FOR TASK ACHIEVEMENT:
   - Calculate base score (1-9) based on response quality and length
   - Then subtract {total_penalty} for penalties
   - Minimum score after penalties: 1.0

CRITICAL ASSESSMENT GUIDELINES:
- Do NOT penalize isolated errors - assess OVERALL EFFECTIVENESS
- Focus on: "Can they get the job done despite errors?"
- Errors are acceptable if the message is successfully communicated
- Pauses at clause/sentence boundaries are natural and fine
- Mid-clause pauses suggest processing difficulty (more concerning)
- Complex structure attempts with errors are BETTER than only simple structures
- Vocabulary appropriacy matters more than using impressive words randomly

CALCULATE FINAL BAND SCORE:
Final Band = (Fluency×0.25) + (Lexical×0.20) + (Grammar×0.20) + (Cohesion×0.15) + (Task Achievement×0.20)

Return your assessment as valid JSON with this EXACT structure:
{{
  "scores": {{
    "fluency_coherence": {{
      "score": 7.0,
      "justification": "detailed explanation with specific examples from the conversation"
    }},
    "lexical_resource": {{
      "score": 6.5,
      "justification": "detailed explanation",
      "notable_vocabulary": ["example word/phrase", "another example"]
    }},
    "grammatical_range": {{
      "score": 7.0,
      "justification": "detailed explanation",
      "complex_attempts": ["example of complex structure used"]
    }},
    "coherence_cohesion": {{
      "score": 6.5,
      "justification": "detailed explanation",
      "cohesive_devices_used": ["because", "however", "for example"]
    }},
    "task_achievement": {{
      "score": 6.0,
      "justification": "detailed explanation including length assessment",
      "base_score_before_penalties": 7.0,
      "penalties_applied": {total_penalty}
    }}
  }},
  "final_band": 6.6,
  "cefr_level": "B2",
  "strengths": ["specific strength 1", "specific strength 2", "specific strength 3"],
  "areas_for_improvement": ["specific area 1", "specific area 2", "specific area 3"],
  "overall_feedback": "2-3 sentence summary of performance and level"
}}

Return ONLY valid JSON, no other text."""

        # Call GPT-4 for scoring
        response = client.chat.completions.create(
            model=GPT_SCORER_MODEL,
            messages=[
                {"role": "system", "content": scoring_prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent scoring
            response_format={"type": "json_object"}
        )
        
        # Parse JSON response
        result = json.loads(response.choices[0].message.content)
        
        # Validate and add CEFR mapping if not present
        if 'cefr_level' not in result or not result['cefr_level']:
            result['cefr_level'] = map_band_to_cefr(result.get('final_band', 5.0))
        
        return result
        
    except Exception as e:
        # Fallback scoring if GPT fails
        import streamlit as st
        st.error(f"Error during scoring: {str(e)}")
        
        # Return basic fallback scores
        fallback_band = 5.0
        return {
            "scores": {
                "fluency_coherence": {"score": fallback_band, "justification": "Unable to assess - system error"},
                "lexical_resource": {"score": fallback_band, "justification": "Unable to assess - system error"},
                "grammatical_range": {"score": fallback_band, "justification": "Unable to assess - system error"},
                "coherence_cohesion": {"score": fallback_band, "justification": "Unable to assess - system error"},
                "task_achievement": {"score": fallback_band, "justification": "Unable to assess - system error"}
            },
            "final_band": fallback_band,
            "cefr_level": "B1",
            "strengths": ["Completed the test"],
            "areas_for_improvement": ["System error prevented detailed assessment"],
            "overall_feedback": "There was an error scoring your test. Please try again."
        }
