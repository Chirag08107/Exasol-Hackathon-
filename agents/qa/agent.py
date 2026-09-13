import re
from typing import Any, Dict, List

from agents.database import ExasolClient
from agents.models import FormField, QAResult


class QAAgent:
    def __init__(self, db: ExasolClient):
        self.db = db

    def validate(
        self,
        form_id: int,
        fields: List[FormField],
        answers: Dict[str, Any],
    ) -> QAResult:

        blocking_issues = []
        warnings = []
        checklist = []

        # --------------------------------------------------
        # 1. REQUIRED FIELD VALIDATION
        # --------------------------------------------------

        for field in fields:
            value = answers.get(field.field_code)

            if field.is_required:
                if value is None or str(value).strip() == "":
                    blocking_issues.append({
                        "field": field.field_code,
                        "issue": "Required field is missing.",
                        "severity": "HIGH",
                    })

        # --------------------------------------------------
        # 2. FIELD REGEX VALIDATION
        # --------------------------------------------------

        for field in fields:
            value = answers.get(field.field_code)

            if value is None:
                continue

            pattern = field.validation_pattern

            if not pattern:
                continue

            # Normalize escaped regex patterns coming from the database.
            # Some stored patterns may contain double backslashes such as
            # "\\s" and "\\." which should be interpreted as "\s" and "\."
            pattern = pattern.replace("\\\\", "\\")

            try:
                if not re.match(
                    pattern,
                    str(value),
                ):
                    
                    blocking_issues.append({
                        "field": field.field_code,
                        "issue": (
                            "Value does not match "
                            "the required format."
                        ),
                        "severity": "HIGH",
                    })

            except re.error:
                warnings.append({
                    "field": field.field_code,
                    "issue": (
                        "Validation pattern "
                        "could not be evaluated."
                    ),
                    "severity": "LOW",
                })

        # --------------------------------------------------
        # 3. LENGTH VALIDATION
        # --------------------------------------------------

        for field in fields:
            value = answers.get(field.field_code)

            if value is None:
                continue

            value_length = len(str(value))

            if (
                field.min_length is not None
                and value_length < field.min_length
            ):
                blocking_issues.append({
                    "field": field.field_code,
                    "issue": (
                        f"Minimum length is "
                        f"{field.min_length}."
                    ),
                    "severity": "HIGH",
                })

            if (
                field.max_length is not None
                and value_length > field.max_length
            ):
                blocking_issues.append({
                    "field": field.field_code,
                    "issue": (
                        f"Maximum length is "
                        f"{field.max_length}."
                    ),
                    "severity": "HIGH",
                })

        # --------------------------------------------------
        # 4. DATABASE RULES
        # --------------------------------------------------

        rules = self.db.execute(f"""
            SELECT
                rule_id,
                field_id,
                rule_type,
                rule_expression,
                error_message,
                severity
            FROM FORM_KB.FORM_RULE
            WHERE form_id = {int(form_id)}
        """)

        for rule in rules:

            field_code = self._get_field_code(
                rule["FIELD_ID"]
            )

            if not field_code:
                continue

            value = answers.get(field_code)

            if value is None:
                continue

            rule_type = str(
                rule["RULE_TYPE"]
            ).upper()

            expression = rule["RULE_EXPRESSION"]

            # ----------------------------------------------
            # REGEX RULE
            # ----------------------------------------------

            if rule_type == "REGEX":

                try:

                    if not re.match(
                        expression,
                        str(value),
                    ):
                        blocking_issues.append({
                            "field": field_code,
                            "issue": rule["ERROR_MESSAGE"],
                            "severity": rule["SEVERITY"],
                        })

                except re.error:

                    warnings.append({
                        "field": field_code,
                        "issue": (
                            "Database regex rule "
                            "could not be evaluated."
                        ),
                        "severity": "LOW",
                    })

        # --------------------------------------------------
        # 5. CHECKLIST
        # --------------------------------------------------

        for field in fields:

            completed = bool(
                answers.get(field.field_code)
            )

            checklist.append({
                "field": field.field_code,
                "completed": completed,
            })

        # --------------------------------------------------
        # 6. FINAL STATUS
        # --------------------------------------------------

        valid = len(blocking_issues) == 0

        if blocking_issues:
            risk_level = "HIGH"
        elif warnings:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return QAResult(
            valid=valid,
            risk_level=risk_level,
            blocking_issues=blocking_issues,
            warnings=warnings,
            checklist=[
                (
                    f"{item['field']}: "
                    f"{'Complete' if item['completed'] else 'Missing'}"
                )
                for item in checklist
            ],
            ready_for_review=valid,
        )

    def _get_field_code(
        self,
        field_id: Any,
    ) -> str | None:

        rows = self.db.execute(f"""
            SELECT
                field_code
            FROM FORM_KB.FORM_FIELD
            WHERE field_id = {int(field_id)}
        """)

        if not rows:
            return None

        return rows[0]["FIELD_CODE"]