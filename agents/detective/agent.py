import re
from typing import List

from agents.database import ExasolClient
from agents.models import DetectiveResult, FormField, FormInfo
from agents.utils import extract_pdf_text


class DetectiveAgent:
    def __init__(self, db: ExasolClient):
        self.db = db

    def detect_from_pdf(self, pdf_data: bytes) -> DetectiveResult:
        """
        Extract text from a PDF, identify the form using the
        Exasol knowledge base, and retrieve its fields.
        """

        text = extract_pdf_text(pdf_data)

        if not text:
            return DetectiveResult(
                success=False,
                extracted_text="",
                warnings=[
                    "No text could be extracted from the PDF."
                ],
            )

        form = self._detect_form(text)

        if not form:
            return DetectiveResult(
                success=False,
                extracted_text=text,
                warnings=[
                    "Unable to identify a supported form."
                ],
            )

        fields = self._get_fields(form["FORM_ID"])

        form_info = FormInfo(
            form_id=form["FORM_ID"],
            form_code=form["FORM_CODE"],
            form_name=form["FORM_NAME"],
            category=form.get("CATEGORY"),
            authority=form.get("AUTHORITY"),
            country=form.get("COUNTRY"),
            description=form.get("DESCRIPTION"),
        )

        return DetectiveResult(
            success=True,
            form=form_info,
            confidence=form["confidence"],
            source="pdf",
            extracted_text=text,
            fields=fields,
        )

    def _detect_form(self, text: str):
        """
        Compare extracted PDF text against all forms in Exasol
        and select the best matching form.
        """

        normalized = text.lower()

        forms = self.db.execute("""
            SELECT
                form_id,
                form_code,
                form_name,
                category,
                authority,
                country,
                description
            FROM FORM_KB.FORM
        """)

        best_match = None
        best_score = 0

        for form in forms:
            code = str(form["FORM_CODE"]).lower()
            name = str(form["FORM_NAME"]).lower()

            score = 0

            # Strong match if the form code appears in the PDF.
            if code and code in normalized:
                score += 5

            # Match meaningful words from the form name.
            words = re.findall(
                r"[a-zA-Z0-9]+",
                name,
            )

            for word in words:
                if len(word) >= 3 and word in normalized:
                    score += 1

            if score > best_score:
                best_score = score
                best_match = form

        if not best_match:
            return None

        confidence = min(
            0.99,
            max(0.1, best_score / 10),
        )

        best_match["confidence"] = confidence

        return best_match

    def _get_fields(
        self,
        form_id: int,
    ) -> List[FormField]:
        """
        Retrieve all fields belonging to the detected form.
        """

        rows = self.db.execute(f"""
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

        return [
            FormField(
                field_id=row["FIELD_ID"],
                field_code=row["FIELD_CODE"],
                field_label=row["FIELD_LABEL"],
                field_type=row["FIELD_TYPE"],
                section_name=row["SECTION_NAME"],
                is_required=bool(row["IS_REQUIRED"]),
                field_order=row["FIELD_ORDER"],
                explanation=row["EXPLANATION"],
                example_value=row["EXAMPLE_VALUE"],
                validation_pattern=row["VALIDATION_PATTERN"],
                min_length=row["MIN_LENGTH"],
                max_length=row["MAX_LENGTH"],
            )
            for row in rows
        ]