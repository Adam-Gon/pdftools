from pypdf import PdfReader
from io import BytesIO
from .base import PDFTool


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

        reader = PdfReader(files[0])
        lines = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            lines.append(f"=== Página {i + 1} ===\n{text}\n")

        content = "\n".join(lines).encode("utf-8")
        return {
            "file": content,
            "filename": "texto_extraido.txt",
            "mimetype": "text/plain; charset=utf-8",
        }
