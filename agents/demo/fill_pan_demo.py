"""
End-to-end demo/test for the PDF-filling stage of the PAN Form 93 flow,
against the live Exasol database.

  1. Fetches the real PAN Form 93 field definitions from Exasol
     (FORM_KB.FORM_FIELD) — whatever fields actually exist there.
  2. Runs them through the real, unmodified agents.qa.agent.QAAgent.
  3. Only calls agents.filler.fill_form(...) if QA passes, exactly
     like the intended production flow.

Run from the repository root:
    python -m agents.demo.fill_pan_demo
"""

from __future__ import annotations

import os

from agents.database import ExasolClient
from agents.filler import PdfFillError, fill_form
from agents.models import FormField
from agents.qa.agent import QAAgent

PAN_FORM_ID = 2

MAPPING_PATH = os.path.join(
    os.path.dirname(__file__), "..", "mappings", "pan_form_93.json"
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def load_pan_fields(db: ExasolClient) -> list[FormField]:
    rows = db.execute(
        f"""
        SELECT field_id, field_code, field_label, field_type, is_required,
               field_order, explanation, example_value, validation_pattern,
               min_length, max_length
        FROM FORM_KB.FORM_FIELD
        WHERE form_id = {PAN_FORM_ID}
        ORDER BY field_order
        """
    )

    return [
        FormField(
            field_id=r["FIELD_ID"],
            field_code=r["FIELD_CODE"],
            field_label=r["FIELD_LABEL"],
            field_type=r["FIELD_TYPE"],
            is_required=bool(r["IS_REQUIRED"]),
            field_order=r["FIELD_ORDER"],
            explanation=r["EXPLANATION"],
            example_value=r["EXAMPLE_VALUE"],
            validation_pattern=r["VALIDATION_PATTERN"],
            min_length=r["MIN_LENGTH"],
            max_length=r["MAX_LENGTH"],
        )
        for r in rows
    ]


def run_case(title: str, fields: list[FormField], db: ExasolClient, answers: dict) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    qa = QAAgent(db=db)
    qa_result = qa.validate(form_id=PAN_FORM_ID, fields=fields, answers=answers)

    print(f"QA valid: {qa_result.valid}  risk_level: {qa_result.risk_level}")

    for issue in qa_result.blocking_issues:
        print(f"  BLOCKING: [{issue['field']}] {issue['issue']}")

    if not qa_result.valid:
        print("QA blocked this submission -> PDF will NOT be generated.")
        return

    try:
        pdf_bytes = fill_form(MAPPING_PATH, answers)
    except PdfFillError as exc:
        print(f"PDF FILL FAILED: {exc}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "pan_form_93_filled.pdf")

    with open(out_path, "wb") as fh:
        fh.write(pdf_bytes)

    print(f"PDF generated: {out_path} ({len(pdf_bytes)} bytes)")
    print("Form ready! Please carefully check the completed form before submitting it.")


def main():
    db = ExasolClient()

    try:
        fields = load_pan_fields(db)
        print(f"Loaded {len(fields)} live field definitions for PAN Form 93")

        valid_answers = {
            "PAN_NAME": "Aditya Mishra",
            "PAN_DOB": "01/01/2002",
            "PAN_FATHER": "Rajesh Mishra",
            "PAN_MOTHER": "Sunita Mishra",
            "PAN_SINGLE_PARENT": "No",
            "PAN_GENDER": "Male",
            "PAN_RESIDENTIAL_STATUS": "Resident",
            "PAN_ADDRESS": "Plot 401, Sahid Nagar, Bhubaneswar",
            "PAN_STATE": "Odisha",
            "PAN_PIN": "751007",
            "PAN_EMAIL": "aditya@example.com",
            "PAN_PHONE": "9876543210",
            "PAN_HAS_OFFICE_ADDRESS": "Yes",
            "PAN_OFFICE_ADDRESS": "Infocity Tower, Patia, Bhubaneswar",
            "PAN_HAS_REPRESENTATIVE": "No",
            # The real session flow auto-answers this with the same
            # sentinel once PAN_HAS_REPRESENTATIVE is "No" (see
            # session_service.CONDITIONAL_FIELDS) — supplied directly
            # here since this script calls QAAgent standalone.
            "PAN_REPRESENTATIVE_NAME": "Not Applicable",
            "PAN_SOURCE_INCOME": "Salary",
            "PAN_PRINT_PARENT": "Father",
            "PAN_PROOF_DOCS": "identity, address, date of birth",
        }

        run_case("CASE 1: Complete, valid profile (with new fields)", fields, db, valid_answers)

        invalid_answers = dict(valid_answers)
        invalid_answers["PAN_DOB"] = "2002-01-01"  # wrong format (not DD/MM/YYYY)
        invalid_answers["PAN_EMAIL"] = "not-an-email"  # fails email pattern
        invalid_answers["PAN_PHONE"] = "98765"  # too short, fails 10-digit pattern

        run_case("CASE 2: Invalid DOB / email / phone", fields, db, invalid_answers)

    finally:
        db.close()


if __name__ == "__main__":
    main()
