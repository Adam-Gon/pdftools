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

        for page in reader.pages:
            if level in ("medium", "high"):
                page.compress_content_streams()
            writer.add_page(page)

        # Remove metadata to save space
        if level == "high":
            writer.add_metadata({})

        # Compress embedded objects
        for page in writer.pages:
            for key in ["/Resources", "/Font", "/XObject"]:
                try:
                    obj = page.get(key)
                    if obj:
                        obj.compress_content_streams()
                except Exception:
                    pass

        output = BytesIO()
        writer.write(output)
        output.seek(0)

        result_bytes = output.read()
        original_size = files[0].seek(0, 2)  # seek to end to get size
        files[0].seek(0)

        return {
            "file": result_bytes,
            "filename": "comprimido.pdf",
            "mimetype": "application/pdf",
        }
