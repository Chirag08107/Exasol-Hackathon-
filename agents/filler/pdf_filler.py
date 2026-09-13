"""
Generic PDF filler.

Takes the original template PDF plus a flat list of placements (already
resolved to concrete page/x/y coordinates by value_resolver.py) and
produces a filled PDF that preserves the original template's layout,
background, and page count exactly — nothing here knows what a "PAN
form" is; it only knows how to draw text/characters at coordinates and
merge that on top of an existing page.

Everything happens in memory (BytesIO) — no temporary files are written
to disk, so there is nothing to clean up afterwards.
"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import List, Optional, Tuple, Union

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import white
from reportlab.pdfgen import canvas


@dataclass
class CharPlacement:
    """One character drawn inside a box. Coordinates use the template's
    top-left-origin convention (y increases downward), matching how the
    boxes were measured against the PDF."""

    page: int
    x_left: float
    x_right: float
    y_top: float
    y_bottom: float
    char: str
    font_size: float = 9.0


@dataclass
class TextPlacement:
    """A plain text string drawn at a baseline position (top-left
    origin, y increases downward)."""

    page: int
    x: float
    y_baseline: float
    text: str
    font_size: float = 9.0


@dataclass
class CheckboxPlacement:
    """A drawn, checked checkbox: a bordered square with a mark inside,
    for templates (like this one) that only print an instruction word
    ("Tick") rather than an actual box glyph. `cover`, if given, is a
    (x0, y0, x1, y1) rectangle (top-left origin) painted white first,
    to blank out that instruction word before drawing the real box on
    top of it — this is generic box-drawing, not specific to any one
    form's wording."""

    page: int
    x_left: float
    x_right: float
    y_top: float
    y_bottom: float
    cover: Optional[Tuple[float, float, float, float]] = None


Placement = Union[CharPlacement, TextPlacement, CheckboxPlacement]


class PdfFillQAError(Exception):
    """Raised when the generated PDF fails a basic structural sanity
    check (wrong page count, empty output, etc)."""


def _draw_char_placement(c: canvas.Canvas, page_height: float, p: CharPlacement, font: str) -> None:
    box_width = p.x_right - p.x_left
    box_height = p.y_bottom - p.y_top

    c.setFont(font, p.font_size)

    # Center the single character inside its box horizontally, and sit
    # it a couple of points above the box's bottom edge vertically.
    text_width = c.stringWidth(p.char, font, p.font_size)
    x = p.x_left + max((box_width - text_width) / 2, 0)

    # Convert from top-left-origin (template measurement space) to
    # PDF/reportlab's bottom-left-origin canvas space.
    y_bottom_pdf = page_height - p.y_bottom
    y = y_bottom_pdf + max((box_height - p.font_size) / 2, 1.5)

    c.drawString(x, y, p.char)


def _draw_text_placement(c: canvas.Canvas, page_height: float, p: TextPlacement, font: str) -> None:
    c.setFont(font, p.font_size)
    y_pdf = page_height - p.y_baseline
    c.drawString(p.x, y_pdf, p.text)


def _draw_checkbox_placement(c: canvas.Canvas, page_height: float, p: CheckboxPlacement) -> None:
    if p.cover:
        cx0, cy0, cx1, cy1 = p.cover
        c.saveState()
        c.setFillColor(white)
        # Small margin so we fully erase the covered text without
        # visibly clipping the box we're about to draw.
        c.rect(
            cx0 - 1,
            page_height - cy1 - 1,
            (cx1 - cx0) + 2,
            (cy1 - cy0) + 2,
            stroke=0,
            fill=1,
        )
        c.restoreState()

    box_left = p.x_left
    box_bottom_pdf = page_height - p.y_bottom
    box_width = p.x_right - p.x_left
    box_height = p.y_bottom - p.y_top

    c.saveState()
    c.setLineWidth(0.8)
    c.rect(box_left, box_bottom_pdf, box_width, box_height, stroke=1, fill=0)

    # Checkmark drawn as two strokes (not a font glyph) so it renders
    # identically regardless of which base font is configured.
    c.setLineWidth(1.1)
    c.line(
        box_left + box_width * 0.18,
        box_bottom_pdf + box_height * 0.5,
        box_left + box_width * 0.42,
        box_bottom_pdf + box_height * 0.22,
    )
    c.line(
        box_left + box_width * 0.42,
        box_bottom_pdf + box_height * 0.22,
        box_left + box_width * 0.85,
        box_bottom_pdf + box_height * 0.8,
    )
    c.restoreState()


def fill_pdf(
    template_path: str,
    page_count: int,
    page_width: float,
    page_height: float,
    placements: List[Placement],
    font: str = "Courier",
) -> bytes:
    """
    Render `placements` onto a copy of `template_path` and return the
    resulting PDF as bytes. The original template's pages, layout, and
    background are preserved untouched — placements are drawn on a
    transparent overlay per page and merged on top.
    """

    reader = PdfReader(template_path)

    if len(reader.pages) != page_count:
        raise PdfFillQAError(
            f"Template page count mismatch: mapping expects "
            f"{page_count} pages, but '{template_path}' has "
            f"{len(reader.pages)}."
        )

    by_page: dict[int, List[Placement]] = {}
    for placement in placements:
        by_page.setdefault(placement.page, []).append(placement)

    writer = PdfWriter()

    for index, template_page in enumerate(reader.pages):
        page_placements = by_page.get(index, [])

        if page_placements:
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=(page_width, page_height))

            for placement in page_placements:
                if isinstance(placement, CheckboxPlacement):
                    _draw_checkbox_placement(c, page_height, placement)
                elif isinstance(placement, CharPlacement):
                    _draw_char_placement(c, page_height, placement, font)
                elif isinstance(placement, TextPlacement):
                    _draw_text_placement(c, page_height, placement, font)

            c.save()
            buffer.seek(0)

            overlay_reader = PdfReader(buffer)
            template_page.merge_page(overlay_reader.pages[0])

        writer.add_page(template_page)

    output = BytesIO()
    writer.write(output)
    filled_bytes = output.getvalue()

    # -----------------------------------------------------------
    # Final structural QA check — this is NOT a visual check (a
    # human still has to look at the rendered PDF), only a sanity
    # check that the merge didn't drop or duplicate pages.
    # -----------------------------------------------------------

    if not filled_bytes:
        raise PdfFillQAError("PDF generation produced an empty file.")

    verify_reader = PdfReader(BytesIO(filled_bytes))

    if len(verify_reader.pages) != page_count:
        raise PdfFillQAError(
            f"Generated PDF has {len(verify_reader.pages)} pages, "
            f"expected {page_count}."
        )

    return filled_bytes
