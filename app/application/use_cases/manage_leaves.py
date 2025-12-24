"""Manage Leaves Use Case"""

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from app.core.entities.leave import Leave
from app.core.interfaces.leave_repository import LeaveRepository


@dataclass
class AddLeaveRequest:
    leave_date: date
    reason: str = ""


@dataclass
class LeaveResponse:
    success: bool
    leave: Optional[Leave] = None
    error: Optional[str] = None


@dataclass
class LeavesListResponse:
    success: bool
    leaves: List[Leave] = None
    count: int = 0
    error: Optional[str] = None


class ManageLeavesUseCase:
    """
    Use case for managing leaves.

    Provides operations for adding, removing, and querying leaves.
    """

    def __init__(self, leave_repository: LeaveRepository):
        self._leaves = leave_repository

    def add_leave(self, request: AddLeaveRequest) -> LeaveResponse:
        """Add a new leave"""
        try:
            leave = self._leaves.add(request.leave_date, request.reason)
            return LeaveResponse(success=True, leave=leave)
        except Exception as e:
            return LeaveResponse(success=False, error=str(e))

    def remove_leave(self, leave_id: int) -> LeaveResponse:
        """Remove a leave by ID"""
        try:
            success = self._leaves.remove(leave_id)
            return LeaveResponse(success=success)
        except Exception as e:
            return LeaveResponse(success=False, error=str(e))

    def remove_leave_by_date(self, leave_date: date) -> LeaveResponse:
        """Remove a leave by date"""
        try:
            success = self._leaves.remove_by_date(leave_date)
            return LeaveResponse(success=success)
        except Exception as e:
            return LeaveResponse(success=False, error=str(e))

    def get_leaves_for_month(self, year: int, month: int) -> LeavesListResponse:
        """Get all leaves for a specific month"""
        try:
            leaves = self._leaves.get_for_month(year, month)
            return LeavesListResponse(success=True, leaves=leaves, count=len(leaves))
        except Exception as e:
            return LeavesListResponse(success=False, error=str(e))

    def get_leaves_for_calendar(self, start: str, end: str) -> LeavesListResponse:
        """Get leaves for calendar view (FullCalendar)"""
        try:
            start_date = start.split("T")[0] if "T" in start else start
            end_date = end.split("T")[0] if "T" in end else end
            leaves = self._leaves.get_for_range(start_date, end_date)
            return LeavesListResponse(success=True, leaves=leaves, count=len(leaves))
        except Exception as e:
            return LeavesListResponse(success=False, error=str(e))

    def get_all_leaves(self, year: Optional[int] = None) -> LeavesListResponse:
        """Get all leaves, optionally filtered by year"""
        try:
            leaves = self._leaves.get_all(year)
            return LeavesListResponse(success=True, leaves=leaves, count=len(leaves))
        except Exception as e:
            return LeavesListResponse(success=False, error=str(e))
