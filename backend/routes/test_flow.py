"""
Test flow routes — start, submit answer, skip, next part, score.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.services.session_store import get_session
from backend.services import test_engine

router = APIRouter(prefix="/api/test", tags=["test"])


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class StartRequest(BaseModel):
    session_id: str
    mode: str  # 'text' or 'voice'


class AnswerRequest(BaseModel):
    session_id: str
    answer: str


class SkipRequest(BaseModel):
    session_id: str
    phase: Optional[str] = None  # For Part 2: 'long_response' or 'rounding'


class SessionOnly(BaseModel):
    session_id: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_session_or_404(session_id: str):
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/start")
def start_test(req: StartRequest):
    """Set mode, init Part 1, return first question."""
    session = _get_session_or_404(req.session_id)
    if req.mode not in ('text', 'voice'):
        raise HTTPException(status_code=400, detail="Mode must be 'text' or 'voice'")
    return test_engine.start_test(session, req.mode)


@router.post("/answer")
def submit_answer(req: AnswerRequest):
    """Submit an answer for the current step."""
    session = _get_session_or_404(req.session_id)
    step = session.get('step', '')

    if step == 'PART_1':
        return test_engine.submit_answer_part1(session, req.answer)
    elif step == 'PART_2':
        if session.get('part2_waiting_for_rounding_answer'):
            return test_engine.submit_rounding_answer(session, req.answer)
        else:
            return test_engine.submit_long_response(session, req.answer)
    elif step == 'PART_3':
        return test_engine.submit_answer_part3(session, req.answer)
    else:
        raise HTTPException(status_code=400, detail=f"Cannot submit answer in step: {step}")


@router.post("/skip")
def skip(req: SkipRequest):
    """Handle timeout (records [No response])."""
    session = _get_session_or_404(req.session_id)
    step = session.get('step', '')

    if step == 'PART_1':
        return test_engine.skip_answer_part1(session)
    elif step == 'PART_2':
        phase = req.phase or 'rounding'
        return test_engine.skip_answer_part2(session, phase)
    elif step == 'PART_3':
        return test_engine.skip_answer_part3(session)
    else:
        raise HTTPException(status_code=400, detail=f"Cannot skip in step: {step}")


@router.post("/next-part")
def next_part(req: SessionOnly):
    """Transition to the next part."""
    session = _get_session_or_404(req.session_id)
    step = session.get('step', '')

    if step == 'PART_1':
        session['step'] = 'PART_2'
        return test_engine.start_part2(session)
    elif step == 'PART_2':
        session['step'] = 'PART_3'
        return test_engine.start_part3(session)
    elif step == 'PART_3':
        session['step'] = 'SCORING'
        return test_engine.calculate_scores(session)
    else:
        raise HTTPException(status_code=400, detail=f"Cannot advance from step: {step}")


@router.post("/skip-prep")
def skip_prep(req: SessionOnly):
    """Skip Part 2 prep phase."""
    session = _get_session_or_404(req.session_id)
    if session.get('step') != 'PART_2':
        raise HTTPException(status_code=400, detail="Not in Part 2")
    return test_engine.skip_prep(session)


@router.post("/complete-prep")
def complete_prep(req: SessionOnly):
    """Mark Part 2 prep as complete (timer expired)."""
    session = _get_session_or_404(req.session_id)
    if session.get('step') != 'PART_2':
        raise HTTPException(status_code=400, detail="Not in Part 2")
    return test_engine.complete_prep(session)


@router.post("/score")
def score(req: SessionOnly):
    """Calculate final scores."""
    session = _get_session_or_404(req.session_id)
    return test_engine.calculate_scores(session)
