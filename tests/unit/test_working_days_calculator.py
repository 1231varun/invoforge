"""
Unit tests for WorkingDaysCalculator service.

Tests cover:
- Weekday calculation for various months
- Leave filtering (weekday vs weekend)
- Service period calculation
- Edge cases (leap years, month boundaries)
"""

from datetime import date

from app.core.entities.leave import Leave
from app.core.services.working_days_calculator import WorkingDaysCalculator


class TestCalculateWeekdays:
    """Tests for calculate_weekdays method."""

    def test_january_2025_has_23_weekdays(self, working_days_calculator: WorkingDaysCalculator):
        """January 2025 starts on Wednesday, has 23 weekdays."""
        result = working_days_calculator.calculate_weekdays(2025, 1)
        assert result == 23

    def test_february_2025_has_20_weekdays(self, working_days_calculator: WorkingDaysCalculator):
        """February 2025 is not a leap year, has 20 weekdays."""
        result = working_days_calculator.calculate_weekdays(2025, 2)
        assert result == 20

    def test_february_2024_leap_year_has_21_weekdays(
        self, working_days_calculator: WorkingDaysCalculator
    ):
        """February 2024 is a leap year with 29 days, has 21 weekdays."""
        result = working_days_calculator.calculate_weekdays(2024, 2)
        assert result == 21

    def test_april_has_22_weekdays(self, working_days_calculator: WorkingDaysCalculator):
        """April 2025 has 30 days with 22 weekdays."""
        result = working_days_calculator.calculate_weekdays(2025, 4)
        assert result == 22

    def test_december_2025_has_23_weekdays(self, working_days_calculator: WorkingDaysCalculator):
        """December 2025 has 23 weekdays."""
        result = working_days_calculator.calculate_weekdays(2025, 12)
        assert result == 23


class TestCalculateWithLeaves:
    """Tests for calculate method with leaves."""

    def test_no_leaves_returns_all_weekdays(self, working_days_calculator: WorkingDaysCalculator):
        """With no leaves, working days equals weekdays."""
        result = working_days_calculator.calculate(2025, 1, [])

        assert result.total_weekdays == 23
        assert result.leaves == 0
        assert result.working_days == 23
        assert result.leave_dates == []

    def test_weekday_leaves_are_subtracted(
        self, working_days_calculator: WorkingDaysCalculator, january_2025_leaves: list[Leave]
    ):
        """Only weekday leaves are subtracted from working days."""
        result = working_days_calculator.calculate(2025, 1, january_2025_leaves)

        assert result.total_weekdays == 23
        assert result.leaves == 2  # Only 2 weekday leaves count
        assert result.working_days == 21  # 23 - 2
        assert len(result.leave_dates) == 3  # All leaves are listed

    def test_weekend_leaves_not_counted(self, working_days_calculator: WorkingDaysCalculator):
        """Leaves on weekends don't affect working days count."""
        weekend_leave = Leave(id=1, leave_date=date(2025, 1, 4), reason="Saturday")  # Saturday

        result = working_days_calculator.calculate(2025, 1, [weekend_leave])

        assert result.leaves == 0
        assert result.working_days == 23  # No change

    def test_all_weekday_leaves_subtracted(self, working_days_calculator: WorkingDaysCalculator):
        """Multiple weekday leaves are all subtracted."""
        leaves = [
            Leave(id=1, leave_date=date(2025, 1, 6), reason="Day 1"),  # Monday
            Leave(id=2, leave_date=date(2025, 1, 7), reason="Day 2"),  # Tuesday
            Leave(id=3, leave_date=date(2025, 1, 8), reason="Day 3"),  # Wednesday
        ]

        result = working_days_calculator.calculate(2025, 1, leaves)

        assert result.leaves == 3
        assert result.working_days == 20  # 23 - 3


class TestGetServicePeriod:
    """Tests for get_service_period method."""

    def test_returns_first_and_last_day_of_month(
        self, working_days_calculator: WorkingDaysCalculator
    ):
        """Service period spans entire month."""
        reference = date(2025, 1, 15)

        start, end = working_days_calculator.get_service_period(reference)

        assert start == date(2025, 1, 1)
        assert end == date(2025, 1, 31)

    def test_february_non_leap_year(self, working_days_calculator: WorkingDaysCalculator):
        """February in non-leap year ends on 28th."""
        reference = date(2025, 2, 10)

        start, end = working_days_calculator.get_service_period(reference)

        assert start == date(2025, 2, 1)
        assert end == date(2025, 2, 28)

    def test_february_leap_year(self, working_days_calculator: WorkingDaysCalculator):
        """February in leap year ends on 29th."""
        reference = date(2024, 2, 10)

        start, end = working_days_calculator.get_service_period(reference)

        assert start == date(2024, 2, 1)
        assert end == date(2024, 2, 29)

    def test_works_with_first_day_of_month(self, working_days_calculator: WorkingDaysCalculator):
        """Works correctly when reference is first day of month."""
        reference = date(2025, 3, 1)

        start, end = working_days_calculator.get_service_period(reference)

        assert start == date(2025, 3, 1)
        assert end == date(2025, 3, 31)

    def test_works_with_last_day_of_month(self, working_days_calculator: WorkingDaysCalculator):
        """Works correctly when reference is last day of month."""
        reference = date(2025, 4, 30)

        start, end = working_days_calculator.get_service_period(reference)

        assert start == date(2025, 4, 1)
        assert end == date(2025, 4, 30)
