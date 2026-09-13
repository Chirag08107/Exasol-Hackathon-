from database.exasol import get_connection


def get_all_forms():
    connection = get_connection()

    try:
        statement = connection.execute("""
            SELECT
                form_id,
                form_code,
                form_name,
                category,
                sub_category,
                authority,
                country,
                description,
                form_url,
                instructions_url,
                version,
                status,
                last_verified_date
            FROM FORM_KB.FORM
            ORDER BY form_id
        """)

        rows = statement.fetchall()

        forms = []

        for row in rows:
            forms.append({
                "form_id": row[0],
                "form_code": row[1],
                "form_name": row[2],
                "category": row[3],
                "sub_category": row[4],
                "authority": row[5],
                "country": row[6],
                "description": row[7],
                "form_url": row[8],
                "instructions_url": row[9],
                "version": row[10],
                "status": row[11],
                "last_verified_date": row[12]
            })

        return forms

    finally:
        connection.close()


def get_form_by_id(form_id: int):
    connection = get_connection()

    try:
        statement = connection.execute("""
            SELECT
                form_id,
                form_code,
                form_name,
                category,
                sub_category,
                authority,
                country,
                description,
                form_url,
                instructions_url,
                version,
                status,
                last_verified_date
            FROM FORM_KB.FORM
            WHERE form_id = {form_id}
        """.format(form_id=form_id))

        row = statement.fetchone()

        if row is None:
            return None

        return {
            "form_id": row[0],
            "form_code": row[1],
            "form_name": row[2],
            "category": row[3],
            "sub_category": row[4],
            "authority": row[5],
            "country": row[6],
            "description": row[7],
            "form_url": row[8],
            "instructions_url": row[9],
            "version": row[10],
            "status": row[11],
            "last_verified_date": row[12]
        }

    finally:
        connection.close()


def get_form_fields(form_id: int):
    connection = get_connection()

    try:
        statement = connection.execute("""
            SELECT
                f.field_id,
                f.form_id,
                f.field_code,
                f.field_label,
                f.field_type,
                f.section_name,
                f.is_required,
                f.field_order,
                f.explanation,
                f.example_value,
                f.validation_pattern,
                f.min_length,
                f.max_length,
                o.option_id,
                o.option_code,
                o.option_label
            FROM FORM_KB.FORM_FIELD f
            LEFT JOIN FORM_KB.FIELD_OPTION o
                ON f.field_id = o.field_id
            WHERE f.form_id = {form_id}
            ORDER BY
                f.field_order,
                o.option_id
        """.format(form_id=form_id))

        rows = statement.fetchall()

        fields = {}

        for row in rows:

            field_id = row[0]

            if field_id not in fields:
                fields[field_id] = {
                    "field_id": row[0],
                    "form_id": row[1],
                    "field_code": row[2],
                    "field_label": row[3],
                    "field_type": row[4],
                    "section_name": row[5],
                    "is_required": bool(row[6]),
                    "field_order": row[7],
                    "explanation": row[8],
                    "example_value": row[9],
                    "validation_pattern": row[10],
                    "min_length": row[11],
                    "max_length": row[12],
                    "options": []
                }

            if row[13] is not None:
                fields[field_id]["options"].append({
                    "option_id": row[13],
                    "option_code": row[14],
                    "option_label": row[15]
                })

        return list(fields.values())

    finally:
        connection.close()

def get_form_requirements(form_id: int):
    connection = get_connection()

    try:
        statement = connection.execute("""
            SELECT
                requirement_id,
                form_id,
                requirement_type,
                requirement_text,
                severity,
                condition
            FROM FORM_KB.FORM_REQUIREMENT
            WHERE form_id = {form_id}
            ORDER BY requirement_id
        """.format(form_id=form_id))

        rows = statement.fetchall()

        requirements = []

        for row in rows:
            requirements.append({
                "requirement_id": row[0],
                "form_id": row[1],
                "requirement_type": row[2],
                "requirement_text": row[3],
                "severity": row[4],
                "condition": row[5]
            })

        return requirements

    finally:
        connection.close()


def get_form_documents(form_id: int):
    connection = get_connection()

    try:
        statement = connection.execute("""
            SELECT
                form_document_id,
                form_id,
                document_name,
                document_type,
                mandatory,
                condition,
                description
            FROM FORM_KB.FORM_DOCUMENT
            WHERE form_id = {form_id}
            ORDER BY form_document_id
        """.format(form_id=form_id))

        rows = statement.fetchall()

        documents = []

        for row in rows:
            documents.append({
                "form_document_id": row[0],
                "form_id": row[1],
                "document_name": row[2],
                "document_type": row[3],
                "mandatory": bool(row[4]),
                "condition": row[5],
                "description": row[6]
            })

        return documents

    finally:
        connection.close()


def get_form_rules(form_id: int):
    connection = get_connection()

    try:
        statement = connection.execute("""
            SELECT
                rule_id,
                form_id,
                field_id,
                rule_type,
                rule_expression,
                error_message,
                severity
            FROM FORM_KB.FORM_RULE
            WHERE form_id = {form_id}
            ORDER BY rule_id
        """.format(form_id=form_id))

        rows = statement.fetchall()

        rules = []

        for row in rows:
            rules.append({
                "rule_id": row[0],
                "form_id": row[1],
                "field_id": row[2],
                "rule_type": row[3],
                "rule_expression": row[4],
                "error_message": row[5],
                "severity": row[6]
            })

        return rules

    finally:
        connection.close()

def get_form_mistakes(form_id: int):
    connection = get_connection()

    try:
        statement = connection.execute("""
            SELECT
                mistake_id,
                form_id,
                field_id,
                mistake,
                explanation,
                severity,
                prevention_tip
            FROM FORM_KB.COMMON_MISTAKE
            WHERE form_id = {form_id}
            ORDER BY mistake_id
        """.format(form_id=form_id))

        rows = statement.fetchall()

        mistakes = []

        for row in rows:
            mistakes.append({
                "mistake_id": row[0],
                "form_id": row[1],
                "field_id": row[2],
                "mistake": row[3],
                "explanation": row[4],
                "severity": row[5],
                "prevention_tip": row[6]
            })

        return mistakes

    finally:
        connection.close()

def get_form_sources(form_id: int):
    connection = get_connection()

    try:
        statement = connection.execute("""
            SELECT
                source_id,
                form_id,
                source_type,
                source_name,
                source_url,
                retrieved_date,
                verified_date,
                source_version
            FROM FORM_KB.FORM_SOURCE
            WHERE form_id = {form_id}
            ORDER BY source_id
        """.format(form_id=form_id))

        rows = statement.fetchall()

        sources = []

        for row in rows:
            sources.append({
                "source_id": row[0],
                "form_id": row[1],
                "source_type": row[2],
                "source_name": row[3],
                "source_url": row[4],
                "retrieved_date": row[5],
                "verified_date": row[6],
                "source_version": row[7]
            })

        return sources

    finally:
        connection.close()

def search_forms(query: str):

    query = query.strip()

    if not query:
        return []

    # Match each word of the query independently (all must be present
    # somewhere across the searchable columns) instead of requiring the
    # whole phrase to appear verbatim — otherwise a query like
    # "PAN form" never matches "PAN Card Application - Form 93", since
    # "pan" and "form" aren't adjacent in that text.
    words = query.split()

    per_word_clause = """(
        LOWER(form_name) LIKE LOWER({q})
        OR LOWER(form_code) LIKE LOWER({q})
        OR LOWER(category) LIKE LOWER({q})
        OR LOWER(sub_category) LIKE LOWER({q})
        OR LOWER(description) LIKE LOWER({q})
        OR LOWER(authority) LIKE LOWER({q})
    )"""

    where_clause = " AND ".join(
        per_word_clause.replace("{q}", f"{{q{i}}}")
        for i in range(len(words))
    )

    params = {f"q{i}": f"%{word}%" for i, word in enumerate(words)}

    connection = get_connection()

    try:

        result = connection.execute(
            f"""
            SELECT
                form_id,
                form_code,
                form_name,
                category,
                sub_category,
                authority,
                country,
                description,
                form_url,
                instructions_url,
                version,
                status,
                last_verified_date
            FROM FORM_KB.FORM
            WHERE {where_clause}
            ORDER BY form_name
            """,
            params
        ).fetchall()

        forms = []

        for row in result:

            forms.append({
                "form_id": row[0],
                "form_code": row[1],
                "form_name": row[2],
                "category": row[3],
                "sub_category": row[4],
                "authority": row[5],
                "country": row[6],
                "description": row[7],
                "form_url": row[8],
                "instructions_url": row[9],
                "version": row[10],
                "status": row[11],
                "last_verified_date": row[12]
            })

        return forms

    finally:
        connection.close()