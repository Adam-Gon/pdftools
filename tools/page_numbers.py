from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from io import BytesIO
import gc
from .base import PDFTool


class PageNumbersTool(PDFTool):
    id = "page-numbers"
    name = "Numerar Páginas"
    description = "Insira números de página em todas as páginas do PDF"
    icon = "🔢"
    multiple_files = False
    accept = ".pdf"

    def process(self, files: list, options: dict) -> dict:
        if not files:
            return {"error": "Envie um arquivo PDF."}

        position  = options.get("position", "bottom-center")
        start     = int(options.get("start", 1))
        fmt       = options.get("format", "n")
        font_size = int(options.get("font_size", 14))
        font_size = max(6, min(font_size, 72))

        reader = PdfReader(files[0])
        total  = len(reader.pages)
        writer = PdfWriter()

        # Cache overlays by (page_size, label) to avoid rebuilding identical pages
        overlay_cache: dict = {}

        for idx, page in enumerate(reader.pages):
            box = page.mediabox
            pw  = float(box.width)
            ph  = float(box.height)

            num = idx + start
            if fmt == "page_n":
                label = f"Página {num}"
            elif fmt == "n_total":
                label = f"{num} / {total + start - 1}"
            else:
                label = str(num)

            cache_key = (round(pw), round(ph), label, position, font_size)

            if cache_key not in overlay_cache:
                buf = BytesIO()
                c = canvas.Canvas(buf, pagesize=(pw, ph))
                c.setFont("Helvetica", font_size)
                c.setFillColorRGB(0.3, 0.3, 0.3)
                margin = font_size * 2
                y = margin if "bottom" in position else ph - margin - font_size
                if "left" in position:
                    c.drawString(margin, y, label)
                elif "right" in position:
                    c.drawRightString(pw - margin, y, label)
                else:
                    c.drawCentredString(pw / 2, y, label)
                c.save()
                overlay_cache[cache_key] = buf.getvalue()

            num_page = PdfReader(BytesIO(overlay_cache[cache_key])).pages[0]
            page.merge_page(num_page)
            writer.add_page(page)

        output = BytesIO()
        writer.write(output)
        output.seek(0)
        gc.collect()
        return {"file": output.read(), "filename": "numerado.pdf", "mimetype": "application/pdf"}
