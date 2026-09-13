from typing import Any, Dict
from agents.models import (
    FormField,
    GuideAction,
    GuideQuestion,
    GuideResult,
    UserProfile,
)


class GuideAgent:

    def process(
        self,
        fields: list[FormField],
        profile: UserProfile,
        answers: Dict[str, Any],
    ) -> GuideResult:

        questions = []
        actions = []
        feedback = []

        completed = 0

        for field in fields:

            field_code = field.field_code

            # -------------------------------------------------
            # 1. Check if an answer was already provided
            # -------------------------------------------------
            value = answers.get(field_code)

            if value not in (None, ""):

                actions.append(
                    GuideAction(
                        field_code=field_code,
                        action="fill",
                        value=value,
                        source="user",
                    )
                )

                completed += 1
                continue

            # -------------------------------------------------
            # 2. Try to find the value in the user profile
            # -------------------------------------------------
            value = self._find_profile_value(field_code, profile)

            if value not in (None, ""):

                actions.append(
                    GuideAction(
                        field_code=field_code,
                        action="fill",
                        value=value,
                        source="profile",
                    )
                )

                completed += 1
                continue

            # -------------------------------------------------
            # 3. Ask the user only if the field is required
            # -------------------------------------------------
            if field.is_required:

                questions.append(
                    GuideQuestion(
                        field_code=field_code,
                        question=self._generate_question(field),
                        reason="Required information is missing.",
                    )
                )

        total = len(fields)

        next_field = (
            questions[0].field_code
            if questions
            else None
        )

        return GuideResult(
            success=True,
            questions=questions,
            actions=actions,
            feedback=feedback,
            next_field=next_field,
            progress=f"{completed}/{total} fields",
        )

    # =========================================================
    # PROFILE → FORM FIELD MAPPING
    # =========================================================

    def _find_profile_value(
        self,
        field_code: str,
        profile: UserProfile,
    ) -> Any:

        # Combine all profile sections
        profile_data = {}

        profile_data.update(profile.personal_information)
        profile_data.update(profile.education)
        profile_data.update(profile.additional_details)

        # -------------------------------------------------
        # Canonical mapping between form fields and profile
        # -------------------------------------------------

        field_mapping = {

            "PAN_NAME": [
                "full_name",
                "name",
                "applicant_name",
            ],

            "PAN_DOB": [
                "date_of_birth",
                "dob",
                "birth_date",
            ],

            "PAN_FATHER": [
                "father_name",
                "father",
                "parent_name",
            ],

            "PAN_GENDER": [
                "gender",
            ],

            "PAN_RESIDENTIAL_STATUS": [
                "residential_status",
                "residence_status",
            ],

            "PAN_ADDRESS": [
                "address",
                "full_address",
                "residence_address",
            ],

            "PAN_EMAIL": [
                "email",
                "email_address",
            ],

            "PAN_PHONE": [
                "phone",
                "mobile",
                "mobile_number",
            ],
        }

        possible_keys = field_mapping.get(
            field_code.upper(),
            [field_code.lower()],
        )

        # -------------------------------------------------
        # Search profile
        # -------------------------------------------------

        for key in possible_keys:

            if key in profile_data:

                value = profile_data[key]

                if value not in (None, ""):

                    # Special formatting for PAN DOB
                    if field_code.upper() == "PAN_DOB":

                        value = self._format_date(value)

                    return value

        return None

    # =========================================================
    # DATE NORMALIZATION
    # =========================================================

    def _format_date(self, value: Any) -> Any:

        if not isinstance(value, str):
            return value

        # Profile may contain YYYY-MM-DD
        # PAN expects DD/MM/YYYY

        parts = value.split("-")

        if len(parts) == 3:

            year, month, day = parts

            if (
                len(year) == 4
                and len(month) == 2
                and len(day) == 2
            ):
                return f"{day}/{month}/{year}"

        return value

    # =========================================================
    # QUESTION GENERATION
    # =========================================================

    def _generate_question(
        self,
        field: FormField,
    ) -> str:

        label = field.field_label

        if field.explanation:

            return (
                f"What should I enter for '{label}'? "
                f"{field.explanation}"
            )

        return f"What should I enter for '{label}'?"