from pypdf import PdfWriter, PdfReader
from io import BytesIO
from .base import PDFTool


class RotateTool(PDFTool):
    id = "rotate"
    name = "Girar PDF"
    description = "Gire todas as páginas de um PDF em 90°, 180° ou 270°"
    icon = "🔄"
    multiple_files = False
    accept = ".pdf"

    def process(self, files: list, options: dict) -> dict:
        if not files:
            return {"error": "Envie um arquivo PDF."}

        try:
            degrees = int(options.get("degrees", 90))
        except ValueError:
            return {"error": "Ângulo inválido."}

        if degrees not in (90, 180, 270):
            return {"error": "Ângulo deve ser 90, 180 ou 270."}

        reader = PdfReader(files[0])
        writer = PdfWriter()
        for page in reader.pages:
            page.rotate(degrees)
            writer.add_page(page)

        output = BytesIO()
        writer.write(output)
        output.seek(0)
        return {"file": output.read(), "filename": "girado.pdf", "mimetype": "application/pdf"}
