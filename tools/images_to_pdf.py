from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import gc
from .base import PDFTool

# Max dimension in pixels before resizing — prevents huge RAW/DSLR images crashing the server
MAX_DIMENSION = 4000


class ImagesToPdfTool(PDFTool):
    id = "images-to-pdf"
    name = "Imagens para PDF"
    description = "Converta JPG, PNG, WEBP e outras imagens em um único PDF"
    icon = "🖼️"
    multiple_files = True
    accept = ".jpg,.jpeg,.png,.webp,.bmp,.tiff,.gif"

    def process(self, files: list, options: dict) -> dict:
        if not files:
            return {"error": "Envie pelo menos uma imagem."}

        page_size = options.get("page_size", "auto")
        fit       = options.get("fit", "fit")

        output = BytesIO()
        pdf = canvas.Canvas(output)

        for f in files:
            try:
                img = Image.open(f)
            except Exception:
                return {"error": f"Não foi possível abrir '{f.filename}'. Envie apenas imagens válidas."}

            # Convert color mode
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Resize if image is too large to prevent RAM spike
            w, h = img.size
            if max(w, h) > MAX_DIMENSION:
                scale = MAX_DIMENSION / max(w, h)
                img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

            img_w, img_h = img.size

            # Page dimensions
            if page_size == "a4":
                page_w, page_h = A4
            else:
                dpi = img.info.get("dpi", (96, 96))
                if isinstance(dpi, (int, float)):
                    dpi = (dpi, dpi)
                dpi_x, dpi_y = dpi if dpi[0] > 0 else (96, 96)
                page_w = img_w / dpi_x * 72
                page_h = img_h / dpi_y * 72

            pdf.setPageSize((page_w, page_h))

            # Draw position
            if fit == "fill":
                draw_w, draw_h = page_w, page_h
                x, y = 0, 0
            else:
                scale = min(page_w / img_w, page_h / img_h)
                draw_w = img_w * scale
                draw_h = img_h * scale
                x = (page_w - draw_w) / 2
                y = (page_h - draw_h) / 2

            img_buffer = BytesIO()
            img.save(img_buffer, format="JPEG", quality=88)
            img_buffer.seek(0)

            pdf.drawImage(ImageReader(img_buffer), x, y, width=draw_w, height=draw_h,
                          preserveAspectRatio=(fit == "fit"))
            pdf.showPage()

            # Free image from memory before loading the next one
            del img, img_buffer
            gc.collect()

        pdf.save()
        output.seek(0)
        return {"file": output.read(), "filename": "imagens.pdf", "mimetype": "application/pdf"}
