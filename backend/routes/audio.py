"""
Audio routes — TTS and Whisper transcription.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import Response, StreamingResponse
from backend.services.session_store import get_session
from backend.voice_functions import text_to_speech, transcribe_audio, store_voice_timing_data
from config import client, TTS_MODEL, TTS_VOICE
import io

router = APIRouter(prefix="/api/audio", tags=["audio"])


@router.post("/tts")
def tts_post(text: str = Form(...)):
    """Text-to-speech (POST). Streams audio/mpeg bytes as they arrive from OpenAI."""
    return _stream_tts(text)


@router.get("/tts")
def tts_get(text: str):
    """Text-to-speech (GET). Browser can stream playback directly via <audio src>."""
    return _stream_tts(text)


def _stream_tts(text: str):
    try:
        response = client.audio.speech.create(
            model=TTS_MODEL,
            voice=TTS_VOICE,
            input=text,
        )
        return StreamingResponse(
            response.iter_bytes(chunk_size=4096),
            media_type="audio/mpeg",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {e}")


@router.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    session_id: str = Form(""),
    include_timestamps: bool = Form(False),
    part: str = Form(""),
    question: str = Form(""),
):
    """
    Whisper STT. Accepts multipart audio file.
    Optionally stores voice timing data if session_id, part, and question are provided.
    """
    contents = await file.read()
    audio_file = io.BytesIO(contents)
    audio_file.name = file.filename or "audio.webm"

    result = transcribe_audio(audio_file, include_timestamps=include_timestamps)

    if result is None:
        raise HTTPException(status_code=500, detail="Transcription failed")

    # Store timing data if session context is provided
    if session_id and part and question and include_timestamps and isinstance(result, dict):
        session = get_session(session_id)
        if session:
            text = result.get('text', '')
            if text and text != "[No speech detected]":
                store_voice_timing_data(
                    session.get('voice_timing_data', []),
                    part, question, text, result
                )

    return result
