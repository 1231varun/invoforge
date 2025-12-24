"""Invoice domain entity"""

from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass(frozen=True)
class InvoiceInput:
    """Input data for creating an invoice"""

    invoice_number: int
    invoice_date: date
    validity_year: str
    total_working_days: int
    leaves_taken: int
    leave_dates: List[date]
    rate: float


@dataclass(frozen=True)
class Invoice:
    """Core invoice entity representing a generated invoice"""

    invoice_number: int
    invoice_date: date
    service_period_start: date
    service_period_end: date
    validity_year: str
    total_working_days: int
    leaves_taken: int
    leave_dates: tuple  # Immutable
    days_worked: int
    rate: float
    amount: float
    total_payable: float
    amount_in_words: str

    @property
    def service_period(self) -> str:
        return f"{self.service_period_start.isoformat()} to {self.service_period_end.isoformat()}"


@dataclass
class InvoiceRecord:
    """Stored invoice record with file paths"""

    id: Optional[int]
    invoice_number: int
    invoice_date: date
    service_period_start: date
    service_period_end: date
    days_worked: int
    amount: float
    docx_path: str
    pdf_path: Optional[str]
    created_at: Optional[str]

    def to_dict(self) -> dict:
        from pathlib import Path

        return {
            "id": self.id,
            "invoice_number": self.invoice_number,
            "invoice_date": self.invoice_date.isoformat(),
            "service_period": f"{self.service_period_start.isoformat()} to {self.service_period_end.isoformat()}",
            "days_worked": self.days_worked,
            "amount": self.amount,
            "docx_path": self.docx_path,
            "pdf_path": self.pdf_path,
            "docx_filename": Path(self.docx_path).name if self.docx_path else None,
            "pdf_filename": Path(self.pdf_path).name if self.pdf_path else None,
            "created_at": self.created_at,
        }
