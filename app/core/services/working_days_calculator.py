"""Working days calculation service"""

from calendar import monthrange
from dataclasses import dataclass
from datetime import date
from typing import List

from app.core.entities.leave import Leave


@dataclass
class WorkingDaysResult:
    """Result of working days calculation"""

    total_weekdays: int
    leaves: int
    working_days: int
    leave_dates: List[str]


class WorkingDaysCalculator:
    """
    Calculates working days for freelance billing.

    Working days = Weekdays (Mon-Fri) in month - Leaves on weekdays
    """

    def calculate_weekdays(self, year: int, month: int) -> int:
        """Calculate total weekdays (Mon-Fri) in a given month"""
        _, num_days = monthrange(year, month)
        weekdays = 0

        for day in range(1, num_days + 1):
            d = date(year, month, day)
            if d.weekday() < 5:  # Monday = 0, Friday = 4
                weekdays += 1

        return weekdays

    def calculate(self, year: int, month: int, leaves: List[Leave]) -> WorkingDaysResult:
        """
        Calculate working days for a month minus leaves.

        Only counts leaves that fall on weekdays.
        """
        total_weekdays = self.calculate_weekdays(year, month)

        # Only count leaves that fall on weekdays
        weekday_leaves = [l for l in leaves if l.is_weekday]

        return WorkingDaysResult(
            total_weekdays=total_weekdays,
            leaves=len(weekday_leaves),
            working_days=total_weekdays - len(weekday_leaves),
            leave_dates=[l.leave_date.isoformat() for l in leaves],
        )

    def get_service_period(self, reference_date: date) -> tuple[date, date]:
        """Get the service period (first and last day of month) for a given date"""
        first_day = date(reference_date.year, reference_date.month, 1)
        last_day_num = monthrange(reference_date.year, reference_date.month)[1]
        last_day = date(reference_date.year, reference_date.month, last_day_num)
        return first_day, last_day

    def calculate_weekdays_for_range(self, start_date: date, end_date: date) -> int:
        """Calculate total weekdays (Mon-Fri) in a date range"""
        from datetime import timedelta

        weekdays = 0
        current = start_date

        while current <= end_date:
            if current.weekday() < 5:  # Monday = 0, Friday = 4
                weekdays += 1
            current = current + timedelta(days=1)

        return weekdays

    def calculate_for_range(
        self, start_date: date, end_date: date, leaves: List[Leave]
    ) -> WorkingDaysResult:
        """
        Calculate working days for a custom date range minus leaves.

        Only counts leaves that fall on weekdays within the range.
        """
        total_weekdays = self.calculate_weekdays_for_range(start_date, end_date)

        # Only count leaves that fall on weekdays and within the date range
        weekday_leaves = [
            l for l in leaves if l.is_weekday and start_date <= l.leave_date <= end_date
        ]

        return WorkingDaysResult(
            total_weekdays=total_weekdays,
            leaves=len(weekday_leaves),
            working_days=total_weekdays - len(weekday_leaves),
            leave_dates=[l.leave_date.isoformat() for l in leaves],
        )
