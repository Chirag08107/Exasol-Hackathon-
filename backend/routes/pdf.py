from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response

from services.pdf_service import PdfGenerationError, generate_session_pdf
from utils.auth import get_current_user

router = APIRouter(
    prefix="/api/sessions",
    tags=["Form PDF"]
)


READY_MESSAGE = (
    "Form ready! Please carefully check the completed form before "
    "submitting it."
)

REVIEW_MESSAGE = (
    "Review all details carefully. If a hard copy is required, print "
    "and submit it yourself. If an online upload is required, upload "
    "it yourself. This assistant does not submit forms on your behalf."
)


@router.get("/{session_id}/pdf")
def get_session_pdf(
    session_id: int,
    user=Depends(get_current_user)
):
    try:
        pdf_bytes = generate_session_pdf(session_id, user["id"])

    except PdfGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="form_{session_id}.pdf"',
            "X-Form-Message": READY_MESSAGE,
            "X-Form-Review-Note": REVIEW_MESSAGE,
        },
    )
