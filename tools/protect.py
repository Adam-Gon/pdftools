from pypdf import PdfWriter, PdfReader
from io import BytesIO
from .base import PDFTool


class ProtectTool(PDFTool):
    id = "protect"
    name = "Proteger PDF"
    description = "Adicione uma senha para proteger seu PDF"
    icon = "🔒"
    multiple_files = False
    accept = ".pdf"

    def process(self, files: list, options: dict) -> dict:
        if not files:
            return {"error": "Envie um arquivo PDF."}

        password = options.get("password", "").strip()
        if not password:
            return {"error": "Informe uma senha."}
        if len(password) < 4:
            return {"error": "A senha deve ter pelo menos 4 caracteres."}

        reader = PdfReader(files[0])

        if reader.is_encrypted:
            return {"error": "Este PDF já está protegido por senha."}

        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        writer.encrypt(password)

        output = BytesIO()
        writer.write(output)
        output.seek(0)
        return {"file": output.read(), "filename": "protegido.pdf", "mimetype": "application/pdf"}
