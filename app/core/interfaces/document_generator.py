"""Document generator interface (port)"""

from abc import ABC, abstractmethod
from pathlib import Path

from app.core.entities.invoice import Invoice
from app.core.entities.settings import Settings


class DocumentGenerator(ABC):
    """Interface for generating invoice documents"""

    @abstractmethod
    def generate(self, invoice: Invoice, settings: Settings) -> Path:
        """Generate a document from an invoice and return the file path"""
        pass
