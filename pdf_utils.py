"""
pdf_utils.py
Handles extraction of raw text from an uploaded PDF file.
"""

import pdfplumber
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts all readable text from a PDF given as raw bytes.

    Args:
        file_bytes: The raw bytes of the uploaded PDF file.

    Returns:
        A single string containing the text of every page,
        separated by page-break markers (useful for traceability).
    """
    text_chunks = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_chunks.append(f"\n--- Page {page_number} ---\n{page_text}")

    full_text = "\n".join(text_chunks).strip()
    return full_text


def chunk_text(text: str, max_chars: int = 12000) -> list[str]:
    """
    Splits long text into chunks that comfortably fit inside a single
    LLM call. Splits on paragraph boundaries where possible so claims
    are not cut in half.

    Args:
        text: The full document text.
        max_chars: Approximate max characters per chunk.

    Returns:
        List of text chunks.
    """
    if len(text) <= max_chars:
        return [text]

    paragraphs = text.split("\n")
    chunks = []
    current = []
    current_len = 0

    for para in paragraphs:
        if current_len + len(para) > max_chars and current:
            chunks.append("\n".join(current))
            current = []
            current_len = 0
        current.append(para)
        current_len += len(para)

    if current:
        chunks.append("\n".join(current))

    return chunks
