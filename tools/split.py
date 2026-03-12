from pypdf import PdfWriter, PdfReader
from io import BytesIO
import zipfile
from .base import PDFTool


class SplitTool(PDFTool):
    id = "split"
    name = "Dividir PDF"
    description = "Separe um PDF em páginas individuais ou por intervalos"
    icon = "✂️"
    multiple_files = False
    accept = ".pdf"

    def process(self, files: list, options: dict) -> dict:
        if not files:
            return {"error": "Envie um arquivo PDF."}

        reader = PdfReader(files[0])
        total = len(reader.pages)
        mode = options.get("mode", "all")  # "all" or "range"

        # Determine page ranges to extract
        if mode == "range":
            raw = options.get("pages", "").strip()
            if not raw:
                return {"error": "Informe o intervalo de páginas (ex: 1-3, 5)."}
            pages_to_extract = self._parse_ranges(raw, total)
            if pages_to_extract is None:
                return {"error": f"Intervalo inválido. O PDF tem {total} páginas."}
        else:
            pages_to_extract = list(range(total))

        # Build a zip with one PDF per page
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, page_idx in enumerate(pages_to_extract):
                writer = PdfWriter()
                writer.add_page(reader.pages[page_idx])
                pdf_buffer = BytesIO()
                writer.write(pdf_buffer)
                zf.writestr(f"pagina_{page_idx + 1}.pdf", pdf_buffer.getvalue())

        zip_buffer.seek(0)
        return {
            "file": zip_buffer.read(),
            "filename": "paginas.zip",
            "mimetype": "application/zip",
        }

    def _parse_ranges(self, raw: str, total: int):
        """Parse '1-3, 5, 7-9' into 0-indexed page indices."""
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
        return sorted(indices)
