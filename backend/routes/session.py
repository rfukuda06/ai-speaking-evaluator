"""
Session management routes.
"""

from fastapi import APIRouter, HTTPException
from backend.services.session_store import create_session, get_session, delete_session, reset_session

router = APIRouter(prefix="/api/session", tags=["session"])


@router.post("")
def create():
    """Create a new session."""
    sid = create_session()
    return {"session_id": sid}


@router.get("/{session_id}")
def get(session_id: str):
    """Get full session state."""
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session_id,
        "step": session.get("step"),
        "test_mode": session.get("test_mode"),
    }


@router.delete("/{session_id}")
def delete(session_id: str):
    """Delete / reset a session (retake test)."""
    if not reset_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "reset"}
