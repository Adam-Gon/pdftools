from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from io import BytesIO
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

        position = options.get("position", "bottom-center")  # top/bottom + left/center/right
        start    = int(options.get("start", 1))
        fmt      = options.get("format", "n")   # "n" = "1", "page_n" = "Página 1", "n_total" = "1 / 10"

        reader = PdfReader(files[0])
        total  = len(reader.pages)
        writer = PdfWriter()

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

            # Build number overlay
            num_buf = BytesIO()
            c = canvas.Canvas(num_buf, pagesize=(pw, ph))
            c.setFont("Helvetica", 10)
            c.setFillColorRGB(0.3, 0.3, 0.3)

            margin = 24
            if "bottom" in position:
                y = margin
            else:
                y = ph - margin - 10

            if "left" in position:
                c.drawString(margin, y, label)
            elif "right" in position:
                c.drawRightString(pw - margin, y, label)
            else:
                c.drawCentredString(pw / 2, y, label)

            c.save()
            num_buf.seek(0)

            num_page = PdfReader(num_buf).pages[0]
            page.merge_page(num_page)
            writer.add_page(page)

        output = BytesIO()
        writer.write(output)
        output.seek(0)
        return {"file": output.read(), "filename": "numerado.pdf", "mimetype": "application/pdf"}
