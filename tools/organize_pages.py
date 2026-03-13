from pypdf import PdfWriter
from io import BytesIO
from .base import PDFTool
from .utils import open_pdf, check_encrypted

MAX_ORDER_ENTRIES = 500  # Prevent "1,1,1,1..." DoS with thousands of repeated pages


class OrganizePagesTool(PDFTool):
    id = "organize-pages"
    name = "Organizar PDF"
    description = "Reordene as páginas de um PDF na ordem que desejar"
    icon = "🔀"
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

        raw = options.get("order", "").strip()
        if not raw:
            return {"error": "Informe a nova ordem das páginas (ex: 3, 1, 2)."}

        total = len(reader.pages)

        try:
            order = [int(p.strip()) for p in raw.split(",") if p.strip()]
        except ValueError:
            return {"error": "Formato inválido. Use números separados por vírgula (ex: 3, 1, 2)."}

        if not order:
            return {"error": "Nenhuma página informada."}

        if len(order) > MAX_ORDER_ENTRIES:
            return {"error": f"Muitas entradas. O limite é {MAX_ORDER_ENTRIES} páginas por operação."}

        invalid = [p for p in order if p < 1 or p > total]
        if invalid:
            return {"error": f"Página(s) inválida(s): {invalid}. O PDF tem {total} páginas."}

        writer = PdfWriter()
        for p in order:
            writer.add_page(reader.pages[p - 1])

        output = BytesIO()
        writer.write(output)
        output.seek(0)
        return {"file": output.read(), "filename": "organizado.pdf", "mimetype": "application/pdf"}
