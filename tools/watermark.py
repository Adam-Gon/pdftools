from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from io import BytesIO
import math
from .base import PDFTool


class WatermarkTool(PDFTool):
    id = "watermark"
    name = "Marca d'Água"
    description = "Adicione um texto como marca d'água em todas as páginas"
    icon = "💧"
    multiple_files = False
    accept = ".pdf"

    def process(self, files: list, options: dict) -> dict:
        if not files:
            return {"error": "Envie um arquivo PDF."}

        text     = options.get("text", "CONFIDENCIAL").strip() or "CONFIDENCIAL"
        opacity  = float(options.get("opacity", 0.15))
        position = options.get("position", "diagonal")  # "diagonal" or "center"

        reader = PdfReader(files[0])
        writer = PdfWriter()

        for page in reader.pages:
            # Get page dimensions
            box   = page.mediabox
            pw    = float(box.width)
            ph    = float(box.height)

            # Build watermark PDF in memory
            wm_buf = BytesIO()
            c = canvas.Canvas(wm_buf, pagesize=(pw, ph))
            c.setFillColor(HexColor("#000000"), alpha=opacity)
            c.setFont("Helvetica-Bold", min(pw, ph) * 0.08)

            if position == "diagonal":
                c.saveState()
                c.translate(pw / 2, ph / 2)
                c.rotate(45)
                c.drawCentredString(0, 0, text)
                c.restoreState()
            else:
                c.drawCentredString(pw / 2, ph / 2, text)

            c.save()
            wm_buf.seek(0)

            wm_page = PdfReader(wm_buf).pages[0]
            page.merge_page(wm_page)
            writer.add_page(page)

        output = BytesIO()
        writer.write(output)
        output.seek(0)
        return {"file": output.read(), "filename": "com_marca_dagua.pdf", "mimetype": "application/pdf"}
