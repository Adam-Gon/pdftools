from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from io import BytesIO
import gc
from .base import PDFTool
from .utils import open_pdf, check_encrypted


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

        reader, err = open_pdf(files[0])
        if err:
            return {"error": err}

        err = check_encrypted(reader, files[0].filename)
        if err:
            return {"error": err}

        position = options.get("position", "bottom-center")

        try:
            start = int(options.get("start", 1))
            start = max(1, min(start, 9999))
        except (ValueError, TypeError):
            start = 1

        fmt = options.get("format", "n")
        if fmt not in ("n", "page_n", "n_total"):
            fmt = "n"

        try:
            font_size = int(options.get("font_size", 14))
            font_size = max(6, min(font_size, 72))
        except (ValueError, TypeError):
            font_size = 14

        total  = len(reader.pages)
        writer = PdfWriter()
        overlay_cache: dict = {}

        for idx, page in enumerate(reader.pages):
            box = page.mediabox
            pw  = float(box.width)
            ph  = float(box.height)

            # Guard against degenerate zero-dimension pages
            if pw <= 0 or ph <= 0:
                writer.add_page(page)
                continue

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
