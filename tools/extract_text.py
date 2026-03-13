from io import BytesIO
from .base import PDFTool
from .utils import open_pdf, check_encrypted

MAX_TEXT_PAGES = 200  # Prevent huge string accumulation


class ExtractTextTool(PDFTool):
    id = "extract-text"
    name = "Extrair Texto"
    description = "Extraia todo o texto de um PDF em formato .txt"
    icon = "📝"
    multiple_files = False
    accept = ".pdf"

    def process(self, files: list, options: dict) -> dict:
        if not files:
            return {"error": "Envie um arquivo PDF."}

        reader, err = open_pdf(files[0])
        if err:
            return {"error": err}

        err = check_encrypted(reader, files[0].filename)
        if err:
            return {"error": err}

        pages = reader.pages[:MAX_TEXT_PAGES]
        lines = []
        for i, page in enumerate(pages):
            text = page.extract_text() or ""
            lines.append(f"=== Página {i + 1} ===\n{text}\n")

        if len(reader.pages) > MAX_TEXT_PAGES:
            lines.append(f"\n[Aviso: apenas as primeiras {MAX_TEXT_PAGES} páginas foram extraídas.]")

        content = "\n".join(lines).encode("utf-8")
        return {"file": content, "filename": "texto_extraido.txt", "mimetype": "text/plain; charset=utf-8"}
