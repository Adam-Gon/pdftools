from pypdf import PdfWriter
from io import BytesIO
from .base import PDFTool
from .utils import open_pdf, check_encrypted, parse_page_ranges


class ExtractPagesTool(PDFTool):
    id = "extract-pages"
    name = "Extrair Páginas"
    description = "Extraia páginas específicas de um PDF em um novo arquivo"
    icon = "📤"
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

        raw = options.get("pages", "").strip()
        if not raw:
            return {"error": "Informe as páginas a extrair (ex: 1, 3-5)."}

        total = len(reader.pages)
        pages_to_extract, err = parse_page_ranges(raw, total)
        if err:
            return {"error": err}

        writer = PdfWriter()
        for i in pages_to_extract:
            writer.add_page(reader.pages[i])

        output = BytesIO()
        writer.write(output)
        output.seek(0)
        return {"file": output.read(), "filename": "paginas_extraidas.pdf", "mimetype": "application/pdf"}
