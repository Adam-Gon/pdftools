from pypdf import PdfWriter, PdfReader
from io import BytesIO
from .base import PDFTool


class ExtractPagesTool(PDFTool):
    id = "extract-pages"
    name = "Extrair Páginas"
    description = "Extraia páginas específicas de um PDF em um novo arquivo"
    icon = "📤"
    multiple_files = False
    accept = ".pdf"

    def process(self, files: list, options: dict) -> dict:
        if not files:
            return {"error": "Envie um arquivo PDF."}

        raw = options.get("pages", "").strip()
        if not raw:
            return {"error": "Informe as páginas a extrair (ex: 1, 3-5)."}

        reader = PdfReader(files[0])
        total = len(reader.pages)

        pages_to_extract = self._parse_ranges(raw, total)
        if pages_to_extract is None:
            return {"error": f"Intervalo inválido. O PDF tem {total} páginas."}

        writer = PdfWriter()
        for i in sorted(pages_to_extract):
            writer.add_page(reader.pages[i])

        output = BytesIO()
        writer.write(output)
        output.seek(0)
        return {"file": output.read(), "filename": "paginas_extraidas.pdf", "mimetype": "application/pdf"}

    def _parse_ranges(self, raw: str, total: int):
        indices = set()
        try:
            for part in raw.split(","):
                part = part.strip()
                if "-" in part:
                    start, end = part.split("-")
                    start, end = int(start), int(end)
                    if start < 1 or end > total or start > end:
                        return None
                    indices.update(range(start - 1, end))
                else:
                    p = int(part)
                    if p < 1 or p > total:
                        return None
                    indices.add(p - 1)
        except (ValueError, TypeError):
            return None
        return indices
