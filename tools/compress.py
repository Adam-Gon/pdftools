from pypdf import PdfWriter
from io import BytesIO
import gc
from .base import PDFTool
from .utils import open_pdf, check_encrypted


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

        reader, err = open_pdf(files[0])
        if err:
            return {"error": err}

        err = check_encrypted(reader, files[0].filename)
        if err:
            return {"error": err}

        level = options.get("level", "medium")

        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        if level in ("medium", "high"):
            for i, page in enumerate(writer.pages):
                try:
                    page.compress_content_streams()
                except Exception:
                    pass
                if i % 5 == 0:
                    gc.collect()

        if level == "high":
            writer.add_metadata({})

        output = BytesIO()
        writer.write(output)
        output.seek(0)
        gc.collect()
        return {"file": output.read(), "filename": "comprimido.pdf", "mimetype": "application/pdf"}
