"""
Configuration and constants for the IELTS Speaking Assessment application.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Model configuration
GPT_EXAMINER_MODEL = "gpt-4o-mini"
GPT_SCORER_MODEL = "gpt-4o"
TTS_MODEL = "tts-1"
TTS_VOICE = "alloy"
WHISPER_MODEL = "whisper-1"

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
    "an event",
    "an activity",
    "media (book/film/music)",
    "a decision",
    "a journey"
]

# Word limits by part
WORD_LIMITS = {
    'part1': 65,
    'part2_long': 400,
    'part2_rounding': 65,
    'part3': 150
}

# Ideal word count ranges for scoring
IDEAL_WORD_COUNTS = {
    'part1': {'min': 20, 'max': 50},
    'part2_long': {'min': 150, 'acceptable_min': 100},
    'part2_rounding': {'min': 20, 'max': 50},
    'part3': {'min': 50, 'max': 100}
}

# Timer settings (in seconds)
TIMER_SETTINGS = {
    'part1_text': {'check_in': 30, 'auto_skip': 60},
    'part1_voice': {'display': 30, 'actual': 40},
    'part2_prep': 60,
    'part2_long_text': {'check_in': 60, 'auto_skip': 120},
    'part2_long_voice': {'display': 120, 'actual': 130},
    'part2_rounding_text': {'check_in': 30, 'auto_skip': 60},
    'part2_rounding_voice': {'display': 30, 'actual': 40},
    'part3_text': {'check_in': 40, 'auto_skip': 80},
    'part3_voice': {'display': 60, 'actual': 70}
}

# Scoring weights (must sum to 100)
SCORING_WEIGHTS = {
    'fluency_coherence': 25,
    'lexical_resource': 20,
    'grammatical_range': 20,
    'coherence_cohesion': 15,
    'task_achievement': 20
}

# Pause detection thresholds (in seconds)
PAUSE_THRESHOLDS = {
    'min_pause': 0.3,  # Minimum pause to count
    'long_pause': 1.5,  # Threshold for "long" pause
    'display_pause': 0.5  # Minimum pause to show in transcript
}

# WPM (Words Per Minute) ranges for assessment
WPM_RANGES = {
    'very_slow': (0, 80),
    'slow': (80, 120),
    'normal': (120, 160),
    'fast': (160, 200),
    'very_fast': (200, 300)
}

# Relevance score threshold
RELEVANCE_THRESHOLD = 0.65
