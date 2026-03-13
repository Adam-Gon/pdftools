from io import BytesIO
import zipfile
import gc
from .base import PDFTool

MAX_PAGES = 40  # Safety limit for free tier RAM


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

        dpi = max(72, min(dpi, 200))  # Cap at 200 DPI on free tier (300 crashes)

        pdf_bytes = files[0].read()

        # Check page count before converting
        try:
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(pdf_bytes))
            total_pages = len(reader.pages)
            del reader
            gc.collect()
        except Exception:
            total_pages = 999

        if total_pages > MAX_PAGES:
            return {"error": f"Este PDF tem {total_pages} páginas. O limite é {MAX_PAGES} páginas por conversão para evitar sobrecarga do servidor."}

        # Convert page by page to keep memory low
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

            zip_buf.seek(0)

            # If single page, return JPG directly instead of ZIP
            if total_pages == 1:
                with zipfile.ZipFile(BytesIO(zip_buf.getvalue())) as zf:
                    jpg_bytes = zf.read("pagina_1.jpg")
                return {"file": jpg_bytes, "filename": "pagina_1.jpg", "mimetype": "image/jpeg"}

            return {"file": zip_buf.read(), "filename": "paginas.zip", "mimetype": "application/zip"}

        except Exception as e:
            return {"error": f"Erro ao converter o PDF: {str(e)}"}
