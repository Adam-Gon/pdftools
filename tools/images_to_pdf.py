from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from .base import PDFTool


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

        page_size = options.get("page_size", "auto")  # "auto", "a4", "original"
        fit = options.get("fit", "fit")                # "fit", "fill", "original"

        output = BytesIO()
        pdf = canvas.Canvas(output)

        for f in files:
            try:
                img = Image.open(f)
            except Exception:
                return {"error": f"Não foi possível abrir o arquivo '{f.filename}'. Certifique-se de enviar imagens válidas."}

            # Convert to RGB (remove alpha / palette modes)
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            img_w, img_h = img.size  # pixels

            # Determine page dimensions (points, 1pt = 1/72 inch)
            if page_size == "a4":
                page_w, page_h = A4
            else:
                # "auto" / "original" — use image dimensions converted to points at 96 dpi
                dpi = img.info.get("dpi", (96, 96))
                if isinstance(dpi, (int, float)):
                    dpi = (dpi, dpi)
                dpi_x, dpi_y = dpi if dpi[0] > 0 else (96, 96)
                page_w = img_w / dpi_x * 72
                page_h = img_h / dpi_y * 72

            pdf.setPageSize((page_w, page_h))

            # Calculate draw size
            if fit == "original":
                draw_w = img_w / 96 * 72
                draw_h = img_h / 96 * 72
                x = (page_w - draw_w) / 2
                y = (page_h - draw_h) / 2
            elif fit == "fill":
                draw_w, draw_h = page_w, page_h
                x, y = 0, 0
            else:  # "fit" — keep aspect ratio with padding
                scale = min(page_w / img_w, page_h / img_h)
                draw_w = img_w * scale
                draw_h = img_h * scale
                x = (page_w - draw_w) / 2
                y = (page_h - draw_h) / 2

            # Save image to temp buffer for reportlab
            img_buffer = BytesIO()
            img.save(img_buffer, format="JPEG", quality=90)
            img_buffer.seek(0)

            pdf.drawImage(
                ImageReader(img_buffer),
                x, y, width=draw_w, height=draw_h,
                preserveAspectRatio=(fit == "fit"),
            )
            pdf.showPage()

        pdf.save()
        output.seek(0)
        return {
            "file": output.read(),
            "filename": "imagens.pdf",
            "mimetype": "application/pdf",
        }
