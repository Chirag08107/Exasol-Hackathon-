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

    if "name" in code or "name" in label:
        if any(word in label for word in business_words):
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
        return user.get("phone")

    if (
        "AADHAAR" in code
        or "AADHAR" in code
        or "aadhaar" in label
        or "aadhar" in label
    ):
        return user.get("aadhaarNumber") or user.get("aadhaar_number")

    if "ADDRESS" in code or "address" in label:
        return user.get("address")

    return None


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


# GET CURRENT / NEXT FIELD

def get_current_field(session_id: int, form_id: int):

    # Get all fields in the correct order
    fields = get_form_fields(form_id)

    if not fields:
        return None

    connection = get_connection()

    try:

        # Get fields already answered in this session
        result = connection.execute(
            """
            SELECT DISTINCT field_id
            FROM FORM_APP.FORM_ANSWER
            WHERE session_id = {session_id}
            """,
            {
                "session_id": session_id
            }
        ).fetchall()

        answered_field_ids = {
            row[0]
            for row in result
        }

    finally:
        connection.close()

    # Find the first unanswered field
    for field in fields:

        field_id = field.get("field_id")

        if field_id not in answered_field_ids:
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