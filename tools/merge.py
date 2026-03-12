from pypdf import PdfWriter, PdfReader
from io import BytesIO
from .base import PDFTool


class MergeTool(PDFTool):
    id = "merge"
    name = "Unir PDFs"
    description = "Combine múltiplos PDFs em um único arquivo"
    icon = "🔗"
    multiple_files = True
    accept = ".pdf"

    def process(self, files: list, options: dict) -> dict:
        if len(files) < 2:
            return {"error": "Envie pelo menos 2 arquivos PDF para unir."}

        writer = PdfWriter()
        for f in files:
            reader = PdfReader(f)
            for page in reader.pages:
                writer.add_page(page)

        output = BytesIO()
        writer.write(output)
        output.seek(0)
        return {"file": output.read(), "filename": "unido.pdf", "mimetype": "application/pdf"}
