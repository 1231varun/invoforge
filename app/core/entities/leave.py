"""Leave domain entity"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Leave:
    """Represents a day off / leave"""

    id: Optional[int]
    leave_date: date
    reason: str = ""

    @property
    def is_weekday(self) -> bool:
        """Check if this leave falls on a weekday (Mon-Fri)"""
        return self.leave_date.weekday() < 5

    def to_dict(self) -> dict:
        return {"id": self.id, "leave_date": self.leave_date.isoformat(), "reason": self.reason}

    def to_calendar_event(self) -> dict:
        """Convert to FullCalendar event format"""
        return {
            "id": str(self.id),
            "title": self.reason or "Leave",
            "start": self.leave_date.isoformat(),
            "allDay": True,
            "backgroundColor": "#ef4444",
            "borderColor": "#dc2626",
            "extendedProps": {"reason": self.reason},
        }
