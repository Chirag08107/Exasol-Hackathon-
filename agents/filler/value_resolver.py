"""
Generic field mapper.

Turns a canonical answers dict (e.g. {"PAN_NAME": "Aditya Mishra",
"PAN_DOB": "01/01/2002", ...} — exactly what the existing Guide/QA
agents produce) plus a TemplateMapping into a flat list of concrete
placements a renderer can draw, without knowing anything about PAN,
passports, or any other specific form.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from .pdf_filler import CharPlacement, CheckboxPlacement, TextPlacement, Placement
from .schema import CheckboxOption, Extract, FieldMapping, TemplateMapping


def _split_name(full_name: str) -> Dict[str, str]:
    parts = [p for p in re.split(r"\s+", full_name.strip()) if p]

    if not parts:
        return {"first": "", "middle": "", "last": ""}
    if len(parts) == 1:
        return {"first": parts[0], "middle": "", "last": ""}
    if len(parts) == 2:
        return {"first": parts[0], "middle": "", "last": parts[1]}

    return {
        "first": parts[0],
        "middle": " ".join(parts[1:-1]),
        "last": parts[-1],
    }


def _split_phone(digits: str, default_country_code: str) -> Dict[str, str]:
    """
    Split a digits-only phone string into (country_code, local_number).

    Local Indian mobile numbers are 10 digits. If more than 10 digits
    were supplied, the leading digits are treated as an explicit
    country code (e.g. "919876543210" -> "91" + "9876543210"). If
    exactly 10 (or fewer) digits were supplied, there is no country
    code in the data at all — this documents the assumption that we
    default it to `default_country_code` ("91"/India) rather than
    guessing, since this canonical field only ever carries a bare
    mobile number today (see agents/guide/agent.py's profile mapping).
    """

    if len(digits) > 10:
        return {"country_code": digits[:-10], "local_number": digits[-10:]}

    return {"country_code": default_country_code, "local_number": digits}


def _apply_extract(extract: Extract, raw_value: Any) -> str:
    value = "" if raw_value is None else str(raw_value)

    if extract.kind == "raw":
        return value

    if extract.kind == "static":
        return extract.value or ""

    if extract.kind == "digits":
        return re.sub(r"\D", "", value)

    if extract.kind == "name_part":
        parts = _split_name(value)
        return parts.get(extract.part or "first", "")

    if extract.kind in ("phone_country_code", "phone_local_number"):
        digits = re.sub(r"\D", "", value)
        split = _split_phone(digits, extract.default_country_code)
        key = "country_code" if extract.kind == "phone_country_code" else "local_number"
        return split[key]

    if extract.kind == "csv_part":
        parts = [p.strip() for p in value.split(",")]
        index = extract.part_index or 0
        return parts[index] if 0 <= index < len(parts) else ""

    return value


def _match_checkbox_option(
    value: str, options: List[CheckboxOption]
) -> Optional[CheckboxOption]:
    normalized = value.strip().lower()

    if not normalized:
        return None

    for option in options:
        for candidate in option.matches:
            if candidate.lower() == normalized:
                return option

    # Fall back to a substring match so slightly different wording
    # ("Non-Resident" vs "Non Resident") still resolves.
    for option in options:
        for candidate in option.matches:
            if candidate.lower() in normalized or normalized in candidate.lower():
                return option

    return None


def _cover_tuple(option: CheckboxOption):
    if not option.cover:
        return None
    return (option.cover.x0, option.cover.y0, option.cover.x1, option.cover.y1)


def _checkbox_placement(field, option: CheckboxOption) -> CheckboxPlacement:
    return CheckboxPlacement(
        page=field.page,
        x_left=option.x,
        x_right=option.x_right or (option.x + 10),
        y_top=option.y_top,
        y_bottom=option.y_bottom,
        cover=_cover_tuple(option),
    )


def _place_char_row(
    page: int, text: str, row, font_size: float
) -> List[CharPlacement]:
    placements: List[CharPlacement] = []

    for i, ch in enumerate(text[: row.max_chars]):
        if ch == " ":
            continue

        x_left = row.x_start + i * row.box_width
        placements.append(
            CharPlacement(
                page=page,
                x_left=x_left,
                x_right=x_left + row.box_width,
                y_top=row.y_top,
                y_bottom=row.y_bottom,
                char=ch,
                font_size=font_size,
            )
        )

    return placements


def resolve_placements(
    mapping: TemplateMapping, answers: Dict[str, Any]
) -> List[Placement]:
    """
    Resolve every field in the mapping against the answers dict.
    A field whose canonical_field has no answer (or an empty one) is
    silently skipped — it stays blank on the generated PDF, exactly
    like the applicant leaving that box empty.
    """

    placements: List[Placement] = []

    for field in mapping.fields:
        raw_value = answers.get(field.canonical_field)

        if raw_value in (None, ""):
            continue

        # Conditional fields the applicant said don't apply (e.g. "no
        # office address") are auto-answered with this sentinel by
        # the session flow rather than left unanswered, so the form
        # can still complete — it must never be printed onto the PDF.
        if isinstance(raw_value, str) and raw_value.strip().lower() == "not applicable":
            continue

        value = _apply_extract(field.extract, raw_value)

        if not value:
            continue

        font_size = field.font_size or mapping.default_font_size

        if field.type == "text":
            placements.append(
                TextPlacement(
                    page=field.page,
                    x=field.x,
                    y_baseline=field.y_baseline,
                    text=value,
                    font_size=font_size,
                )
            )

        elif field.type == "char_boxes":
            placements.extend(
                _place_char_row(field.page, value, field.row, font_size)
            )

        elif field.type == "grouped_char_boxes":
            cursor = 0
            for group in field.groups:
                chunk = value[cursor : cursor + group.count]
                cursor += group.count

                for i, ch in enumerate(chunk):
                    if ch == " ":
                        continue

                    x_left = group.x_start + i * group.box_width
                    placements.append(
                        CharPlacement(
                            page=field.page,
                            x_left=x_left,
                            x_right=x_left + group.box_width,
                            y_top=field.group_y_top,
                            y_bottom=field.group_y_bottom,
                            char=ch,
                            font_size=font_size,
                        )
                    )

        elif field.type == "multiline_char_boxes":
            remaining = value
            for row in field.rows:
                if not remaining:
                    break

                chunk, remaining = (
                    remaining[: row.max_chars],
                    remaining[row.max_chars :],
                )
                placements.extend(
                    _place_char_row(field.page, chunk, row, font_size)
                )

        elif field.type == "checkbox":
            option = _match_checkbox_option(value, field.options or [])

            if option is None:
                continue

            placements.append(_checkbox_placement(field, option))

        elif field.type == "multi_checkbox":
            # Unlike "checkbox" (exactly one option, exact/substring
            # match against the whole answer), this ticks every option
            # whose match phrase appears anywhere in the answer — for
            # a field the user can answer with more than one selection
            # at once, e.g. "identity, address" or "identity and dob".
            normalized = value.strip().lower()

            for option in field.options or []:
                if any(candidate.lower() in normalized for candidate in option.matches):
                    placements.append(_checkbox_placement(field, option))

    return placements
