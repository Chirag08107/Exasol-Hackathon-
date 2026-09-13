from database.exasol import get_connection

from services.form_service import (
    get_form_by_id,
    get_form_fields
)

def get_profile_value(field, user):
    code = (field.get("field_code") or "").upper()
    label = (field.get("field_label") or "").lower()

    business_words = [
        "business",
        "company",
        "organization",
        "organisation",
        "entity"
    ]

    # Someone else's name (father, mother, guardian, spouse, nominee,
    # representative, witness...) must never be auto-filled from the
    # logged-in user's own profile — that would silently put the
    # applicant's own name into e.g. "Father's Name". These must
    # always be asked of the user directly.
    other_person_words = [
        "father",
        "mother",
        "guardian",
        "spouse",
        "husband",
        "wife",
        "nominee",
        "representative",
        "witness",
        "referee",
        "parent",
        "assessee"
    ]

    if "name" in code or "name" in label:
        if any(word in label for word in business_words):
            return None

        if any(word in code.lower() for word in other_person_words) or any(
            word in label for word in other_person_words
        ):
            return None

        if "middle" in label:
            return user.get("middleName") or user.get("middle_name")

        if "first" in label:
            return user.get("firstName") or user.get("first_name")

        if "last" in label or "surname" in label:
            return user.get("lastName") or user.get("last_name")

        return " ".join(
            value
            for value in [
                user.get("firstName") or user.get("first_name"),
                user.get("middleName") or user.get("middle_name"),
                user.get("lastName") or user.get("last_name")
            ]
            if value
        )

    if "EMAIL" in code or "email" in label:
        return user.get("email")

    if (
        "PHONE" in code
        or "MOBILE" in code
        or "phone" in label
        or "mobile" in label
    ):
        phone = user.get("phone")

        if not phone:
            return None

        # Stored phone numbers include the country code (e.g.
        # "+919876543210", the format /verify sends to the OTP API),
        # but most form fields for a phone number expect a bare local
        # number. Strip non-digits and use the last 10 — normal for
        # Indian mobile numbers — so auto-fill doesn't hand a form
        # field a value it will fail validation on.
        digits = "".join(ch for ch in phone if ch.isdigit())
        return digits[-10:] if len(digits) >= 10 else digits

    # Label-only check (not field_code): several forms — Aadhaar
    # Registration itself included — prefix every one of their own
    # fields with the form's topic word (e.g. "AADHAAR_DOB",
    # "AADHAAR_GENDER"). Matching on field_code here would sweep all
    # of those unrelated fields into being filled with the user's
    # Aadhaar *number*. The human-readable label doesn't have that
    # prefix-collision problem.
    if "aadhaar" in label or "aadhar" in label:
        aadhaar = user.get("aadhaarNumber") or user.get("aadhaar_number")

        if not aadhaar:
            return None

        return "".join(ch for ch in aadhaar if ch.isdigit())

    # "Office Address" must never silently default to the user's home
    # address — most applicants don't have one, and this field is only
    # asked at all when they've said they do (see CONDITIONAL_FIELDS).
    if "office" in label or "OFFICE" in code:
        return None

    if "ADDRESS" in code or "address" in label:
        return user.get("address")

    return None


# ---------------------------------------------------------------------
# Conditional fields: a field in this dict is only ever asked once its
# trigger field has been answered, and only shown at all if the
# trigger's answer matches `show_when`. If the trigger says otherwise,
# the field is auto-answered with a placeholder so it doesn't block
# the form from completing (mirrors the paper form: sections like
# "Office Address" or "Representative Assessee" are simply left blank
# when not applicable).
# ---------------------------------------------------------------------
CONDITIONAL_FIELDS = {
    "PAN_OFFICE_ADDRESS": {"trigger": "PAN_HAS_OFFICE_ADDRESS", "show_when": "yes"},
    "PAN_REPRESENTATIVE_NAME": {"trigger": "PAN_HAS_REPRESENTATIVE", "show_when": "yes"},
}

# Must satisfy every conditional field's own validation_pattern (e.g.
# PAN_REPRESENTATIVE_NAME's letters-only pattern) — plain words, no
# digits or punctuation, long enough to clear any min_length in play.
NOT_APPLICABLE_PLACEHOLDER = "Not Applicable"


def create_session(user_id: int, form_id: int):
    form = get_form_by_id(form_id)

    if form is None:
        raise ValueError("Form not found")

    fields = get_form_fields(form_id)

    if not fields:
        raise ValueError("This form has no fields")

    from services.auth_service import get_user_by_id

    user = get_user_by_id(user_id)

    if user is None:
        raise ValueError("User not found")

    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT COALESCE(MAX(session_id), 0) + 1
            FROM FORM_APP.FORM_SESSION
            """
        ).fetchall()

        session_id = int(result[0][0])

        connection.execute(
            """
            INSERT INTO FORM_APP.FORM_SESSION
            (
                session_id,
                user_id,
                form_id,
                status
            )
            VALUES
            (
                {session_id},
                {user_id},
                {form_id},
                {status}
            )
            """,
            {
                "session_id": session_id,
                "user_id": user_id,
                "form_id": form_id,
                "status": "active"
            }
        )

        result = connection.execute(
            """
            SELECT COALESCE(MAX(answer_id), 0) + 1
            FROM FORM_APP.FORM_ANSWER
            """
        ).fetchall()

        next_answer_id = int(result[0][0])

        for field in fields:
            value = get_profile_value(field, user)

            if value is None or str(value).strip() == "":
                continue

            connection.execute(
                """
                INSERT INTO FORM_APP.FORM_ANSWER
                (
                    answer_id,
                    session_id,
                    field_id,
                    answer_value
                )
                VALUES
                (
                    {answer_id},
                    {session_id},
                    {field_id},
                    {answer_value}
                )
                """,
                {
                    "answer_id": next_answer_id,
                    "session_id": session_id,
                    "field_id": field["field_id"],
                    "answer_value": str(value)
                }
            )

            next_answer_id += 1

        connection.commit()

        return {
            "session_id": session_id,
            "user_id": user_id,
            "form_id": form_id,
            "status": "active"
        }

    finally:
        connection.close()

def get_session(session_id: int, user_id: int):

    connection = get_connection()

    try:

        result = connection.execute(
            """
            SELECT
                session_id,
                user_id,
                form_id,
                status
            FROM FORM_APP.FORM_SESSION
            WHERE session_id = {session_id}
              AND user_id = {user_id}
            """,
            {
                "session_id": session_id,
                "user_id": user_id
            }
        ).fetchall()

        if not result:
            return None

        row = result[0]

        return {
            "session_id": row[0],
            "user_id": row[1],
            "form_id": row[2],
            "status": row[3]
        }

    finally:
        connection.close()


def _auto_answer_not_applicable(session_id: int, field_id: int):
    """Write NOT_APPLICABLE_PLACEHOLDER for a conditional field whose
    trigger says it doesn't apply, so it never blocks completion —
    mirrors leaving that section blank on the paper form."""

    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT COALESCE(MAX(answer_id), 0) + 1
            FROM FORM_APP.FORM_ANSWER
            """
        ).fetchall()

        answer_id = result[0][0]

        connection.execute(
            """
            INSERT INTO FORM_APP.FORM_ANSWER
            (answer_id, session_id, field_id, answer_value)
            VALUES ({answer_id}, {session_id}, {field_id}, {answer_value})
            """,
            {
                "answer_id": answer_id,
                "session_id": session_id,
                "field_id": field_id,
                "answer_value": NOT_APPLICABLE_PLACEHOLDER
            }
        )

        connection.commit()

    finally:
        connection.close()


# GET CURRENT / NEXT FIELD

def get_current_field(session_id: int, form_id: int):

    # Get all fields in the correct order
    fields = get_form_fields(form_id)

    if not fields:
        return None

    field_by_code = {f["field_code"]: f for f in fields}

    connection = get_connection()

    try:

        # Get fields already answered in this session, with their values
        # (needed to resolve conditional fields' triggers).
        result = connection.execute(
            """
            SELECT field_id, answer_value
            FROM FORM_APP.FORM_ANSWER
            WHERE session_id = {session_id}
            """,
            {
                "session_id": session_id
            }
        ).fetchall()

    finally:
        connection.close()

    answered_field_ids = {row[0] for row in result}
    answer_by_field_id = {row[0]: row[1] for row in result}
    answer_by_code = {
        f["field_code"]: answer_by_field_id[f["field_id"]]
        for f in fields
        if f["field_id"] in answer_by_field_id
    }

    # Find the first unanswered field, honoring CONDITIONAL_FIELDS.
    for field in fields:

        field_id = field.get("field_id")

        if field_id in answered_field_ids:
            continue

        condition = CONDITIONAL_FIELDS.get(field["field_code"])

        if condition:
            trigger_value = answer_by_code.get(condition["trigger"])

            if trigger_value is None:
                # Trigger not yet answered — field_order always places
                # the trigger earlier, so this shouldn't happen in
                # practice; skip rather than ask out of order.
                continue

            if trigger_value.strip().lower() != condition["show_when"]:
                # Trigger says this section doesn't apply — auto-fill
                # and move on instead of asking a question the user
                # already said "no" to.
                _auto_answer_not_applicable(session_id, field_id)
                answered_field_ids.add(field_id)
                continue

        return field

    # Every field has been answered
    return None


# GET SESSION DETAILS

def get_session_details(
    session_id: int,
    user_id: int
):

    # Get session
    session = get_session(
        session_id,
        user_id
    )

    if session is None:
        return None

    # Get all fields belonging to the form
    fields = get_form_fields(
        session["form_id"]
    )

    total_fields = len(fields)

    # Get number of answered fields
    connection = get_connection()

    try:

        result = connection.execute(
            """
            SELECT COUNT(DISTINCT field_id)
            FROM FORM_APP.FORM_ANSWER
            WHERE session_id = {session_id}
            """,
            {
                "session_id": session_id
            }
        ).fetchall()

        answered_count = result[0][0]

    finally:
        connection.close()

    # Find next unanswered field
    current_field = get_current_field(
        session_id,
        session["form_id"]
    )

    # -----------------------------------------------------
    # IMPORTANT:
    # Only mark completed if ALL fields are answered.
    # -----------------------------------------------------

    if answered_count >= total_fields:

        status = "completed"

        connection = get_connection()

        try:

            connection.execute(
                """
                UPDATE FORM_APP.FORM_SESSION
                SET
                    status = 'completed',
                    updated_at = CURRENT_TIMESTAMP
                WHERE session_id = {session_id}
                """,
                {
                    "session_id": session_id
                }
            )

            connection.commit()

        finally:
            connection.close()

    else:

        status = "active"

    return {
        "session_id": session["session_id"],
        "form_id": session["form_id"],
        "status": status,
        "current_field": current_field,
        "progress": {
            "current": answered_count + 1
            if current_field
            else answered_count,
            "completed": answered_count,
            "total": total_fields
        }
    }


# SUBMIT ANSWER
import re

def validate_field_value(field, value):
    value = value.strip()

    if field["is_required"] and not value:
        raise ValueError(
            f"{field['field_label']} is required"
        )

    if not value:
        return

    min_length = field.get("min_length")
    max_length = field.get("max_length")

    if min_length is not None and len(value) < min_length:
        raise ValueError(
            f"{field['field_label']} must contain at least "
            f"{min_length} characters"
        )

    if max_length is not None and len(value) > max_length:
        raise ValueError(
            f"{field['field_label']} must contain at most "
            f"{max_length} characters"
        )

    field_type = (field.get("field_type") or "").lower()

    if field_type == "number":
        if not value.isdigit():
            raise ValueError(
                f"{field['field_label']} must contain only numbers"
            )

    validation_pattern = field.get("validation_pattern")

    if validation_pattern and validation_pattern != "NULL":
        # Some patterns stored in Exasol come back double-escaped
        # (e.g. "\\\\s" instead of "\\s") — normalize the same way
        # agents/qa/agent.py already does, otherwise valid values like
        # a normal email address get rejected.
        validation_pattern = validation_pattern.replace("\\\\", "\\")

        try:
            if not re.fullmatch(validation_pattern, value):
                raise ValueError(
                    f"Invalid value for {field['field_label']}"
                )
        except re.error:
            pass

    if field_type == "dropdown":
        options = field.get("options", [])

        valid_values = set()

        for option in options:
            if option.get("option_code"):
                valid_values.add(
                    option["option_code"].strip().lower()
                )

            if option.get("option_label"):
                valid_values.add(
                    option["option_label"].strip().lower()
                )

        if value.lower() not in valid_values:
            raise ValueError(
                f"Invalid option for {field['field_label']}"
            )

def submit_answer(
    session_id: int,
    user_id: int,
    field_id: int,
    value: str
):

    
    # Check session
    

    session = get_session(
        session_id,
        user_id
    )

    if session is None:
        raise ValueError("Session not found")

    if session["status"] == "completed":
        raise ValueError("Session is already completed")

    
    # Get fields belonging to this form
    

    fields = get_form_fields(
        session["form_id"]
    )

    # Find requested field
    field = next(
        (
            field
            for field in fields
            if field["field_id"] == field_id
        ),
        None
    )

    if field is None:
        raise ValueError(
            "Field does not belong to this form"
        )

    
    # Clean value
    

    value = value.strip()
    validate_field_value(field,value)
    
    # Required validation
    

    if field["is_required"] and not value:

        raise ValueError(
            f"{field['field_label']} is required"
        )

    
    # Minimum length validation
    

    if (
        field.get("min_length") is not None
        and len(value) < field["min_length"]
    ):

        raise ValueError(
            f"{field['field_label']} must contain at least "
            f"{field['min_length']} characters"
        )

    
    # Maximum length validation
    

    if (
        field.get("max_length") is not None
        and len(value) > field["max_length"]
    ):

        raise ValueError(
            f"{field['field_label']} must contain at most "
            f"{field['max_length']} characters"
        )

    connection = get_connection()

    try:

        # -------------------------------------------------
        # Check whether answer already exists
        # -------------------------------------------------

        result = connection.execute(
            """
            SELECT answer_id
            FROM FORM_APP.FORM_ANSWER
            WHERE session_id = {session_id}
              AND field_id = {field_id}
            """,
            {
                "session_id": session_id,
                "field_id": field_id
            }
        ).fetchall()

        # -------------------------------------------------
        # UPDATE existing answer
        # -------------------------------------------------

        if result:

            answer_id = result[0][0]

            connection.execute(
                """
                UPDATE FORM_APP.FORM_ANSWER
                SET
                    answer_value = {answer_value},
                    answered_at = CURRENT_TIMESTAMP
                WHERE answer_id = {answer_id}
                """,
                {
                    "answer_value": value,
                    "answer_id": answer_id
                }
            )

        # -------------------------------------------------
        # INSERT new answer
        # -------------------------------------------------

        else:

            result = connection.execute(
                """
                SELECT COALESCE(MAX(answer_id), 0) + 1
                FROM FORM_APP.FORM_ANSWER
                """
            ).fetchall()

            answer_id = result[0][0]

            connection.execute(
                """
                INSERT INTO FORM_APP.FORM_ANSWER
                (
                    answer_id,
                    session_id,
                    field_id,
                    answer_value
                )
                VALUES
                (
                    {answer_id},
                    {session_id},
                    {field_id},
                    {answer_value}
                )
                """,
                {
                    "answer_id": answer_id,
                    "session_id": session_id,
                    "field_id": field_id,
                    "answer_value": value
                }
            )

        # -------------------------------------------------
        # Update session timestamp
        # -------------------------------------------------

        connection.execute(
            """
            UPDATE FORM_APP.FORM_SESSION
            SET
                updated_at = CURRENT_TIMESTAMP
            WHERE session_id = {session_id}
            """,
            {
                "session_id": session_id
            }
        )

        connection.commit()

    finally:
        connection.close()

    
    # Return updated session
    

    return get_session_details(
        session_id,
        user_id
    )