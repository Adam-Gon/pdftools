from pypdf import PdfWriter, PdfReader
from io import BytesIO
from .base import PDFTool
import gc


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

        level = options.get("level", "medium")

        reader = PdfReader(files[0])
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        # Compress page by page and force garbage collection between each
        # to avoid memory spikes on the Render free tier (512MB RAM)
        if level in ("medium", "high"):
            for i, page in enumerate(writer.pages):
                try:
                    page.compress_content_streams()
                except Exception:
                    pass  # Skip pages that fail, don't crash the whole process
                if i % 5 == 0:
                    gc.collect()  # Free memory every 5 pages

        if level == "high":
            writer.add_metadata({})

        output = BytesIO()
        writer.write(output)
        output.seek(0)

        gc.collect()

        return {
            "file": output.read(),
            "filename": "comprimido.pdf",
            "mimetype": "application/pdf",
        }
