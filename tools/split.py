from pypdf import PdfWriter
from io import BytesIO
import zipfile
import gc
from .base import PDFTool
from .utils import open_pdf, check_encrypted, parse_page_ranges

MAX_SPLIT_PAGES = 100


class SplitTool(PDFTool):
    id = "split"
    name = "Dividir PDF"
    description = "Separe um PDF em páginas individuais ou por intervalos"
    icon = "✂️"
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

        total = len(reader.pages)
        mode  = options.get("mode", "all")

        if mode == "range":
            raw = options.get("pages", "").strip()
            if not raw:
                return {"error": "Informe o intervalo de páginas (ex: 1-3, 5)."}
            pages_to_extract, err = parse_page_ranges(raw, total)
            if err:
                return {"error": err}
        else:
            pages_to_extract = list(range(total))

        if len(pages_to_extract) > MAX_SPLIT_PAGES:
            return {"error": f"Muitas páginas para dividir de uma vez. Limite: {MAX_SPLIT_PAGES} páginas."}

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for page_idx in pages_to_extract:
                writer = PdfWriter()
                writer.add_page(reader.pages[page_idx])
                pdf_buffer = BytesIO()
                writer.write(pdf_buffer)
                zf.writestr(f"pagina_{page_idx + 1}.pdf", pdf_buffer.getvalue())
                del writer, pdf_buffer
                gc.collect()

        zip_buffer.seek(0)
        return {"file": zip_buffer.read(), "filename": "paginas.zip", "mimetype": "application/zip"}
