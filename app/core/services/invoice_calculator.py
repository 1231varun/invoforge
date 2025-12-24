"""Invoice calculation service"""

from app.core.entities.invoice import Invoice, InvoiceInput
from app.core.services.amount_formatter import AmountFormatter
from app.core.services.working_days_calculator import WorkingDaysCalculator


class InvoiceCalculator:
    """
    Core business logic for invoice calculations.
    
    Responsible for:
    - Calculating service period from invoice date
    - Computing days worked
    - Calculating amounts
    - Formatting amounts to words
    """

    def __init__(
        self,
        working_days_calculator: WorkingDaysCalculator = None,
        amount_formatter: AmountFormatter = None
    ):
        self._working_days = working_days_calculator or WorkingDaysCalculator()
        self._formatter = amount_formatter or AmountFormatter()

    def calculate_amount(self, days: int, rate: float) -> float:
        """Calculate total amount from days worked and rate"""
        return round(days * rate, 2)

    def create_invoice(self, input_data: InvoiceInput, currency: str = "EUR") -> Invoice:
        """
        Create an Invoice entity from input data.
        
        Performs all calculations and returns an immutable Invoice.
        """
        # Calculate service period
        period_start, period_end = self._working_days.get_service_period(input_data.invoice_date)

        # Calculate days worked
        days_worked = input_data.total_working_days - input_data.leaves_taken

        # Calculate amount
        amount = self.calculate_amount(days_worked, input_data.rate)

        # Format amount in words
        amount_words = self._formatter.to_words(amount, currency)

        return Invoice(
            invoice_number=input_data.invoice_number,
            invoice_date=input_data.invoice_date,
            service_period_start=period_start,
            service_period_end=period_end,
            validity_year=input_data.validity_year,
            total_working_days=input_data.total_working_days,
            leaves_taken=input_data.leaves_taken,
            leave_dates=tuple(sorted(input_data.leave_dates)),
            days_worked=days_worked,
            rate=input_data.rate,
            amount=amount,
            total_payable=amount,
            amount_in_words=amount_words
        )

