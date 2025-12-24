"""Preview Invoice Use Case"""

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from app.core.entities.invoice import InvoiceInput
from app.core.interfaces.settings_repository import SettingsRepository
from app.core.services.invoice_calculator import InvoiceCalculator


@dataclass
class PreviewInvoiceRequest:
    """Input data for previewing an invoice"""

    invoice_number: int
    invoice_date: date
    validity_year: str
    total_working_days: int
    leaves_taken: int
    leave_dates: List[date]
    rate: Optional[float] = None


@dataclass
class PreviewInvoiceResponse:
    """Result of invoice preview"""

    success: bool
    service_period: Optional[str] = None
    days_worked: Optional[int] = None
    amount: Optional[str] = None
    total_payable: Optional[str] = None
    amount_in_words: Optional[str] = None
    error: Optional[str] = None


class PreviewInvoiceUseCase:
    """
    Use case for previewing invoice calculations without generating documents.
    """

    def __init__(
        self, settings_repository: SettingsRepository, invoice_calculator: InvoiceCalculator = None
    ):
        self._settings = settings_repository
        self._calculator = invoice_calculator or InvoiceCalculator()

    def execute(self, request: PreviewInvoiceRequest) -> PreviewInvoiceResponse:
        """Execute the use case"""
        try:
            settings = self._settings.get_all()
            rate = request.rate if request.rate is not None else settings.daily_rate

            input_data = InvoiceInput(
                invoice_number=request.invoice_number,
                invoice_date=request.invoice_date,
                validity_year=request.validity_year,
                total_working_days=request.total_working_days,
                leaves_taken=request.leaves_taken,
                leave_dates=request.leave_dates,
                rate=rate,
            )

            invoice = self._calculator.create_invoice(input_data, settings.currency)

            return PreviewInvoiceResponse(
                success=True,
                service_period=invoice.service_period,
                days_worked=invoice.days_worked,
                amount=f"{invoice.amount:.2f}",
                total_payable=f"{invoice.total_payable:.2f}",
                amount_in_words=invoice.amount_in_words,
            )

        except Exception as e:
            return PreviewInvoiceResponse(success=False, error=str(e))
