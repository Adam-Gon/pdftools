from .merge          import MergeTool
from .split          import SplitTool
from .rotate         import RotateTool
from .extract_text   import ExtractTextTool
from .images_to_pdf  import ImagesToPdfTool
from .remove_pages   import RemovePagesTool
from .extract_pages  import ExtractPagesTool
from .organize_pages import OrganizePagesTool
from .protect        import ProtectTool
from .unlock         import UnlockTool
from .watermark      import WatermarkTool
from .page_numbers   import PageNumbersTool
from .compress       import CompressTool
from .pdf_to_jpg     import PdfToJpgTool

TOOLS: list = [
    MergeTool(),
    SplitTool(),
    RemovePagesTool(),
    ExtractPagesTool(),
    OrganizePagesTool(),
    ImagesToPdfTool(),
    PdfToJpgTool(),
    RotateTool(),
    WatermarkTool(),
    PageNumbersTool(),
    CompressTool(),
    ProtectTool(),
    UnlockTool(),
    ExtractTextTool(),
]

TOOLS_BY_ID: dict = {tool.id: tool for tool in TOOLS}
