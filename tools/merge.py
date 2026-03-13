from pypdf import PdfWriter
from io import BytesIO
import gc
from .base import PDFTool
from .utils import open_pdf, check_encrypted

MAX_TOTAL_PAGES = 300


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
            reader, err = open_pdf(f)
            if err:
                return {"error": err}

            err = check_encrypted(reader, f.filename)
            if err:
                return {"error": err}

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
