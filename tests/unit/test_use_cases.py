"""
Unit tests for application use cases.

Tests cover:
- GetWorkingDaysUseCase
- PreviewInvoiceUseCase
- Use case orchestration logic
- Error handling
"""

from datetime import date
from unittest.mock import Mock

from app.application.use_cases.get_working_days import GetWorkingDaysUseCase
from app.application.use_cases.preview_invoice import (
    PreviewInvoiceRequest,
    PreviewInvoiceUseCase,
)
from app.core.entities.leave import Leave
from app.core.entities.settings import Settings
from app.core.services.invoice_calculator import InvoiceCalculator
from app.core.services.working_days_calculator import WorkingDaysCalculator


class TestGetWorkingDaysUseCase:
    """Tests for GetWorkingDaysUseCase."""

    def test_returns_working_days_for_month(self):
        """Use case returns correct working days calculation."""
        # Arrange
        mock_leave_repo = Mock()
        mock_leave_repo.get_for_month.return_value = []

        calculator = WorkingDaysCalculator()
        use_case = GetWorkingDaysUseCase(
            leave_repository=mock_leave_repo,
            working_days_calculator=calculator,
        )

        # Act
        result = use_case.execute(year=2025, month=1)

        # Assert
        assert result.success is True
        assert result.total_weekdays == 23
        assert result.leaves == 0
        assert result.working_days == 23

    def test_subtracts_weekday_leaves(self):
        """Weekday leaves are subtracted from working days."""
        # Arrange
        mock_leave_repo = Mock()
        mock_leave_repo.get_for_month.return_value = [
            Leave(id=1, leave_date=date(2025, 1, 6), reason="Test"),  # Monday
            Leave(id=2, leave_date=date(2025, 1, 7), reason="Test"),  # Tuesday
        ]

        calculator = WorkingDaysCalculator()
        use_case = GetWorkingDaysUseCase(
            leave_repository=mock_leave_repo,
            working_days_calculator=calculator,
        )

        # Act
        result = use_case.execute(year=2025, month=1)

        # Assert
        assert result.success is True
        assert result.leaves == 2
        assert result.working_days == 21  # 23 - 2

    def test_ignores_weekend_leaves(self):
        """Weekend leaves don't affect working days count."""
        # Arrange
        mock_leave_repo = Mock()
        mock_leave_repo.get_for_month.return_value = [
            Leave(id=1, leave_date=date(2025, 1, 4), reason="Saturday"),
        ]

        calculator = WorkingDaysCalculator()
        use_case = GetWorkingDaysUseCase(
            leave_repository=mock_leave_repo,
            working_days_calculator=calculator,
        )

        # Act
        result = use_case.execute(year=2025, month=1)

        # Assert
        assert result.leaves == 0  # Weekend not counted
        assert result.working_days == 23

    def test_handles_repository_error(self):
        """Returns error response when repository fails."""
        # Arrange
        mock_leave_repo = Mock()
        mock_leave_repo.get_for_month.side_effect = Exception("Database error")

        use_case = GetWorkingDaysUseCase(
            leave_repository=mock_leave_repo,
            working_days_calculator=WorkingDaysCalculator(),
        )

        # Act
        result = use_case.execute(year=2025, month=1)

        # Assert
        assert result.success is False
        assert "Database error" in result.error

    def test_returns_leave_dates_in_response(self):
        """Leave dates are included in response."""
        # Arrange
        mock_leave_repo = Mock()
        mock_leave_repo.get_for_month.return_value = [
            Leave(id=1, leave_date=date(2025, 1, 6), reason="Test"),
        ]

        use_case = GetWorkingDaysUseCase(
            leave_repository=mock_leave_repo,
            working_days_calculator=WorkingDaysCalculator(),
        )

        # Act
        result = use_case.execute(year=2025, month=1)

        # Assert
        assert "2025-01-06" in result.leave_dates


class TestPreviewInvoiceUseCase:
    """Tests for PreviewInvoiceUseCase."""

    def _create_mock_settings_repo(self, settings: Settings = None) -> Mock:
        """Helper to create mock settings repository."""
        mock_repo = Mock()
        mock_repo.get_all.return_value = settings or Settings(
            daily_rate=100.00,
            currency="EUR",
        )
        return mock_repo

    def test_returns_invoice_preview(self):
        """Use case returns correct invoice preview."""
        # Arrange
        mock_settings = self._create_mock_settings_repo()
        use_case = PreviewInvoiceUseCase(
            settings_repository=mock_settings,
            invoice_calculator=InvoiceCalculator(),
        )

        request = PreviewInvoiceRequest(
            invoice_number=1,
            invoice_date=date(2025, 1, 15),
            validity_year="2025-26",
            total_working_days=23,
            leaves_taken=2,
            leave_dates=[date(2025, 1, 6), date(2025, 1, 7)],
            rate=100.00,
        )

        # Act
        result = use_case.execute(request)

        # Assert
        assert result.success is True
        assert result.days_worked == 21
        assert result.amount == "2100.00"
        assert "2025-01-01 to 2025-01-31" in result.service_period

    def test_uses_provided_rate_over_settings(self):
        """Rate from request takes precedence over settings."""
        # Arrange
        mock_settings = self._create_mock_settings_repo(Settings(daily_rate=50.00, currency="EUR"))
        use_case = PreviewInvoiceUseCase(
            settings_repository=mock_settings,
            invoice_calculator=InvoiceCalculator(),
        )

        request = PreviewInvoiceRequest(
            invoice_number=1,
            invoice_date=date(2025, 1, 15),
            validity_year="2025-26",
            total_working_days=20,
            leaves_taken=0,
            leave_dates=[],
            rate=100.00,  # Override settings rate
        )

        # Act
        result = use_case.execute(request)

        # Assert
        assert result.amount == "2000.00"  # 20 * 100, not 20 * 50

    def test_falls_back_to_settings_rate(self):
        """Uses settings rate when request rate is None."""
        # Arrange
        mock_settings = self._create_mock_settings_repo(Settings(daily_rate=75.00, currency="EUR"))
        use_case = PreviewInvoiceUseCase(
            settings_repository=mock_settings,
            invoice_calculator=InvoiceCalculator(),
        )

        request = PreviewInvoiceRequest(
            invoice_number=1,
            invoice_date=date(2025, 1, 15),
            validity_year="2025-26",
            total_working_days=20,
            leaves_taken=0,
            leave_dates=[],
            rate=None,  # No rate provided
        )

        # Act
        result = use_case.execute(request)

        # Assert
        assert result.amount == "1500.00"  # 20 * 75

    def test_uses_settings_currency(self):
        """Currency from settings is used in formatting."""
        # Arrange
        mock_settings = self._create_mock_settings_repo(Settings(daily_rate=100.00, currency="USD"))
        use_case = PreviewInvoiceUseCase(
            settings_repository=mock_settings,
            invoice_calculator=InvoiceCalculator(),
        )

        request = PreviewInvoiceRequest(
            invoice_number=1,
            invoice_date=date(2025, 1, 15),
            validity_year="2025-26",
            total_working_days=10,
            leaves_taken=0,
            leave_dates=[],
            rate=100.00,
        )

        # Act
        result = use_case.execute(request)

        # Assert
        assert "Dollars" in result.amount_in_words

    def test_handles_settings_repository_error(self):
        """Returns error response when settings repository fails."""
        # Arrange
        mock_settings = Mock()
        mock_settings.get_all.side_effect = Exception("Settings not found")

        use_case = PreviewInvoiceUseCase(
            settings_repository=mock_settings,
            invoice_calculator=InvoiceCalculator(),
        )

        request = PreviewInvoiceRequest(
            invoice_number=1,
            invoice_date=date(2025, 1, 15),
            validity_year="2025-26",
            total_working_days=20,
            leaves_taken=0,
            leave_dates=[],
            rate=100.00,
        )

        # Act
        result = use_case.execute(request)

        # Assert
        assert result.success is False
        assert "Settings not found" in result.error

    def test_amount_in_words_included(self):
        """Amount in words is included in response."""
        # Arrange
        mock_settings = self._create_mock_settings_repo()
        use_case = PreviewInvoiceUseCase(
            settings_repository=mock_settings,
            invoice_calculator=InvoiceCalculator(),
        )

        request = PreviewInvoiceRequest(
            invoice_number=1,
            invoice_date=date(2025, 1, 15),
            validity_year="2025-26",
            total_working_days=21,
            leaves_taken=0,
            leave_dates=[],
            rate=100.00,
        )

        # Act
        result = use_case.execute(request)

        # Assert
        assert result.amount_in_words is not None
        assert "Euros" in result.amount_in_words
