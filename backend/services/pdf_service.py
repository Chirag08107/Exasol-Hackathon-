"""
Wires the generic PDF filler (agents/filler) into the existing session
flow. Every database access here is a read-only SELECT — this module
never inserts/updates/deletes anything in Exasol; it only reads
answers that were already written by the existing session/answer
endpoints (services/session_service.py), which this module does not
modify.
"""

import os
import sys

# agents/ lives at the repo root, as a sibling of backend/, so it is
# not on backend's sys.path by default (backend runs with its own
# directory as the import root, e.g. `from routes.health import ...`).
_REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from agents.database import ExasolClient  # noqa: E402
from agents.filler import PdfFillError, fill_form  # noqa: E402
from agents.models import FormField  # noqa: E402
from agents.qa.agent import QAAgent  # noqa: E402

from database.exasol import get_connection
from services.form_service import get_form_by_id, get_form_fields
from services.session_service import get_session_details


# Which mapping file to use for a given form_code. Only PAN Form 93
# has a mapping today; any other form_code simply isn't supported yet
# (see agents/mappings/README.md for how to add one).
# "PAN_FORM_93" is the real form_code in Exasol (FORM_KB.FORM, form_id
# 2) — confirmed directly against the live database. The rest are kept
# as fallback aliases in case the dataset is ever reseeded differently.
_FORM_CODE_MAPPINGS = {
    "PAN_FORM_93": "agents/mappings/pan_form_93.json",
    "93": "agents/mappings/pan_form_93.json",
    "FORM_93": "agents/mappings/pan_form_93.json",
    "FORM 93": "agents/mappings/pan_form_93.json",
    "FORM93": "agents/mappings/pan_form_93.json",
    "PAN": "agents/mappings/pan_form_93.json",
    "49AA": "agents/mappings/pan_form_93.json",
}


class PdfGenerationError(Exception):
    """Raised for any reason the requested session's PDF cannot be
    produced (not found, not complete, unsupported form, bad data)."""


def _mapping_path_for(form_code) -> str | None:
    if not form_code:
        return None

    rel_path = _FORM_CODE_MAPPINGS.get(str(form_code).strip().upper())

    if not rel_path:
        return None

    return os.path.join(_REPO_ROOT, rel_path)


def get_session_answers(session_id: int, form_id: int) -> dict:
    """Read-only: canonical field_code -> answer_value for every
    answered field in this session."""

    fields = get_form_fields(form_id)
    field_code_by_id = {f["field_id"]: f["field_code"] for f in fields}

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT field_id, answer_value
            FROM FORM_APP.FORM_ANSWER
            WHERE session_id = {session_id}
            """,
            {"session_id": session_id},
        ).fetchall()
    finally:
        connection.close()

    answers = {}

    for row in rows:
        field_id, value = row[0], row[1]
        code = field_code_by_id.get(field_id)

        if code:
            answers[code] = value

    return answers


def _run_qa_gate(form_id: int, answers: dict) -> None:
    """
    Extra safety net using the real, unmodified agents.qa.agent.QAAgent
    — the same validation the standalone agents pipeline runs — as a
    second check in front of PDF generation, on top of whatever
    session_service.py already enforced field-by-field. This is
    read-only: QAAgent only SELECTs from FORM_KB.FORM_RULE.

    session_service.py's own per-answer validation already normally
    prevents bad data from reaching this point; this gate exists so a
    PDF is never generated from data QAAgent itself would flag, even
    if the two validation paths ever drift apart.
    """

    raw_fields = get_form_fields(form_id)

    fields = [
        FormField(
            field_id=f["field_id"],
            field_code=f["field_code"],
            field_label=f["field_label"],
            field_type=f.get("field_type"),
            section_name=f.get("section_name"),
            is_required=bool(f.get("is_required")),
            field_order=f.get("field_order"),
            explanation=f.get("explanation"),
            example_value=f.get("example_value"),
            validation_pattern=f.get("validation_pattern"),
            min_length=f.get("min_length"),
            max_length=f.get("max_length"),
        )
        for f in raw_fields
    ]

    qa_db = ExasolClient()

    try:
        qa_result = QAAgent(qa_db).validate(form_id=form_id, fields=fields, answers=answers)
    finally:
        qa_db.close()

    if not qa_result.valid:
        reasons = "; ".join(
            f"{issue['field']}: {issue['issue']}" for issue in qa_result.blocking_issues
        )
        raise PdfGenerationError(
            f"This form did not pass validation and cannot be turned "
            f"into a PDF yet — {reasons}"
        )


def generate_session_pdf(session_id: int, user_id: int) -> bytes:
    """
    Produce the filled PDF for a completed session. Raises
    PdfGenerationError with a human-readable reason if it can't.
    """

    session = get_session_details(session_id, user_id)

    if session is None:
        raise PdfGenerationError("Session not found")

    if session["status"] != "completed":
        raise PdfGenerationError(
            "This form isn't fully answered yet — please answer every "
            "field before generating the PDF."
        )

    form = get_form_by_id(session["form_id"])

    if form is None:
        raise PdfGenerationError("Form not found")

    mapping_path = _mapping_path_for(form.get("form_code"))

    if mapping_path is None:
        raise PdfGenerationError(
            f"PDF generation isn't available yet for "
            f"'{form.get('form_name') or form.get('form_code')}'. "
            f"Only the PAN application (Form 93) is supported so far."
        )

    answers = get_session_answers(session_id, session["form_id"])

    _run_qa_gate(session["form_id"], answers)

    try:
        return fill_form(mapping_path, answers)
    except PdfFillError as exc:
        raise PdfGenerationError(str(exc)) from exc
