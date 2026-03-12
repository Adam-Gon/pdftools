"""
Tool registry — add new tools here!

To add a new tool:
1. Create a new file in tools/ (e.g. tools/watermark.py)
2. Subclass PDFTool and implement `process()`
3. Import and add it to the TOOLS list below
"""

from .merge import MergeTool
from .split import SplitTool
from .rotate import RotateTool
from .extract_text import ExtractTextTool
from .images_to_pdf import ImagesToPdfTool

# ============================================================
# REGISTRY — list all available tools here
# ============================================================
TOOLS: list = [
    MergeTool(),
    SplitTool(),
    RotateTool(),
    ExtractTextTool(),
    ImagesToPdfTool(),
]

# Build a lookup dict by tool id for fast access
TOOLS_BY_ID: dict = {tool.id: tool for tool in TOOLS}
