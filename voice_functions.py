"""
Voice-related functions for audio recording, TTS, and STT.
"""

import streamlit as st
import time
from config import client, WHISPER_MODEL, TTS_MODEL, TTS_VOICE, PAUSE_THRESHOLDS


def text_to_speech(text):
    """
    Convert text to speech audio using OpenAI TTS API
    Returns audio bytes that can be played with st.audio()
    """
    try:
        response = client.audio.speech.create(
            model=TTS_MODEL,
            voice=TTS_VOICE,
            input=text
        )
        return response.content
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")
        return None


def transcribe_audio(audio_file, include_timestamps=False):
    """
    Transcribe audio file to text using OpenAI Whisper API
    
    Args:
        audio_file: Audio file to transcribe
        include_timestamps: If True, returns dict with text and word-level timestamps
    
    Returns:
        If include_timestamps=False: Just the transcribed text string
        If include_timestamps=True: Dict with 'text', 'words' (list of {word, start, end})
    """
    try:
        # audio_file is already a file-like object from st.audio_input()
        if include_timestamps:
            # Request word-level timestamps
            transcript = client.audio.transcriptions.create(
                model=WHISPER_MODEL,
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )
            
            # Check if transcription is empty
            transcribed_text = transcript.text.strip() if hasattr(transcript, 'text') else ""
            
            if not transcribed_text or len(transcribed_text) < 3:
                return {
                    'text': "[No speech detected]",
                    'words': [],
                    'duration': 0
                }
            
            # Extract word-level timestamps
            words = []
            if hasattr(transcript, 'words') and transcript.words:
                words = [
                    {
                        'word': w.word,
                        'start': w.start,
                        'end': w.end
                    }
                    for w in transcript.words
                ]
            
            return {
                'text': transcribed_text,
                'words': words,
                'duration': words[-1]['end'] if words else 0
            }
        else:
            # Standard transcription (text only)
            transcript = client.audio.transcriptions.create(
                model=WHISPER_MODEL,
                file=audio_file
            )
            
            # Check if transcription is empty or just whitespace/noise
            transcribed_text = transcript.text.strip()
            
            # If no meaningful words were transcribed, return a default message
            # that will be caught as irrelevant by the relevance checker
            if not transcribed_text or len(transcribed_text) < 3:
                return "[No speech detected]"
            
            return transcribed_text
            
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        if include_timestamps:
            return {'text': None, 'words': [], 'duration': 0}
        return None


def store_voice_timing_data(part, question, answer, timing_result):
    """
    Store timing data for voice mode answers
    
    Args:
        part: Part name (e.g., "Part 1", "Part 2 Long Response", etc.)
        question: The question text
        answer: The answer text
        timing_result: Dict with 'words', 'duration' from transcribe_audio
    """
    if not isinstance(timing_result, dict) or not timing_result.get('words'):
        return
    
    word_count = len(answer.split())
    duration = timing_result.get('duration', 0)
    wpm = (word_count / duration * 60) if duration > 0 else 0
    
    # Calculate pauses
    pauses = []
    words_data = timing_result.get('words', [])
    min_pause = PAUSE_THRESHOLDS['min_pause']
    long_pause_threshold = PAUSE_THRESHOLDS['long_pause']
    
    for i in range(len(words_data) - 1):
        pause_length = words_data[i+1]['start'] - words_data[i]['end']
        if pause_length > min_pause:
            pauses.append(round(pause_length, 2))
    
    st.session_state.voice_timing_data.append({
        'part': part,
        'question': question[:100] + '...' if len(question) > 100 else question,
        'answer': answer[:100] + '...' if len(answer) > 100 else answer,
        'full_answer': answer,  # Store full answer for matching
        'word_count': word_count,
        'duration': round(duration, 1),
        'wpm': round(wpm, 1),
        'pauses': pauses,
        'num_pauses': len(pauses),
        'avg_pause': round(sum(pauses) / len(pauses), 2) if pauses else 0,
        'long_pauses': len([p for p in pauses if p > long_pause_threshold]),
        'words_data': words_data  # Store full word-level timestamps
    })


def get_voice_timer_limit(part_type):
    """
    Get the time limit in seconds for voice mode based on part type
    """
    limits = {
        'part1': 30,
        'part2_long': 120,
        'part2_rounding': 30,
        'part3': 60
    }
    return limits.get(part_type, 30)


def check_voice_timer_expired(start_time, limit_seconds):
    """
    Check if the voice mode timer has expired
    Returns (expired: bool, elapsed: float, remaining: float)
    """
    if start_time is None:
        return False, 0, limit_seconds
    
    elapsed = time.time() - start_time
    remaining = limit_seconds - elapsed
    expired = elapsed >= limit_seconds
    
    return expired, elapsed, max(0, remaining)


def format_time(seconds):
    """
    Format seconds into M:SS format
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"
