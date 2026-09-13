"""
Generic PDF template-mapping schema.

A mapping file (e.g. agents/mappings/pan_form_93.json) describes, for one
PDF template, where each canonical field's value should be visually placed.
Nothing here is form-specific — PAN, passport, or any other template is
described the same way, by writing a new mapping file. The filler code
that consumes this schema (pdf_filler.py) never branches on form identity.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------
# How to pull a sub-value out of the canonical answer string before
# placing it. This keeps multi-part fields (a name split into
# first/middle/last boxes, a phone split into country-code/number
# groups) generic instead of hardcoding "PAN_NAME" anywhere.
# ---------------------------------------------------------------------

class Extract(BaseModel):
    kind: Literal[
        "raw",
        "name_part",
        "digits",
        "phone_country_code",
        "phone_local_number",
        "static",
        "csv_part",
    ] = "raw"

    # kind == "name_part": which part of a whitespace-split full name.
    part: Optional[Literal["first", "middle", "last"]] = None

    # kind == "static": always place this fixed value, ignoring the
    # canonical answer entirely (e.g. "India" for a country field on a
    # citizen-of-India form). The field is still keyed off a real
    # canonical_field so it only renders once that field has an answer
    # (i.e. once the form is actually being filled).
    value: Optional[str] = None

    # kind == "phone_country_code": used when the answer has no explicit
    # country code (i.e. is exactly a local-length number) — see
    # value_resolver._split_phone for the assumption this documents.
    default_country_code: str = "91"

    # kind == "csv_part": splits the answer on commas and returns the
    # segment at this 0-based index (empty string if the answer has
    # fewer segments). Used for a compound free-text field — an
    # address like "Plot 12, MG Road, Sahid Nagar" — where the
    # template has one box row per component instead of one long
    # overflowing row.
    part_index: Optional[int] = None


# ---------------------------------------------------------------------
# Visual placement shapes.
# ---------------------------------------------------------------------

class CharBoxRow(BaseModel):
    """A single row of uniform, evenly spaced character boxes."""

    y_top: float
    y_bottom: float
    x_start: float
    box_width: float
    max_chars: int


class CharBoxGroup(BaseModel):
    """One group of consecutive character boxes (e.g. the 'DD' group
    of a DOB field, or the country-code group of a phone field)."""

    count: int
    x_start: float
    box_width: float


class CoverRect(BaseModel):
    """A region of pre-printed template text/instructions to blank out
    before drawing the checkbox on top of it."""

    x0: float
    y0: float
    x1: float
    y1: float


class CheckboxOption(BaseModel):
    """Where to draw the selection mark for one checkbox option, and
    the value(s) that select it."""

    matches: List[str]
    x: float
    x_right: Optional[float] = None
    y_top: float
    y_bottom: float
    cover: Optional[CoverRect] = None


class FieldMapping(BaseModel):
    canonical_field: str
    type: Literal[
        "text",
        "char_boxes",
        "grouped_char_boxes",
        "multiline_char_boxes",
        "checkbox",
        "multi_checkbox",
    ]
    page: int
    extract: Extract = Field(default_factory=Extract)

    # type == "text"
    x: Optional[float] = None
    y_baseline: Optional[float] = None
    font_size: Optional[float] = None

    # type == "char_boxes"
    row: Optional[CharBoxRow] = None

    # type == "grouped_char_boxes" (digits consumed left-to-right
    # across the groups, in order)
    groups: Optional[List[CharBoxGroup]] = None
    group_y_top: Optional[float] = None
    group_y_bottom: Optional[float] = None

    # type == "multiline_char_boxes" (value overflows row to row)
    rows: Optional[List[CharBoxRow]] = None

    # type == "checkbox" | "multi_checkbox"
    options: Optional[List[CheckboxOption]] = None


class TemplateMapping(BaseModel):
    template: str
    form_code: str
    page_count: int
    page_width: float
    page_height: float
    coordinate_origin: Literal["top-left"] = "top-left"
    font: str = "Courier"
    default_font_size: float = 9.0
    fields: List[FieldMapping]

    @classmethod
    def load(cls, path: str) -> "TemplateMapping":
        import json

        with open(path, "r", encoding="utf-8") as fh:
            data: Dict[str, Any] = json.load(fh)

        return cls.model_validate(data)
