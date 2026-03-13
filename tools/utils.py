"""
Shared utilities for all PDF tools.
"""

from pypdf import PdfReader
from io import BytesIO

MAX_PAGES = 300  # Global page limit per operation


def open_pdf(file_obj) -> tuple:
    """
    Safely open a PDF file object.
    Returns (reader, error_string) — error is None if successful.
    Checks: valid PDF, not corrupted, page limit.
    """
    try:
        data = file_obj.read()
        file_obj.seek(0)
    except Exception:
        return None, "Não foi possível ler o arquivo enviado."

    # Check PDF signature
    if not data.startswith(b"%PDF"):
        return None, f"'{getattr(file_obj, 'filename', 'arquivo')}' não é um PDF válido."

    try:
        reader = PdfReader(BytesIO(data))
    except Exception:
        return None, f"'{getattr(file_obj, 'filename', 'arquivo')}' está corrompido ou em formato inválido."

    if len(reader.pages) == 0:
        return None, f"'{getattr(file_obj, 'filename', 'arquivo')}' não contém páginas."

    if len(reader.pages) > MAX_PAGES:
        return None, f"'{getattr(file_obj, 'filename', 'arquivo')}' tem {len(reader.pages)} páginas. O limite por operação é {MAX_PAGES} páginas."

    return reader, None


def check_encrypted(reader: PdfReader, filename: str = "arquivo") -> str | None:
    """Returns error string if PDF is encrypted, None if OK."""
    if reader.is_encrypted:
        return f"'{filename}' está protegido por senha. Use a ferramenta 'Desbloquear PDF' primeiro."
    return None


def parse_page_ranges(raw: str, total: int) -> tuple:
    """
    Parse '1-3, 5, 7-9' into a sorted list of 0-indexed page indices.
    Returns (indices, error_string) — error is None if successful.
    """
    indices = set()
    try:
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                start, end = part.split("-", 1)
                start, end = int(start.strip()), int(end.strip())
                if start < 1 or end > total or start > end:
                    return None, f"Intervalo '{part}' inválido. O PDF tem {total} páginas."
                indices.update(range(start - 1, end))
            else:
                p = int(part)
                if p < 1 or p > total:
                    return None, f"Página {p} inválida. O PDF tem {total} páginas."
                indices.add(p - 1)
    except (ValueError, TypeError):
        return None, "Formato inválido. Use números separados por vírgula (ex: 1, 3-5, 7)."

    if not indices:
        return None, "Nenhuma página válida informada."

    return sorted(indices), None
