import fitz  # PyMuPDF


def extract_pdf_pages(pdf_bytes: bytes) -> list[dict]:
    """Extrai texto por página de um PDF pesquisável."""
    pages = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for index, page in enumerate(doc, start=1):
            pages.append({"page": index, "text": page.get_text("text").strip()})
    return pages
