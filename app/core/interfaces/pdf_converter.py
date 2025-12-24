"""PDF converter interface (port)"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class PDFConverter(ABC):
    """Interface for converting documents to PDF"""

    @abstractmethod
    def convert(self, source_path: Path) -> Optional[Path]:
        """
        Convert a document to PDF.

        Returns the PDF path on success, None on failure.
        """
        pass
