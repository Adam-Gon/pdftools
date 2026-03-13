from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from io import BytesIO
import gc
from .base import PDFTool


class WatermarkTool(PDFTool):
    id = "watermark"
    name = "Marca d'Água"
    description = "Adicione um texto como marca d'água em todas as páginas"
    icon = "💧"
    multiple_files = False
    accept = ".pdf"

    def _build_watermark(self, pw, ph, text, opacity, position) -> bytes:
        """Build a watermark PDF page in memory — reused across all pages."""
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=(pw, ph))
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
        return buf.getvalue()

    def process(self, files: list, options: dict) -> dict:
        if not files:
            return {"error": "Envie um arquivo PDF."}

        text     = options.get("text", "CONFIDENCIAL").strip() or "CONFIDENCIAL"
        opacity  = float(options.get("opacity", 0.20))
        position = options.get("position", "diagonal")

        reader = PdfReader(files[0])
        writer = PdfWriter()

        # Cache watermarks by page size — avoids rebuilding for same-size pages
        wm_cache: dict = {}

        for page in reader.pages:
            box = page.mediabox
            pw  = float(box.width)
            ph  = float(box.height)
            key = (round(pw), round(ph))

            if key not in wm_cache:
                wm_cache[key] = self._build_watermark(pw, ph, text, opacity, position)

            wm_page = PdfReader(BytesIO(wm_cache[key])).pages[0]
            page.merge_page(wm_page)
            writer.add_page(page)

        output = BytesIO()
        writer.write(output)
        output.seek(0)
        gc.collect()
        return {"file": output.read(), "filename": "com_marca_dagua.pdf", "mimetype": "application/pdf"}
