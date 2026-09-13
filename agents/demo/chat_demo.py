import json
import re
from difflib import SequenceMatcher

from agents.database import ExasolClient
from agents.researcher import ResearcherAgent
from agents.guide import GuideAgent
from agents.qa import QAAgent
from agents.models import UserProfile, FormField


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(text: str) -> str:
    """
    Normalize text for form-name matching.
    """

    text = str(text or "").lower().strip()

    replacements = {
        "aadhar": "aadhaar",
        "adhar": "aadhaar",
        "pan card": "pan",
        "permanent account number": "pan",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


# =========================================================
# FORM INTENT DETECTION
# =========================================================

def detect_form_intent(
    db: ExasolClient,
    user_message: str,
) -> dict | None:
    """
    Search all forms stored in Exasol and identify
    the best matching form for the user's request.
    """

    user_text = normalize_text(user_message)

    if not user_text:
        return None

    # -----------------------------------------------------
    # Load ALL forms from Exasol
    # -----------------------------------------------------

    forms = db.execute("""
        SELECT
            form_id,
            form_code,
            form_name,
            category,
            sub_category,
            authority,
            country,
            description
        FROM FORM_KB.FORM
    """)

    if not forms:
        return None

    # -----------------------------------------------------
    # Ignore common conversational words
    # -----------------------------------------------------

    stop_words = {
        "i",
        "want",
        "to",
        "fill",
        "the",
        "a",
        "an",
        "form",
        "forms",
        "application",
        "apply",
        "for",
        "my",
        "please",
        "help",
        "me",
        "with",
        "need",
        "complete",
        "submit",
        "get",
        "make",
        "do",
        "this",
    }

    user_tokens = {
        token
        for token in user_text.split()
        if token not in stop_words
    }

    if not user_tokens:
        user_tokens = set(user_text.split())

    best_form = None
    best_score = 0.0

    # -----------------------------------------------------
    # Compare user request against every form
    # -----------------------------------------------------

    for form in forms:

        form_name = normalize_text(
            form["FORM_NAME"]
        )

        form_code = normalize_text(
            form["FORM_CODE"]
        )

        category = normalize_text(
            form["CATEGORY"]
        )

        sub_category = normalize_text(
            form["SUB_CATEGORY"]
        )

        description = normalize_text(
            form["DESCRIPTION"]
        )

        # -------------------------------------------------
        # Build searchable representation
        # -------------------------------------------------

        searchable_text = " ".join([
            form_name,
            form_code,
            category,
            sub_category,
            description,
        ])

        form_tokens = set(searchable_text.split())

        # -------------------------------------------------
        # Token overlap
        # -------------------------------------------------

        overlap = user_tokens.intersection(form_tokens)

        token_score = (
            len(overlap) / len(user_tokens)
            if user_tokens
            else 0.0
        )

        # -------------------------------------------------
        # Form-name similarity
        # -------------------------------------------------

        name_similarity = SequenceMatcher(
            None,
            user_text,
            form_name,
        ).ratio()

        # -------------------------------------------------
        # Exact phrase match
        # -------------------------------------------------

        exact_phrase_score = 0.0

        if form_name and form_name in user_text:
            exact_phrase_score = 1.0

        # -------------------------------------------------
        # Tokens specifically matching form name
        # -------------------------------------------------

        name_tokens = set(form_name.split())

        name_overlap = user_tokens.intersection(
            name_tokens
        )

        name_token_score = (
            len(name_overlap) / len(user_tokens)
            if user_tokens
            else 0.0
        )

        # -------------------------------------------------
        # Final score
        # -------------------------------------------------

        score = max(
            token_score,
            name_similarity * 0.8,
            exact_phrase_score,
            name_token_score + 0.15
            if name_overlap
            else 0.0,
        )

        score = min(score, 1.0)

        if score > best_score:

            best_score = score
            best_form = form

    # -----------------------------------------------------
    # Minimum confidence threshold
    # -----------------------------------------------------

    if best_form is None or best_score < 0.35:
        return None

    return {
        "form": best_form,
        "confidence": round(best_score, 2),
    }


# =========================================================
# LOAD FORM FIELDS
# =========================================================

def load_form_fields(
    db: ExasolClient,
    form_id: int,
) -> list[FormField]:
    """
    Load the fields belonging to the selected form.
    """

    rows = db.execute(f"""
        SELECT
            field_id,
            field_code,
            field_label,
            field_type,
            section_name,
            is_required,
            field_order,
            explanation,
            example_value,
            validation_pattern,
            min_length,
            max_length
        FROM FORM_KB.FORM_FIELD
        WHERE form_id = {int(form_id)}
        ORDER BY field_order
    """)

    fields = []

    for row in rows:

        fields.append(
            FormField(
                field_id=row["FIELD_ID"],
                field_code=row["FIELD_CODE"],
                field_label=row["FIELD_LABEL"],
                field_type=row["FIELD_TYPE"],
                section_name=row["SECTION_NAME"],
                is_required=bool(
                    row["IS_REQUIRED"]
                ),
                field_order=row["FIELD_ORDER"],
                explanation=row["EXPLANATION"],
                example_value=row["EXAMPLE_VALUE"],
                validation_pattern=row[
                    "VALIDATION_PATTERN"
                ],
                min_length=row["MIN_LENGTH"],
                max_length=row["MAX_LENGTH"],
            )
        )

    return fields


# =========================================================
# LOAD FIELD OPTIONS
# =========================================================

def load_field_options(
    db: ExasolClient,
    field_id: int,
) -> list[str]:
    """
    Dynamically load selectable options for a field.
    """

    rows = db.execute(f"""
        SELECT
            option_label
        FROM FORM_KB.FIELD_OPTION
        WHERE field_id = {int(field_id)}
        ORDER BY option_id
    """)

    return [
        str(row["OPTION_LABEL"])
        for row in rows
    ]


# =========================================================
# DISPLAY FIELD OPTIONS
# =========================================================

def ask_for_field(
    db: ExasolClient,
    field: FormField,
) -> str:
    """
    Ask the user for a missing field.

    If the field has options in Exasol, display them.
    Otherwise accept free-form input.
    """

    print()

    print(
        f"Assistant: What should I enter for "
        f"'{field.field_label}'?"
    )

    if field.explanation:

        print(
            f"Assistant: {field.explanation}"
        )

    # -----------------------------------------------------
    # Load options dynamically
    # -----------------------------------------------------

    options = []

    if field.field_id is not None:

        options = load_field_options(
            db,
            field.field_id,
        )

    # -----------------------------------------------------
    # Select field
    # -----------------------------------------------------

    if options:

        print()

        for index, option in enumerate(
            options,
            start=1,
        ):

            print(
                f"  {index}. {option}"
            )

        while True:

            response = input(
                "You: "
            ).strip()

            # Numeric selection
            if response.isdigit():

                index = int(response)

                if 1 <= index <= len(options):

                    return options[index - 1]

            # Direct option text
            for option in options:

                if (
                    response.lower()
                    == option.lower()
                ):

                    return option

            print(
                "Assistant: Please select "
                "one of the available options."
            )

    # -----------------------------------------------------
    # Free-text field
    # -----------------------------------------------------

    return input(
        "You: "
    ).strip()


# =========================================================
# DISPLAY DETECTED FORM
# =========================================================

def display_form_information(
    form: dict,
    confidence: float,
) -> None:

    print()

    print(
        "Assistant: I identified this as "
        f"{form['FORM_NAME']}."
    )

    print(
        f"Assistant: Category: "
        f"{form['CATEGORY']}"
    )

    print(
        f"Assistant: Authority: "
        f"{form['AUTHORITY']}"
    )

    print(
        f"Assistant: Detection confidence: "
        f"{confidence}"
    )


# =========================================================
# MAIN DEMO
# =========================================================

def main():

    print()
    print("======================================")
    print(" UNIVERSAL FORM ASSISTANT - DEMO")
    print("======================================")
    print()

    print(
        "Supported forms are loaded dynamically "
        "from the Exasol knowledge base."
    )

    print()

    # -----------------------------------------------------
    # DATABASE
    # -----------------------------------------------------

    db = ExasolClient()

    try:

        # -------------------------------------------------
        # SIMULATED USER PROFILE
        # -------------------------------------------------

        # This is only a demo profile.
        #
        # Later this will come from the actual
        # persistent user profile service.

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
                "highest_qualification": "B.Tech",
            },
            additional_details={
                "father_name": "Rajesh Mishra",
            },
        )

        # -------------------------------------------------
        # STEP 1 - USER REQUEST
        # -------------------------------------------------

        user_message = input(
            "You: "
        ).strip()

        if not user_message:

            print(
                "Assistant: Please tell me "
                "which form you want to fill."
            )

            return

        # -------------------------------------------------
        # STEP 2 - FORM DETECTION
        # -------------------------------------------------

        print()
        print(
            "Assistant: Identifying the form..."
        )

        form_match = detect_form_intent(
            db,
            user_message,
        )

        if not form_match:

            print()

            print(
                "Assistant: I couldn't confidently "
                "identify the form."
            )

            print(
                "Assistant: Please mention the "
                "form name."
            )

            return

        form = form_match["form"]
        confidence = form_match["confidence"]

        form_id = form["FORM_ID"]
        form_code = form["FORM_CODE"]

        display_form_information(
            form,
            confidence,
        )

        # -------------------------------------------------
        # STEP 3 - RESEARCHER
        # -------------------------------------------------

        print()

        print(
            "Assistant: Checking the form "
            "requirements..."
        )

        researcher = ResearcherAgent(db)

        research_result = researcher.research(
            form_id=form_id,
            form_code=form_code,
        )

        if not research_result.success:

            print()

            print(
                "Assistant: I couldn't retrieve "
                "the form requirements."
            )

            return

        print(
            "Assistant: Form requirements loaded "
            "from the knowledge base."
        )

        # -------------------------------------------------
        # STEP 4 - LOAD FORM FIELDS
        # -------------------------------------------------

        fields = load_form_fields(
            db,
            form_id,
        )

        if not fields:

            print()

            print(
                "Assistant: This form was found, "
                "but no fields are configured "
                "in the knowledge base yet."
            )

            return

        print(
            f"Assistant: {len(fields)} form fields "
            "loaded."
        )

        # -------------------------------------------------
        # STEP 5 - GUIDE
        # -------------------------------------------------

        guide = GuideAgent()

        answers = {}

        guide_result = guide.process(
            fields=fields,
            profile=profile,
            answers=answers,
        )

        # -------------------------------------------------
        # Store automatic profile matches
        # -------------------------------------------------

        for action in guide_result.actions:

            if action.action == "fill":

                answers[
                    action.field_code
                ] = action.value

        # -------------------------------------------------
        # Display current progress
        # -------------------------------------------------

        print()

        print(
            f"Assistant: Profile matching complete. "
            f"Progress: {guide_result.progress}"
        )

        # -------------------------------------------------
        # INTERACTIVE GUIDE LOOP
        # -------------------------------------------------

        while guide_result.questions:

            question = guide_result.questions[0]

            # Find the actual field
            current_field = None

            for field in fields:

                if (
                    field.field_code
                    == question.field_code
                ):

                    current_field = field
                    break

            if current_field is None:

                print(
                    "Assistant: I couldn't locate "
                    "that field."
                )

                break

            # -------------------------------------------------
            # Ask user
            # -------------------------------------------------

            value = ask_for_field(
                db,
                current_field,
            )

            # -------------------------------------------------
            # Store answer
            # -------------------------------------------------

            answers[
                current_field.field_code
            ] = value

            # -------------------------------------------------
            # Run Guide again
            # -------------------------------------------------

            guide_result = guide.process(
                fields=fields,
                profile=profile,
                answers=answers,
            )

            # -------------------------------------------------
            # Store Guide actions
            # -------------------------------------------------

            for action in guide_result.actions:

                if action.action == "fill":

                    answers[
                        action.field_code
                    ] = action.value

            print()

            print(
                f"Assistant: Progress "
                f"{guide_result.progress}"
            )

        # -------------------------------------------------
        # STEP 6 - QA
        # -------------------------------------------------

        print()

        print(
            "Assistant: All required information "
            "has been collected."
        )

        print(
            "Assistant: Running final validation..."
        )

        qa = QAAgent(db)

        qa_result = qa.validate(
            form_id=form_id,
            fields=fields,
            answers=answers,
        )

        print()

        # -------------------------------------------------
        # VALIDATION PASSED
        # -------------------------------------------------

        if qa_result.valid:

            print(
                "======================================"
            )

            print(
                " VALIDATION PASSED"
            )

            print(
                "======================================"
            )

            print()

            print(
                "Risk level:",
                qa_result.risk_level,
            )

            print(
                "Ready for review:",
                qa_result.ready_for_review,
            )

            print()

            print(
                "Assistant: Your form information "
                "is complete and has passed "
                "validation."
            )

            print(
                "Assistant: Please review everything "
                "before submission."
            )

        # -------------------------------------------------
        # VALIDATION FAILED
        # -------------------------------------------------

        else:

            print(
                "======================================"
            )

            print(
                " VALIDATION FAILED"
            )

            print(
                "======================================"
            )

            print()

            for issue in (
                qa_result.blocking_issues
            ):

                print(
                    f"- {issue['field']}: "
                    f"{issue['issue']}"
                )

            print()

            print(
                "Risk level:",
                qa_result.risk_level,
            )

        # -------------------------------------------------
        # FINAL ANSWERS
        # -------------------------------------------------

        print()

        print(
            "Final answers:"
        )

        print(
            json.dumps(
                answers,
                indent=2,
                default=str,
            )
        )

    finally:

        db.close()


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()