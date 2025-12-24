"""Get Working Days Use Case"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from app.core.interfaces.leave_repository import LeaveRepository
from app.core.services.working_days_calculator import WorkingDaysCalculator


@dataclass
class WorkingDaysResponse:
    success: bool
    total_weekdays: int = 0
    leaves: int = 0
    working_days: int = 0
    leave_dates: List[str] = None
    error: Optional[str] = None


class GetWorkingDaysUseCase:
    """
    Use case for calculating working days for a given month.
    """

    def __init__(
        self,
        leave_repository: LeaveRepository,
        working_days_calculator: WorkingDaysCalculator = None,
    ):
        self._leaves = leave_repository
        self._calculator = working_days_calculator or WorkingDaysCalculator()

    def execute(
        self, year: Optional[int] = None, month: Optional[int] = None
    ) -> WorkingDaysResponse:
        """Execute the use case"""
        try:
            # Default to current month
            if not year or not month:
                now = datetime.now()
                year = now.year
                month = now.month

            # Get leaves for the month
            leaves = self._leaves.get_for_month(year, month)

            # Calculate working days
            result = self._calculator.calculate(year, month, leaves)

            return WorkingDaysResponse(
                success=True,
                total_weekdays=result.total_weekdays,
                leaves=result.leaves,
                working_days=result.working_days,
                leave_dates=result.leave_dates,
            )

        except Exception as e:
            return WorkingDaysResponse(success=False, error=str(e))
