"""
Pytest configuration and shared fixtures.

Fixtures are reusable test dependencies injected by pytest.
"""

from datetime import date

import pytest

from app import create_app
from app.core.entities.invoice import InvoiceInput
from app.core.entities.leave import Leave
from app.core.entities.settings import Settings
from app.core.services.amount_formatter import AmountFormatter
from app.core.services.invoice_calculator import InvoiceCalculator
from app.core.services.working_days_calculator import WorkingDaysCalculator

# ============================================
# Flask App Fixtures
# ============================================


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def app_client(app):
    """Flask test client for making requests."""
    return app.test_client()


# ============================================
# Core Service Fixtures
# ============================================


@pytest.fixture
def working_days_calculator() -> WorkingDaysCalculator:
    """Fresh working days calculator instance."""
    return WorkingDaysCalculator()


@pytest.fixture
def amount_formatter() -> AmountFormatter:
    """Fresh amount formatter instance."""
    return AmountFormatter()


@pytest.fixture
def invoice_calculator(
    working_days_calculator: WorkingDaysCalculator,
    amount_formatter: AmountFormatter,
) -> InvoiceCalculator:
    """Invoice calculator with injected dependencies."""
    return InvoiceCalculator(
        working_days_calculator=working_days_calculator,
        amount_formatter=amount_formatter,
    )


# ============================================
# Entity Fixtures
# ============================================


@pytest.fixture
def sample_leave() -> Leave:
    """A sample leave on a weekday (Monday)."""
    return Leave(id=1, leave_date=date(2025, 1, 6), reason="Personal day")


@pytest.fixture
def sample_weekend_leave() -> Leave:
    """A sample leave on a weekend (Saturday)."""
    return Leave(id=2, leave_date=date(2025, 1, 4), reason="Weekend")


@pytest.fixture
def sample_settings() -> Settings:
    """Sample settings for testing - all fake/placeholder data."""
    return Settings(
        daily_rate=100.00,
        currency="EUR",
        supplier_name="ACME Test Corp",
        supplier_address="123 Fake Street, Test City, 000000",
        gstin="00AAAAA0000A0A0",
        pan="AAAAA0000A",
        supplier_email="test@example.test",
        client_name="Fake Client Inc",
        client_address="456 Mock Avenue, Sample Town",
        client_country="Testland",
        client_email="client@example.test",
        place_of_supply="Testland",
        lut_no="XX0000000000000",
        lut_validity="2025-26",
        bank_name="Fake Bank Ltd",
        account_no="0000000000",
        account_holder="ACME Test Corp",
        swift_code="FAKESWIFT",
        signatory_name="John Doe",
        setup_complete=True,
    )


@pytest.fixture
def sample_invoice_input() -> InvoiceInput:
    """Sample invoice input for testing - uses round numbers for easy verification."""
    return InvoiceInput(
        invoice_number=1,
        invoice_date=date(2025, 1, 15),
        validity_year="2025-26",
        total_working_days=23,
        leaves_taken=2,
        leave_dates=[date(2025, 1, 6), date(2025, 1, 7)],
        rate=100.00,  # Round number for easy calculation verification
    )


@pytest.fixture
def january_2025_leaves() -> list[Leave]:
    """List of leaves in January 2025 for testing."""
    return [
        Leave(id=1, leave_date=date(2025, 1, 6), reason="Personal"),  # Monday
        Leave(id=2, leave_date=date(2025, 1, 7), reason="Sick"),  # Tuesday
        Leave(id=3, leave_date=date(2025, 1, 4), reason="Weekend"),  # Saturday (shouldn't count)
    ]
