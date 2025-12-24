"""SQLite Leave Repository Implementation"""

from datetime import date
from typing import List, Optional

from app.core.entities.leave import Leave
from app.core.interfaces.leave_repository import LeaveRepository
from app.infrastructure.persistence.database import Database


class SQLiteLeaveRepository(LeaveRepository):
    """SQLite implementation of LeaveRepository"""

    def __init__(self, database: Database):
        self._db = database

    def add(self, leave_date: date, reason: str = "") -> Leave:
        with self._db.connection() as conn:
            cursor = conn.execute(
                "INSERT OR REPLACE INTO leaves (leave_date, reason) VALUES (?, ?)",
                (leave_date.isoformat(), reason),
            )
            return Leave(id=cursor.lastrowid, leave_date=leave_date, reason=reason)

    def remove(self, leave_id: int) -> bool:
        with self._db.connection() as conn:
            cursor = conn.execute("DELETE FROM leaves WHERE id = ?", (leave_id,))
            return cursor.rowcount > 0

    def remove_by_date(self, leave_date: date) -> bool:
        with self._db.connection() as conn:
            cursor = conn.execute(
                "DELETE FROM leaves WHERE leave_date = ?", (leave_date.isoformat(),)
            )
            return cursor.rowcount > 0

    def get_by_date(self, leave_date: date) -> Optional[Leave]:
        with self._db.connection() as conn:
            row = conn.execute(
                "SELECT id, leave_date, reason FROM leaves WHERE leave_date = ?",
                (leave_date.isoformat(),),
            ).fetchone()

            return self._row_to_leave(row) if row else None

    def get_for_month(self, year: int, month: int) -> List[Leave]:
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"

        with self._db.connection() as conn:
            rows = conn.execute(
                """
                SELECT id, leave_date, reason FROM leaves 
                WHERE leave_date >= ? AND leave_date < ?
                ORDER BY leave_date
                """,
                (start_date, end_date),
            ).fetchall()

            return [self._row_to_leave(row) for row in rows]

    def get_for_range(self, start_date: str, end_date: str) -> List[Leave]:
        with self._db.connection() as conn:
            rows = conn.execute(
                """
                SELECT id, leave_date, reason FROM leaves 
                WHERE leave_date >= ? AND leave_date <= ?
                ORDER BY leave_date
                """,
                (start_date, end_date),
            ).fetchall()

            return [self._row_to_leave(row) for row in rows]

    def get_all(self, year: Optional[int] = None) -> List[Leave]:
        with self._db.connection() as conn:
            if year:
                rows = conn.execute(
                    """
                    SELECT id, leave_date, reason FROM leaves 
                    WHERE leave_date >= ? AND leave_date < ?
                    ORDER BY leave_date DESC
                    """,
                    (f"{year}-01-01", f"{year + 1}-01-01"),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, leave_date, reason FROM leaves ORDER BY leave_date DESC"
                ).fetchall()

            return [self._row_to_leave(row) for row in rows]

    def _row_to_leave(self, row) -> Leave:
        return Leave(
            id=row["id"], leave_date=date.fromisoformat(row["leave_date"]), reason=row["reason"]
        )
