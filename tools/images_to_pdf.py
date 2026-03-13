from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import gc
from .base import PDFTool

MAX_DIMENSION = 4000  # Max px per side before resizing


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
        if fit not in ("fit", "fill", "original"):
            fit = "fit"

        output = BytesIO()
        pdf = canvas.Canvas(output)

        for f in files:
            try:
                img = Image.open(f)
                img.load()  # Force full decode to catch corrupt files early
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

            # Resize oversized images
            w, h = img.size
            if w <= 0 or h <= 0:
                return {"error": f"'{f.filename}' tem dimensões inválidas."}

            if max(w, h) > MAX_DIMENSION:
                scale = MAX_DIMENSION / max(w, h)
                img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)

            img_w, img_h = img.size

            # Page dimensions
            if page_size == "a4":
                page_w, page_h = A4
            else:
                dpi = img.info.get("dpi", (96, 96))
                if isinstance(dpi, (int, float)):
                    dpi = (dpi, dpi)
                dpi_x, dpi_y = dpi if (isinstance(dpi, tuple) and dpi[0] > 0) else (96, 96)
                page_w = img_w / dpi_x * 72
                page_h = img_h / dpi_y * 72

            # Guard against zero page dimensions
            if page_w <= 0 or page_h <= 0:
                page_w, page_h = A4

            pdf.setPageSize((page_w, page_h))

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

            del img, img_buffer
            gc.collect()

        pdf.save()
        output.seek(0)
        return {"file": output.read(), "filename": "imagens.pdf", "mimetype": "application/pdf"}
