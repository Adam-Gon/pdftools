from pypdf import PdfWriter, PdfReader
from io import BytesIO
from .base import PDFTool


class CompressTool(PDFTool):
    id = "compress"
    name = "Comprimir PDF"
    description = "Reduza o tamanho do seu arquivo PDF"
    icon = "🗜️"
    multiple_files = False
    accept = ".pdf"

    def process(self, files: list, options: dict) -> dict:
        if not files:
            return {"error": "Envie um arquivo PDF."}

        level = options.get("level", "medium")  # "low", "medium", "high"

        reader = PdfReader(files[0])
        writer = PdfWriter()

        # Pages must be added to the writer BEFORE compressing
        for page in reader.pages:
            writer.add_page(page)

        # Compress after pages are part of the writer
        if level in ("medium", "high"):
            for page in writer.pages:
                page.compress_content_streams()

        # Remove metadata on high level to save extra space
        if level == "high":
            writer.add_metadata({})

        output = BytesIO()
        writer.write(output)
        output.seek(0)
        return {
            "file": output.read(),
            "filename": "comprimido.pdf",
            "mimetype": "application/pdf",
        }
