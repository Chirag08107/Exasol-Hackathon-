"""
High-level entry point used by callers (the backend, the agents demo
scripts, tests) to turn validated canonical answers into a filled PDF.

This module intentionally contains no PAN-specific (or any other
form-specific) logic — which template and mapping to use is passed in
by the caller, based on the form the Detective agent identified.
"""

from __future__ import annotations

import os
from typing import Any, Dict

from .pdf_filler import PdfFillQAError, fill_pdf
from .schema import TemplateMapping
from .value_resolver import resolve_placements

# agents/filler/service.py -> agents/filler -> agents -> repo root
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PdfFillError(Exception):
    """Raised when the answers cannot be turned into a filled PDF."""


def fill_form(mapping_path: str, answers: Dict[str, Any]) -> bytes:
    """
    Load the mapping at `mapping_path`, resolve `answers` (a canonical
    field_code -> value dict, exactly what the Guide/QA agents already
    produce) against it, and return the filled PDF as bytes.

    Raises PdfFillError if the answers are unusable (e.g. completely
    empty) or if the underlying template/mapping is broken.
    """

    if not answers or not any(v not in (None, "") for v in answers.values()):
        raise PdfFillError("No answers were provided to fill the form.")

    try:
        mapping = TemplateMapping.load(mapping_path)
    except Exception as exc:  # noqa: BLE001 - surface as a clear error
        raise PdfFillError(f"Could not load mapping '{mapping_path}': {exc}") from exc

    # `template` in the mapping file is a path relative to the repo
    # root (e.g. "agents/demo/sample_form.pdf"), so this resolves the
    # same way regardless of the caller's current working directory
    # (the backend runs from backend/, the agents demos run from the
    # repo root).
    template_path = (
        mapping.template
        if os.path.isabs(mapping.template)
        else os.path.join(_REPO_ROOT, mapping.template)
    )

    if not os.path.exists(template_path):
        raise PdfFillError(f"Template PDF not found: {template_path}")

    placements = resolve_placements(mapping, answers)

    if not placements:
        raise PdfFillError(
            "None of the provided answers matched a field in this "
            "template's mapping — nothing would be filled in."
        )

    try:
        return fill_pdf(
            template_path=template_path,
            page_count=mapping.page_count,
            page_width=mapping.page_width,
            page_height=mapping.page_height,
            placements=placements,
            font=mapping.font,
        )
    except PdfFillQAError as exc:
        raise PdfFillError(str(exc)) from exc
