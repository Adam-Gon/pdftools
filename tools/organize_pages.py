from pypdf import PdfWriter, PdfReader
from io import BytesIO
from .base import PDFTool


class OrganizePagesTool(PDFTool):
    id = "organize-pages"
    name = "Organizar PDF"
    description = "Reordene as páginas de um PDF na ordem que desejar"
    icon = "🔀"
    multiple_files = False
    accept = ".pdf"

    def process(self, files: list, options: dict) -> dict:
        if not files:
            return {"error": "Envie um arquivo PDF."}

        raw = options.get("order", "").strip()
        if not raw:
            return {"error": "Informe a nova ordem das páginas (ex: 3, 1, 2)."}

        reader = PdfReader(files[0])
        total = len(reader.pages)

        try:
            order = [int(p.strip()) for p in raw.split(",")]
        except ValueError:
            return {"error": "Formato inválido. Use números separados por vírgula (ex: 3, 1, 2)."}

        if any(p < 1 or p > total for p in order):
            return {"error": f"Número de página inválido. O PDF tem {total} páginas."}

        writer = PdfWriter()
        for p in order:
            writer.add_page(reader.pages[p - 1])

        output = BytesIO()
        writer.write(output)
        output.seek(0)
        return {"file": output.read(), "filename": "organizado.pdf", "mimetype": "application/pdf"}
