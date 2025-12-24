"""Get Dashboard Use Case"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from app.core.interfaces.invoice_repository import InvoiceRepository
from app.core.interfaces.leave_repository import LeaveRepository
from app.core.interfaces.settings_repository import SettingsRepository
from app.core.services.working_days_calculator import WorkingDaysCalculator


@dataclass
class DashboardStats:
    total_invoices: int
    total_earned: float
    leaves_this_year: int
    last_invoice: Optional[Dict[str, Any]]


@dataclass
class CurrentMonthInfo:
    year: int
    month: int
    month_name: str
    total_weekdays: int
    leaves: int
    working_days: int


@dataclass
class DashboardResponse:
    success: bool
    stats: Optional[DashboardStats] = None
    current_month: Optional[CurrentMonthInfo] = None
    next_invoice_number: int = 1
    currency: str = "EUR"
    error: Optional[str] = None


class GetDashboardUseCase:
    """
    Use case for getting dashboard data.
    
    Aggregates data from multiple sources for the dashboard view.
    """

    def __init__(
        self,
        invoice_repository: InvoiceRepository,
        leave_repository: LeaveRepository,
        settings_repository: SettingsRepository,
        working_days_calculator: WorkingDaysCalculator = None
    ):
        self._invoices = invoice_repository
        self._leaves = leave_repository
        self._settings = settings_repository
        self._working_days = working_days_calculator or WorkingDaysCalculator()

    def execute(self) -> DashboardResponse:
        """Execute the use case"""
        try:
            now = datetime.now()
            current_year = now.year

            # Get all invoices for stats
            all_invoices = self._invoices.get_all()

            # Calculate totals
            total_invoices = len(all_invoices)
            total_earned = sum(inv.amount for inv in all_invoices)

            # Get leaves for current year
            leaves_this_year = self._leaves.get_all(current_year)

            # Get last invoice
            last_invoice = None
            if all_invoices:
                last = all_invoices[0]  # Already sorted by created_at DESC
                last_invoice = {
                    "number": last.invoice_number,
                    "amount": last.amount,
                    "date": last.created_at
                }

            # Calculate current month working days
            current_month_leaves = self._leaves.get_for_month(now.year, now.month)
            working_days_result = self._working_days.calculate(
                now.year,
                now.month,
                current_month_leaves
            )

            # Get settings for currency
            settings = self._settings.get_all()

            return DashboardResponse(
                success=True,
                stats=DashboardStats(
                    total_invoices=total_invoices,
                    total_earned=total_earned,
                    leaves_this_year=len(leaves_this_year),
                    last_invoice=last_invoice
                ),
                current_month=CurrentMonthInfo(
                    year=now.year,
                    month=now.month,
                    month_name=now.strftime("%B %Y"),
                    total_weekdays=working_days_result.total_weekdays,
                    leaves=working_days_result.leaves,
                    working_days=working_days_result.working_days
                ),
                next_invoice_number=self._invoices.get_next_number(),
                currency=settings.currency
            )

        except Exception as e:
            return DashboardResponse(success=False, error=str(e))

