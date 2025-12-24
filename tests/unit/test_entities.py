"""
Unit tests for domain entities.

Tests cover:
- Leave entity (weekday detection, serialization)
- Invoice entity (immutability, properties)
- Settings entity (serialization, deserialization)
"""

from datetime import date

import pytest

from app.core.entities.invoice import Invoice, InvoiceInput, InvoiceRecord
from app.core.entities.leave import Leave
from app.core.entities.settings import Settings


class TestLeaveEntity:
    """Tests for Leave entity."""

    def test_weekday_leave_is_weekday(self):
        """Monday-Friday leaves are weekdays."""
        monday = Leave(id=1, leave_date=date(2025, 1, 6), reason="Test")  # Monday
        friday = Leave(id=2, leave_date=date(2025, 1, 10), reason="Test")  # Friday

        assert monday.is_weekday is True
        assert friday.is_weekday is True

    def test_weekend_leave_is_not_weekday(self):
        """Saturday-Sunday leaves are not weekdays."""
        saturday = Leave(id=1, leave_date=date(2025, 1, 4), reason="Test")
        sunday = Leave(id=2, leave_date=date(2025, 1, 5), reason="Test")

        assert saturday.is_weekday is False
        assert sunday.is_weekday is False

    def test_to_dict_serialization(self):
        """Leave serializes to dictionary correctly."""
        leave = Leave(id=1, leave_date=date(2025, 1, 6), reason="Personal day")

        result = leave.to_dict()

        assert result == {
            "id": 1,
            "leave_date": "2025-01-06",
            "reason": "Personal day",
        }

    def test_to_calendar_event(self):
        """Leave converts to FullCalendar event format."""
        leave = Leave(id=42, leave_date=date(2025, 3, 15), reason="Vacation")

        result = leave.to_calendar_event()

        assert result["id"] == "42"
        assert result["title"] == "Vacation"
        assert result["start"] == "2025-03-15"
        assert result["allDay"] is True
        assert "backgroundColor" in result

    def test_empty_reason_shows_leave_title(self):
        """Empty reason defaults to 'Leave' in calendar."""
        leave = Leave(id=1, leave_date=date(2025, 1, 6), reason="")

        result = leave.to_calendar_event()

        assert result["title"] == "Leave"

    def test_default_reason_is_empty(self):
        """Reason defaults to empty string."""
        leave = Leave(id=1, leave_date=date(2025, 1, 6))

        assert leave.reason == ""


class TestInvoiceInputEntity:
    """Tests for InvoiceInput entity."""

    def test_is_immutable(self):
        """InvoiceInput is frozen dataclass."""
        invoice_input = InvoiceInput(
            invoice_number=1,
            invoice_date=date(2025, 1, 15),
            validity_year="2025-26",
            total_working_days=23,
            leaves_taken=2,
            leave_dates=[date(2025, 1, 6)],
            rate=100.00,
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            invoice_input.invoice_number = 2


class TestInvoiceEntity:
    """Tests for Invoice entity."""

    def test_is_immutable(self):
        """Invoice is frozen dataclass."""
        invoice = Invoice(
            invoice_number=1,
            invoice_date=date(2025, 1, 15),
            service_period_start=date(2025, 1, 1),
            service_period_end=date(2025, 1, 31),
            validity_year="2025-26",
            total_working_days=23,
            leaves_taken=2,
            leave_dates=(),
            days_worked=21,
            rate=100.00,
            amount=2100.00,
            total_payable=2100.00,
            amount_in_words="Two Thousand One Hundred Euros",
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            invoice.amount = 5000.00

    def test_service_period_property(self):
        """Service period property returns formatted string."""
        invoice = Invoice(
            invoice_number=1,
            invoice_date=date(2025, 1, 15),
            service_period_start=date(2025, 1, 1),
            service_period_end=date(2025, 1, 31),
            validity_year="2025-26",
            total_working_days=23,
            leaves_taken=0,
            leave_dates=(),
            days_worked=23,
            rate=100.00,
            amount=2300.00,
            total_payable=2300.00,
            amount_in_words="Test",
        )

        assert invoice.service_period == "2025-01-01 to 2025-01-31"


class TestInvoiceRecordEntity:
    """Tests for InvoiceRecord entity."""

    def test_to_dict_serialization(self):
        """InvoiceRecord serializes correctly."""
        record = InvoiceRecord(
            id=1,
            invoice_number=5,
            invoice_date=date(2025, 1, 15),
            service_period_start=date(2025, 1, 1),
            service_period_end=date(2025, 1, 31),
            days_worked=21,
            amount=2100.00,
            docx_path="/path/to/invoice.docx",
            pdf_path="/path/to/invoice.pdf",
            created_at="2025-01-15T10:00:00",
        )

        result = record.to_dict()

        assert result["id"] == 1
        assert result["invoice_number"] == 5
        assert result["invoice_date"] == "2025-01-15"
        assert result["service_period"] == "2025-01-01 to 2025-01-31"
        assert result["docx_filename"] == "invoice.docx"
        assert result["pdf_filename"] == "invoice.pdf"

    def test_handles_none_pdf_path(self):
        """Handles None PDF path gracefully."""
        record = InvoiceRecord(
            id=1,
            invoice_number=1,
            invoice_date=date(2025, 1, 15),
            service_period_start=date(2025, 1, 1),
            service_period_end=date(2025, 1, 31),
            days_worked=21,
            amount=2100.00,
            docx_path="/path/to/invoice.docx",
            pdf_path=None,
            created_at=None,
        )

        result = record.to_dict()

        assert result["pdf_path"] is None
        assert result["pdf_filename"] is None


class TestSettingsEntity:
    """Tests for Settings entity."""

    def test_default_values(self):
        """Settings has sensible defaults."""
        settings = Settings()

        assert settings.daily_rate == 0.0
        assert settings.currency == "EUR"
        assert settings.setup_complete is False

    def test_to_dict_serialization(self, sample_settings: Settings):
        """Settings serializes to dictionary."""
        result = sample_settings.to_dict()

        assert result["daily_rate"] == 100.00
        assert result["currency"] == "EUR"
        assert result["supplier_name"] == "ACME Test Corp"
        assert result["setup_complete"] is True

    def test_from_dict_deserialization(self):
        """Settings deserializes from dictionary."""
        data = {
            "daily_rate": "150.50",  # String should be converted
            "currency": "USD",
            "supplier_name": "Test Corp",
            "setup_complete": "true",  # String boolean
        }

        settings = Settings.from_dict(data)

        assert settings.daily_rate == 150.50
        assert settings.currency == "USD"
        assert settings.supplier_name == "Test Corp"
        assert settings.setup_complete is True

    def test_from_dict_handles_missing_keys(self):
        """from_dict handles missing keys with defaults."""
        data = {"supplier_name": "Minimal Corp"}

        settings = Settings.from_dict(data)

        assert settings.supplier_name == "Minimal Corp"
        assert settings.daily_rate == 0.0
        assert settings.currency == "EUR"

    def test_from_dict_handles_false_string(self):
        """String 'false' is correctly converted to boolean."""
        data = {"setup_complete": "false"}

        settings = Settings.from_dict(data)

        assert settings.setup_complete is False

