from fastapi import APIRouter, Depends, HTTPException, status

from schemas.session import (
    CreateSessionRequest,
    AnswerRequest
)

from services.session_service import (
    create_session,
    get_session_details,
    submit_answer
)

from utils.auth import get_current_user


router = APIRouter(
    prefix="/api/sessions",
    tags=["Form Sessions"]
)

@router.post("/")
def create_new_session(
    data: CreateSessionRequest,
    user=Depends(get_current_user)
):
    if not user["verified"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify yourself before filling a form."
        )

    try:
        session = create_session(
            user["id"],
            data.form_id
        )

        return {
            "message": "Session created successfully",
            "session": session
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{session_id}")
def get_existing_session(
    session_id: int,
    user=Depends(get_current_user)
):

    session = get_session_details(
        session_id,
        user["id"]
    )

    if session is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return session


@router.post("/{session_id}/answers")
def submit_session_answer(
    session_id: int,
    data: AnswerRequest,
    user=Depends(get_current_user)
):

    try:

        session = submit_answer(
            session_id,
            user["id"],
            data.field_id,
            data.value
        )

        return {
            "message": "Answer saved successfully",
            "session": session
        }

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )