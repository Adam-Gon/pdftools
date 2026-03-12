"""
Base class for all PDF tools.
To create a new tool, subclass PDFTool and implement the `process` method.
Then register it in tools/__init__.py.
"""

from abc import ABC, abstractmethod


class PDFTool(ABC):
    # Unique identifier used in URLs and API calls (e.g. "merge", "split")
    id: str = ""
    # Display name shown in the UI
    name: str = ""
    # Short description shown on the tool card
    description: str = ""
    # Emoji icon displayed on the card
    icon: str = "📄"
    # Whether the tool accepts multiple files
    multiple_files: bool = False
    # Accepted file types (e.g. ".pdf,.jpg")
    accept: str = ".pdf"

    @abstractmethod
    def process(self, files: list, options: dict) -> dict:
        """
        Process the uploaded files with the given options.

        Args:
            files: List of file-like objects (from Flask's request.files)
            options: Dict of additional form parameters

        Returns:
            A dict with either:
              - {"file": <bytes>, "filename": <str>, "mimetype": <str>}
              - {"error": <str>}
        """
        pass

    def to_dict(self) -> dict:
        """Serialize tool metadata for the frontend."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "multiple_files": self.multiple_files,
            "accept": self.accept,
        }
