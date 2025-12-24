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


class TestCalculateWeekdaysForRange:
    """Tests for calculate_weekdays_for_range method (custom date ranges)."""

    def test_full_month_matches_calculate_weekdays(
        self, working_days_calculator: WorkingDaysCalculator
    ):
        """Full month range should match calculate_weekdays result."""
        start = date(2025, 1, 1)
        end = date(2025, 1, 31)

        result = working_days_calculator.calculate_weekdays_for_range(start, end)

        assert result == 23  # Same as calculate_weekdays(2025, 1)

    def test_partial_month_start(self, working_days_calculator: WorkingDaysCalculator):
        """Partial month from mid-month to end."""
        # Dec 15-31, 2025: 15th is Monday
        start = date(2025, 12, 15)
        end = date(2025, 12, 31)

        result = working_days_calculator.calculate_weekdays_for_range(start, end)

        # Dec 15 (Mon) to Dec 31 (Wed) = 13 weekdays
        assert result == 13

    def test_partial_month_end(self, working_days_calculator: WorkingDaysCalculator):
        """Partial month from start to mid-month."""
        # Dec 1-15, 2025: 1st is Monday
        start = date(2025, 12, 1)
        end = date(2025, 12, 15)

        result = working_days_calculator.calculate_weekdays_for_range(start, end)

        # Dec 1 (Mon) to Dec 15 (Mon) = 11 weekdays
        assert result == 11

    def test_single_weekday(self, working_days_calculator: WorkingDaysCalculator):
        """Single weekday should return 1."""
        start = date(2025, 1, 6)  # Monday
        end = date(2025, 1, 6)

        result = working_days_calculator.calculate_weekdays_for_range(start, end)

        assert result == 1

    def test_single_weekend_day(self, working_days_calculator: WorkingDaysCalculator):
        """Single weekend day should return 0."""
        start = date(2025, 1, 4)  # Saturday
        end = date(2025, 1, 4)

        result = working_days_calculator.calculate_weekdays_for_range(start, end)

        assert result == 0

    def test_cross_month_range(self, working_days_calculator: WorkingDaysCalculator):
        """Range spanning two months."""
        # Dec 20, 2025 to Jan 10, 2026
        start = date(2025, 12, 20)
        end = date(2026, 1, 10)

        result = working_days_calculator.calculate_weekdays_for_range(start, end)

        # Dec 20 (Sat) - Dec 31 (Wed): 8 weekdays
        # Jan 1 (Thu) - Jan 10 (Sat): 7 weekdays
        # Total: 15 weekdays
        assert result == 15


class TestCalculateForRange:
    """Tests for calculate_for_range method with custom date ranges and leaves."""

    def test_full_month_no_leaves(self, working_days_calculator: WorkingDaysCalculator):
        """Full month with no leaves."""
        start = date(2025, 1, 1)
        end = date(2025, 1, 31)

        result = working_days_calculator.calculate_for_range(start, end, [])

        assert result.total_weekdays == 23
        assert result.leaves == 0
        assert result.working_days == 23

    def test_partial_month_with_leaves(self, working_days_calculator: WorkingDaysCalculator):
        """Partial month with leaves within range."""
        start = date(2025, 1, 15)  # Wednesday
        end = date(2025, 1, 31)

        leaves = [
            Leave(id=1, leave_date=date(2025, 1, 20), reason="Holiday"),  # Monday
            Leave(id=2, leave_date=date(2025, 1, 21), reason="Holiday"),  # Tuesday
        ]

        result = working_days_calculator.calculate_for_range(start, end, leaves)

        # Jan 15-31 has 13 weekdays, minus 2 leaves = 11
        assert result.total_weekdays == 13
        assert result.leaves == 2
        assert result.working_days == 11

    def test_leaves_outside_range_not_counted(self, working_days_calculator: WorkingDaysCalculator):
        """Leaves outside the date range are not counted."""
        start = date(2025, 1, 15)
        end = date(2025, 1, 31)

        leaves = [
            Leave(id=1, leave_date=date(2025, 1, 6), reason="Before range"),  # Before
            Leave(id=2, leave_date=date(2025, 1, 20), reason="In range"),  # In range
            Leave(id=3, leave_date=date(2025, 2, 5), reason="After range"),  # After
        ]

        result = working_days_calculator.calculate_for_range(start, end, leaves)

        assert result.leaves == 1  # Only the one in range

    def test_weekend_leaves_in_range_not_counted(
        self, working_days_calculator: WorkingDaysCalculator
    ):
        """Weekend leaves within range don't count."""
        start = date(2025, 1, 1)
        end = date(2025, 1, 31)

        leaves = [
            Leave(id=1, leave_date=date(2025, 1, 4), reason="Saturday"),
            Leave(id=2, leave_date=date(2025, 1, 5), reason="Sunday"),
        ]

        result = working_days_calculator.calculate_for_range(start, end, leaves)

        assert result.leaves == 0
        assert result.working_days == 23
