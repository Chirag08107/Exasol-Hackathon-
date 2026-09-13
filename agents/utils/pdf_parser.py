from io import BytesIO
from typing import Union

from pypdf import PdfReader


def extract_pdf_text(pdf_data: Union[bytes, bytearray]) -> str:
    reader = PdfReader(BytesIO(pdf_data))

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    return "\n".join(pages).strip()