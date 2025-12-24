"""Invoice repository interface (port)"""
from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from app.core.entities.invoice import InvoiceRecord


class InvoiceRepository(ABC):
    """Interface for invoice persistence operations"""

    @abstractmethod
    def save(
        self,
        invoice_number: int,
        invoice_date: date,
        service_period_start: date,
        service_period_end: date,
        days_worked: int,
        amount: float,
        docx_path: str,
        pdf_path: Optional[str] = None
    ) -> InvoiceRecord:
        """Save a new invoice record"""
        pass

    @abstractmethod
    def get_all(self) -> List[InvoiceRecord]:
        """Get all invoice records ordered by creation date"""
        pass

    @abstractmethod
    def get_by_id(self, invoice_id: int) -> Optional[InvoiceRecord]:
        """Get a specific invoice by ID"""
        pass

    @abstractmethod
    def delete(self, invoice_id: int) -> bool:
        """Delete an invoice record"""
        pass

    @abstractmethod
    def get_next_number(self) -> int:
        """Get the next available invoice number"""
        pass

    @abstractmethod
    def get_last_number(self) -> int:
        """Get the last used invoice number"""
        pass

