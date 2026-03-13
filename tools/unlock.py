from pypdf import PdfWriter, PdfReader
from io import BytesIO
from .base import PDFTool


class UnlockTool(PDFTool):
    id = "unlock"
    name = "Desbloquear PDF"
    description = "Remova a senha de um PDF protegido"
    icon = "🔓"
    multiple_files = False
    accept = ".pdf"

    def process(self, files: list, options: dict) -> dict:
        if not files:
            return {"error": "Envie um arquivo PDF."}

        password = options.get("password", "").strip()

        reader = PdfReader(files[0])

        if not reader.is_encrypted:
            return {"error": "Este PDF não está protegido por senha."}

        if not password:
            return {"error": "Informe a senha do PDF."}

        try:
            result = reader.decrypt(password)
            if result == 0:
                return {"error": "Senha incorreta."}
        except Exception:
            return {"error": "Não foi possível desbloquear o PDF. Verifique a senha."}

        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        output = BytesIO()
        writer.write(output)
        output.seek(0)
        return {"file": output.read(), "filename": "desbloqueado.pdf", "mimetype": "application/pdf"}
