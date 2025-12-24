"""
Unit tests for InvoiceCalculator service.

Tests cover:
- Amount calculation
- Invoice creation from input
- Service period derivation
- Days worked calculation
- Edge cases
"""

from datetime import date

from app.core.entities.invoice import InvoiceInput
from app.core.services.invoice_calculator import InvoiceCalculator


class TestCalculateAmount:
    """Tests for calculate_amount method."""

    def test_simple_calculation(self, invoice_calculator: InvoiceCalculator):
        """Basic days * rate calculation."""
        result = invoice_calculator.calculate_amount(days=20, rate=100.00)
        assert result == 2000.00

    def test_with_decimal_rate(self, invoice_calculator: InvoiceCalculator):
        """Calculation with decimal rate."""
        result = invoice_calculator.calculate_amount(days=21, rate=100.50)
        assert result == 2110.50

    def test_rounds_to_two_decimals(self, invoice_calculator: InvoiceCalculator):
        """Result is rounded to 2 decimal places."""
        # 21 * 100.333 = 2106.993 -> should round to 2106.99
        result = invoice_calculator.calculate_amount(days=21, rate=100.333)
        assert result == 2106.99

    def test_zero_days(self, invoice_calculator: InvoiceCalculator):
        """Zero days returns zero amount."""
        result = invoice_calculator.calculate_amount(days=0, rate=100.00)
        assert result == 0.00

    def test_zero_rate(self, invoice_calculator: InvoiceCalculator):
        """Zero rate returns zero amount."""
        result = invoice_calculator.calculate_amount(days=20, rate=0.00)
        assert result == 0.00


class TestCreateInvoice:
    """Tests for create_invoice method."""

    def test_creates_invoice_with_correct_values(
        self,
        invoice_calculator: InvoiceCalculator,
        sample_invoice_input: InvoiceInput,
    ):
        """Invoice is created with all calculated values."""
        invoice = invoice_calculator.create_invoice(sample_invoice_input, "EUR")

        assert invoice.invoice_number == 1
        assert invoice.invoice_date == date(2025, 1, 15)
        assert invoice.validity_year == "2025-26"

    def test_calculates_days_worked(
        self,
        invoice_calculator: InvoiceCalculator,
        sample_invoice_input: InvoiceInput,
    ):
        """Days worked = total working days - leaves taken."""
        invoice = invoice_calculator.create_invoice(sample_invoice_input, "EUR")

        # 23 total - 2 leaves = 21 days worked
        assert invoice.days_worked == 21

    def test_calculates_amount(
        self,
        invoice_calculator: InvoiceCalculator,
        sample_invoice_input: InvoiceInput,
    ):
        """Amount = days worked * rate."""
        invoice = invoice_calculator.create_invoice(sample_invoice_input, "EUR")

        # 21 days * 100.00 rate = 2100.00
        assert invoice.amount == 2100.00
        assert invoice.total_payable == 2100.00

    def test_derives_service_period(
        self,
        invoice_calculator: InvoiceCalculator,
        sample_invoice_input: InvoiceInput,
    ):
        """Service period is first to last day of invoice month."""
        invoice = invoice_calculator.create_invoice(sample_invoice_input, "EUR")

        assert invoice.service_period_start == date(2025, 1, 1)
        assert invoice.service_period_end == date(2025, 1, 31)

    def test_formats_amount_in_words(
        self,
        invoice_calculator: InvoiceCalculator,
        sample_invoice_input: InvoiceInput,
    ):
        """Amount is converted to words."""
        invoice = invoice_calculator.create_invoice(sample_invoice_input, "EUR")

        assert "Euros" in invoice.amount_in_words
        assert "Thousand" in invoice.amount_in_words or "Two Thousand" in invoice.amount_in_words

    def test_leave_dates_are_sorted_tuple(
        self,
        invoice_calculator: InvoiceCalculator,
    ):
        """Leave dates are stored as sorted immutable tuple."""
        unsorted_input = InvoiceInput(
            invoice_number=1,
            invoice_date=date(2025, 1, 15),
            validity_year="2025-26",
            total_working_days=23,
            leaves_taken=2,
            leave_dates=[date(2025, 1, 7), date(2025, 1, 6)],  # Unsorted
            rate=100.00,
        )

        invoice = invoice_calculator.create_invoice(unsorted_input, "EUR")

        assert isinstance(invoice.leave_dates, tuple)
        assert invoice.leave_dates == (date(2025, 1, 6), date(2025, 1, 7))  # Sorted

    def test_uses_provided_currency(self, invoice_calculator: InvoiceCalculator):
        """Currency is used in amount formatting."""
        input_data = InvoiceInput(
            invoice_number=1,
            invoice_date=date(2025, 1, 15),
            validity_year="2025-26",
            total_working_days=20,
            leaves_taken=0,
            leave_dates=[],
            rate=100.00,
        )

        invoice = invoice_calculator.create_invoice(input_data, "USD")

        assert "Dollars" in invoice.amount_in_words


class TestEdgeCases:
    """Edge case tests for InvoiceCalculator."""

    def test_all_days_are_leaves(self, invoice_calculator: InvoiceCalculator):
        """When all days are leaves, amount is zero."""
        input_data = InvoiceInput(
            invoice_number=1,
            invoice_date=date(2025, 1, 15),
            validity_year="2025-26",
            total_working_days=23,
            leaves_taken=23,
            leave_dates=[],
            rate=100.00,
        )

        invoice = invoice_calculator.create_invoice(input_data, "EUR")

        assert invoice.days_worked == 0
        assert invoice.amount == 0.00

    def test_no_leaves(self, invoice_calculator: InvoiceCalculator):
        """No leaves means full working days."""
        input_data = InvoiceInput(
            invoice_number=1,
            invoice_date=date(2025, 1, 15),
            validity_year="2025-26",
            total_working_days=23,
            leaves_taken=0,
            leave_dates=[],
            rate=100.00,
        )

        invoice = invoice_calculator.create_invoice(input_data, "EUR")

        assert invoice.days_worked == 23
        assert invoice.amount == 2300.00

    def test_february_leap_year_service_period(self, invoice_calculator: InvoiceCalculator):
        """February in leap year has correct service period."""
        input_data = InvoiceInput(
            invoice_number=1,
            invoice_date=date(2024, 2, 15),  # Leap year
            validity_year="2024-25",
            total_working_days=21,
            leaves_taken=0,
            leave_dates=[],
            rate=100.00,
        )

        invoice = invoice_calculator.create_invoice(input_data, "EUR")

        assert invoice.service_period_end == date(2024, 2, 29)
