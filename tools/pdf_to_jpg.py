from io import BytesIO
import zipfile
import gc
from .base import PDFTool
from .utils import open_pdf, check_encrypted

MAX_PAGES = 30  # Conservative limit: 30 pages * ~2s each = ~60s, safe under 120s timeout


class PdfToJpgTool(PDFTool):
    id = "pdf-to-jpg"
    name = "PDF para JPG"
    description = "Converta cada página do PDF em uma imagem JPG"
    icon = "🖼️"
    multiple_files = False
    accept = ".pdf"

    def process(self, files: list, options: dict) -> dict:
        if not files:
            return {"error": "Envie um arquivo PDF."}

        try:
            from pdf2image import convert_from_bytes
        except ImportError:
            return {"error": "Biblioteca pdf2image não instalada no servidor."}

        try:
            dpi = int(options.get("dpi", 150))
        except ValueError:
            dpi = 150
        dpi = max(72, min(dpi, 200))

        # Validate PDF first
        reader, err = open_pdf(files[0])
        if err:
            return {"error": err}

        err = check_encrypted(reader, files[0].filename)
        if err:
            return {"error": err}

        total_pages = len(reader.pages)
        if total_pages > MAX_PAGES:
            return {"error": f"Este PDF tem {total_pages} páginas. O limite é {MAX_PAGES} páginas por conversão."}

        # Read bytes AFTER validation, then delete reader to free memory
        files[0].seek(0)
        pdf_bytes = files[0].read()
        del reader
        gc.collect()

        try:
            zip_buf = BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for page_num in range(1, total_pages + 1):
                    images = convert_from_bytes(
                        pdf_bytes,
                        dpi=dpi,
                        first_page=page_num,
                        last_page=page_num,
                    )
                    img_buf = BytesIO()
                    images[0].save(img_buf, format="JPEG", quality=85)
                    zf.writestr(f"pagina_{page_num}.jpg", img_buf.getvalue())
                    del images, img_buf
                    gc.collect()

            # Free pdf_bytes after all pages processed
            del pdf_bytes
            gc.collect()

            zip_buf.seek(0)

            if total_pages == 1:
                with zipfile.ZipFile(BytesIO(zip_buf.getvalue())) as zf:
                    jpg_bytes = zf.read("pagina_1.jpg")
                return {"file": jpg_bytes, "filename": "pagina_1.jpg", "mimetype": "image/jpeg"}

            return {"file": zip_buf.read(), "filename": "paginas.zip", "mimetype": "application/zip"}

        except Exception as e:
            return {"error": f"Erro ao converter o PDF: {str(e)}"}
