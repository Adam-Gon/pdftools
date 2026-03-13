from pypdf import PdfWriter, PdfReader
from io import BytesIO
import gc
from .base import PDFTool

MAX_TOTAL_PAGES = 300  # Safety limit to avoid RAM exhaustion


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
        total_pages = 0

        for f in files:
            try:
                reader = PdfReader(f)
            except Exception:
                return {"error": f"Não foi possível ler '{f.filename}'. Certifique-se de enviar PDFs válidos."}

            total_pages += len(reader.pages)
            if total_pages > MAX_TOTAL_PAGES:
                return {"error": f"O total de páginas ultrapassa o limite de {MAX_TOTAL_PAGES} páginas por operação."}

            for page in reader.pages:
                writer.add_page(page)

        output = BytesIO()
        writer.write(output)
        output.seek(0)
        gc.collect()
        return {"file": output.read(), "filename": "unido.pdf", "mimetype": "application/pdf"}
