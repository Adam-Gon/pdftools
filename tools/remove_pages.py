from pypdf import PdfWriter
from io import BytesIO
from .base import PDFTool
from .utils import open_pdf, check_encrypted, parse_page_ranges


class RemovePagesTool(PDFTool):
    id = "remove-pages"
    name = "Remover Páginas"
    description = "Remova páginas específicas de um PDF"
    icon = "🗑️"
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
            return {"error": "Informe as páginas a remover (ex: 1, 3-5)."}

        total = len(reader.pages)
        pages_to_remove, err = parse_page_ranges(raw, total)
        if err:
            return {"error": err}

        if len(pages_to_remove) >= total:
            return {"error": "Você não pode remover todas as páginas do PDF."}

        pages_to_remove_set = set(pages_to_remove)
        writer = PdfWriter()
        for i, page in enumerate(reader.pages):
            if i not in pages_to_remove_set:
                writer.add_page(page)

        output = BytesIO()
        writer.write(output)
        output.seek(0)
        return {"file": output.read(), "filename": "sem_paginas.pdf", "mimetype": "application/pdf"}
