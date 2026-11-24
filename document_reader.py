"""Leitura de PDF e DOCX para um texto único, preservando a estrutura útil ao modelo.

- PDF: o texto de cada página é precedido por um marcador [PÁGINA n].
- DOCX: títulos viram linhas "## Título" e tabelas viram linhas "célula | célula".
  O sumário automático (campo do Word) é ignorado por não trazer conteúdo.
"""
import io

import pymupdf
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

SUPPORTED_EXTENSIONS = ("pdf", "docx")


def read_document(file_bytes: bytes, filename: str) -> str:
    extension = filename.rsplit(".", 1)[-1].lower()
    if extension == "pdf":
        return _read_pdf(file_bytes)
    if extension == "docx":
        return _read_docx(file_bytes)
    raise ValueError(f"Formato não suportado: .{extension}. Use PDF ou DOCX.")


def _read_pdf(file_bytes: bytes) -> str:
    blocks = []
    with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:
        for index, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            if text:
                blocks.append(f"[PÁGINA {index}]\n{text}")
    return "\n\n".join(blocks)


def _is_heading(paragraph: Paragraph) -> bool:
    style = (paragraph.style.name or "").lower() if paragraph.style is not None else ""
    return style.startswith(("heading", "título", "titulo", "title"))


def _table_lines(table: Table) -> list[str]:
    lines = []
    for row in table.rows:
        cells = []
        previous = None
        for cell in row.cells:
            # Células mescladas são repetidas pelo python-docx; evita duplicar.
            if previous is not None and cell._tc is previous:
                continue
            previous = cell._tc
            cells.append(" ".join(cell.text.split()))
        if any(cells):
            lines.append(" | ".join(cells))
    return lines


def _read_docx(file_bytes: bytes) -> str:
    document = Document(io.BytesIO(file_bytes))
    lines = []
    for block in document.iter_inner_content():
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if not text:
                continue
            lines.append(f"## {text}" if _is_heading(block) else text)
        elif isinstance(block, Table):
            table = _table_lines(block)
            if table:
                lines.append("[TABELA]")
                lines.extend(table)
                lines.append("[FIM DA TABELA]")
    return "\n".join(lines)
