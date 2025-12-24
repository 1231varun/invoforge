"""Leave repository interface (port)"""

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from app.core.entities.leave import Leave


class LeaveRepository(ABC):
    """Interface for leave persistence operations"""

    @abstractmethod
    def add(self, leave_date: date, reason: str = "") -> Leave:
        """Add or update a leave"""
        pass

    @abstractmethod
    def remove(self, leave_id: int) -> bool:
        """Remove a leave by ID"""
        pass

    @abstractmethod
    def remove_by_date(self, leave_date: date) -> bool:
        """Remove a leave by date"""
        pass

    @abstractmethod
    def get_by_date(self, leave_date: date) -> Optional[Leave]:
        """Get a leave by date"""
        pass

    @abstractmethod
    def get_for_month(self, year: int, month: int) -> List[Leave]:
        """Get all leaves for a specific month"""
        pass

    @abstractmethod
    def get_for_range(self, start_date: str, end_date: str) -> List[Leave]:
        """Get all leaves within a date range"""
        pass

    @abstractmethod
    def get_all(self, year: Optional[int] = None) -> List[Leave]:
        """Get all leaves, optionally filtered by year"""
        pass
