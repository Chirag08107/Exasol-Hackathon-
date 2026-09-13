"""
True end-to-end demo: Detective -> Researcher -> Guide -> QA -> PDF
filler, all running against the LIVE Exasol database (no stand-ins).

This is the capstone test for the backend<->agents integration: it
proves the exact canonical answers produced by the real, unmodified
agents pipeline are consumable as-is by agents.filler.fill_form().

Run from the repository root:
    python -m agents.demo.full_pipeline_pan_demo
"""

import json
import os
from pathlib import Path

from agents.database import ExasolClient
from agents.detective import DetectiveAgent
from agents.researcher import ResearcherAgent
from agents.guide import GuideAgent
from agents.qa.agent import QAAgent
from agents.models import UserProfile
from agents.filler import PdfFillError, fill_form

PDF_PATH = Path(__file__).parent / "sample_form.pdf"
MAPPING_PATH = os.path.join(os.path.dirname(__file__), "..", "mappings", "pan_form_93.json")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "output", "pan_form_93_live_pipeline.pdf")


def main():
    db = ExasolClient()

    try:
        # 1. DETECTIVE — identify the form from the PDF, live against Exasol
        detective = DetectiveAgent(db)
        detective_result = detective.detect_from_pdf(PDF_PATH.read_bytes())

        print(f"Detective: form={detective_result.form.form_code!r} "
              f"confidence={detective_result.confidence}")

        if not detective_result.success:
            print("Detective could not identify the form.")
            return

        form = detective_result.form

        # 2. RESEARCHER — pull real requirements/documents/rules
        researcher = ResearcherAgent(db)
        research_result = researcher.research(form_id=form.form_id, form_code=form.form_code)
        print(f"Researcher: {len(research_result.required_documents)} documents, "
              f"{len(research_result.rules)} rules found")

        # 3. GUIDE — fill from a demo profile (this is the only stand-in:
        # in production this profile comes from the logged-in user)
        profile = UserProfile(
            personal_information={
                "full_name": "Aditya Mishra",
                "date_of_birth": "2002-01-01",
                "phone": "9876543210",
                "email": "aditya@example.com",
                "address": "Bhubaneswar",
                "gender": "Male",
                "residential_status": "Resident",
            },
            additional_details={"father_name": "Rajesh Mishra"},
        )

        guide = GuideAgent()
        guide_result = guide.process(fields=detective_result.fields, profile=profile, answers={})
        print(f"Guide: {guide_result.progress}, {len(guide_result.questions)} still needed")

        answers = {
            action.field_code: action.value
            for action in guide_result.actions
            if action.action == "fill"
        }

        # 4. QA — validate against Exasol's real FORM_RULE rows too
        qa = QAAgent(db)
        qa_result = qa.validate(form_id=form.form_id, fields=detective_result.fields, answers=answers)

        print(f"QA: valid={qa_result.valid} risk={qa_result.risk_level}")

        if not qa_result.valid:
            print("QA blocked this submission:")
            print(json.dumps(qa_result.blocking_issues, indent=2))
            return

        # 5. FILLER — the new stage, consuming QA-validated answers as-is
        try:
            pdf_bytes = fill_form(MAPPING_PATH, answers)
        except PdfFillError as exc:
            print(f"PDF FILL FAILED: {exc}")
            return

        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        with open(OUTPUT_PATH, "wb") as fh:
            fh.write(pdf_bytes)

        print(f"\nPDF generated from the LIVE pipeline: {OUTPUT_PATH} ({len(pdf_bytes)} bytes)")
        print("Form ready! Please carefully check the completed form before submitting it.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
