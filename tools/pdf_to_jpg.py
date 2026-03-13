from io import BytesIO
import zipfile
from .base import PDFTool


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

        dpi = max(72, min(dpi, 300))  # clamp between 72 and 300

        pdf_bytes = files[0].read()

        try:
            images = convert_from_bytes(pdf_bytes, dpi=dpi)
        except Exception as e:
            return {"error": f"Erro ao converter o PDF: {str(e)}"}

        if len(images) == 1:
            # Single page — return JPG directly
            buf = BytesIO()
            images[0].save(buf, format="JPEG", quality=90)
            buf.seek(0)
            return {"file": buf.read(), "filename": "pagina_1.jpg", "mimetype": "image/jpeg"}

        # Multiple pages — return ZIP
        zip_buf = BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, img in enumerate(images):
                img_buf = BytesIO()
                img.save(img_buf, format="JPEG", quality=90)
                zf.writestr(f"pagina_{i + 1}.jpg", img_buf.getvalue())

        zip_buf.seek(0)
        return {"file": zip_buf.read(), "filename": "paginas.zip", "mimetype": "application/zip"}
