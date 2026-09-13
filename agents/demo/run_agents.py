import json
from pathlib import Path

from agents.database import ExasolClient
from agents.detective import DetectiveAgent
from agents.researcher import ResearcherAgent
from agents.guide import GuideAgent
from agents.qa import QAAgent
from agents.models import UserProfile


PDF_PATH = Path(__file__).parent / "sample_form.pdf"


def main():

    # -----------------------------------------
    # Database
    # -----------------------------------------

    db = ExasolClient()

    try:

        # -------------------------------------
        # 1. DETECTIVE
        # -------------------------------------

        print("\n==============================")
        print("1. DETECTIVE AGENT")
        print("==============================")

        pdf_data = PDF_PATH.read_bytes()

        detective = DetectiveAgent(db)

        detective_result = detective.detect_from_pdf(
            pdf_data
        )

        print(
            json.dumps(
                detective_result.model_dump(),
                indent=2,
                default=str,
            )
        )

        if not detective_result.success:
            print(
                "\nDetective could not identify the form."
            )
            return

        form = detective_result.form

        # -------------------------------------
        # 2. RESEARCHER
        # -------------------------------------

        print("\n==============================")
        print("2. RESEARCHER AGENT")
        print("==============================")

        researcher = ResearcherAgent(db)

        research_result = researcher.research(
            form_id=form.form_id,
            form_code=form.form_code,
        )

        print(
            json.dumps(
                research_result.model_dump(),
                indent=2,
                default=str,
            )
        )

        # -------------------------------------
        # 3. GUIDE
        # -------------------------------------

        print("\n==============================")
        print("3. GUIDE AGENT")
        print("==============================")

        profile = UserProfile(
            personal_information={
                "full_name": "Aditya Mishra",
                "date_of_birth": "2002-01-01",
                "phone": "9876543210",
                "email": "aditya@example.com",
                "address": "Bhubaneswar",
                "state": "Odisha",
                "pincode": "751001",
                "gender": "Male",
                "residential_status": "Resident",
            },
            education={
                "highest_qualification": "B.Tech"
            },
            additional_details={
                "father_name": "Rajesh Mishra"
            },
        )

        guide = GuideAgent()

        guide_result = guide.process(
            fields=detective_result.fields,
            profile=profile,
            answers={},
        )

        print(
            json.dumps(
                guide_result.model_dump(),
                indent=2,
                default=str,
            )
        )

        # -------------------------------------
        # 4. QA
        # -------------------------------------

        print("\n==============================")
        print("4. QA AGENT")
        print("==============================")

        answers = {}

        for action in guide_result.actions:

            if action.action == "fill":

                answers[
                    action.field_code
                ] = action.value

        print("\nDEBUG - ANSWERS SENT TO QA:")
        print(json.dumps(answers, indent=2, default=str))

        qa = QAAgent(db)

        qa_result = qa.validate(
            form_id=form.form_id,
            fields=detective_result.fields,
            answers=answers,
        )

        print(
            json.dumps(
                qa_result.model_dump(),
                indent=2,
                default=str,
            )
        )

    finally:

        db.close()


if __name__ == "__main__":
    main()
