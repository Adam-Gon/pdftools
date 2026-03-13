from pypdf import PdfWriter, PdfReader, PasswordType
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

        try:
            data = files[0].read()
            files[0].seek(0)
        except Exception:
            return {"error": "Não foi possível ler o arquivo enviado."}

        if not data.startswith(b"%PDF"):
            return {"error": f"'{files[0].filename}' não é um PDF válido."}

        try:
            reader = PdfReader(BytesIO(data))
        except Exception:
            return {"error": f"'{files[0].filename}' está corrompido ou em formato inválido."}

        if not reader.is_encrypted:
            return {"error": "Este PDF não está protegido por senha."}

        password = options.get("password", "").strip()
        if not password:
            return {"error": "Informe a senha do PDF."}

        try:
            result = reader.decrypt(password)
            # PasswordType.NOT_DECRYPTED == 0 means wrong password
            if result == PasswordType.NOT_DECRYPTED:
                return {"error": "Senha incorreta. Verifique e tente novamente."}
        except Exception:
            return {"error": "Não foi possível desbloquear o PDF. Verifique a senha."}

        if len(reader.pages) == 0:
            return {"error": "O PDF não contém páginas."}

        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        output = BytesIO()
        writer.write(output)
        output.seek(0)
        return {"file": output.read(), "filename": "desbloqueado.pdf", "mimetype": "application/pdf"}
