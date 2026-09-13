from agents.database import ExasolClient
from agents.models import ResearchResult


class ResearcherAgent:
    def __init__(self, db: ExasolClient):
        self.db = db

    def research(
        self,
        form_id: int,
        form_code: str,
    ) -> ResearchResult:
        """
        Retrieve requirements, documents, rules, common mistakes,
        and sources for a form from the Exasol knowledge base.
        """

        form_id = int(form_id)

        # --------------------------------------------------
        # FORM REQUIREMENTS
        # --------------------------------------------------

        requirements = self.db.execute(f"""
            SELECT
                requirement_id,
                requirement_type,
                requirement_text,
                severity,
                condition_text
            FROM FORM_KB.FORM_REQUIREMENT
            WHERE form_id = {form_id}
        """)

        # --------------------------------------------------
        # REQUIRED DOCUMENTS
        # --------------------------------------------------

        documents = self.db.execute(f"""
            SELECT
                form_document_id,
                document_name,
                document_type,
                mandatory,
                condition_text,
                description
            FROM FORM_KB.FORM_DOCUMENT
            WHERE form_id = {form_id}
        """)

        # --------------------------------------------------
        # FORM RULES
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
            WHERE form_id = {form_id}
        """)

        # --------------------------------------------------
        # COMMON MISTAKES
        # --------------------------------------------------

        mistakes = self.db.execute(f"""
            SELECT
                mistake_id,
                field_id,
                mistake,
                explanation,
                severity,
                prevention_tip
            FROM FORM_KB.COMMON_MISTAKE
            WHERE form_id = {form_id}
        """)

        # --------------------------------------------------
        # SOURCES
        # --------------------------------------------------

        sources = self.db.execute(f"""
            SELECT
                source_id,
                source_type,
                source_name,
                source_url,
                retrieved_date,
                verified_date,
                source_version
            FROM FORM_KB.FORM_SOURCE
            WHERE form_id = {form_id}
        """)

        return ResearchResult(
            success=True,
            form_code=form_code,
            requirements=requirements,
            required_documents=documents,
            rules=rules,
            common_mistakes=mistakes,
            sources=sources,
        )