"""SQLite Invoice Repository Implementation"""

from datetime import date, datetime
from typing import List, Optional

from app.core.entities.invoice import InvoiceRecord
from app.core.interfaces.invoice_repository import InvoiceRepository
from app.infrastructure.persistence.database import Database


class SQLiteInvoiceRepository(InvoiceRepository):
    """SQLite implementation of InvoiceRepository"""

    def __init__(self, database: Database):
        self._db = database

    def save(
        self,
        invoice_number: int,
        invoice_date: date,
        service_period_start: date,
        service_period_end: date,
        days_worked: int,
        amount: float,
        docx_path: str,
        pdf_path: Optional[str] = None,
    ) -> InvoiceRecord:
        with self._db.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO invoices
                (invoice_number, invoice_date, service_period_start, service_period_end,
                 days_worked, amount, docx_path, pdf_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    invoice_number,
                    invoice_date.isoformat(),
                    service_period_start.isoformat(),
                    service_period_end.isoformat(),
                    days_worked,
                    amount,
                    docx_path,
                    pdf_path,
                ),
            )
            return InvoiceRecord(
                id=cursor.lastrowid,
                invoice_number=invoice_number,
                invoice_date=invoice_date,
                service_period_start=service_period_start,
                service_period_end=service_period_end,
                days_worked=days_worked,
                amount=amount,
                docx_path=docx_path,
                pdf_path=pdf_path,
                created_at=datetime.now().isoformat(),
            )

    def get_all(self) -> List[InvoiceRecord]:
        with self._db.connection() as conn:
            rows = conn.execute(
                """
                SELECT id, invoice_number, invoice_date, service_period_start,
                       service_period_end, days_worked, amount, docx_path, pdf_path, created_at
                FROM invoices
                ORDER BY created_at DESC
                """
            ).fetchall()

            return [self._row_to_record(row) for row in rows]

    def get_by_id(self, invoice_id: int) -> Optional[InvoiceRecord]:
        with self._db.connection() as conn:
            row = conn.execute(
                """
                SELECT id, invoice_number, invoice_date, service_period_start,
                       service_period_end, days_worked, amount, docx_path, pdf_path, created_at
                FROM invoices WHERE id = ?
                """,
                (invoice_id,),
            ).fetchone()

            return self._row_to_record(row) if row else None

    def delete(self, invoice_id: int) -> bool:
        with self._db.connection() as conn:
            cursor = conn.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
            return cursor.rowcount > 0

    def get_next_number(self) -> int:
        return self.get_last_number() + 1

    def get_last_number(self) -> int:
        with self._db.connection() as conn:
            row = conn.execute("SELECT MAX(invoice_number) as max_num FROM invoices").fetchone()
            return row["max_num"] if row and row["max_num"] else 0

    def _row_to_record(self, row) -> InvoiceRecord:
        return InvoiceRecord(
            id=row["id"],
            invoice_number=row["invoice_number"],
            invoice_date=date.fromisoformat(row["invoice_date"]),
            service_period_start=date.fromisoformat(row["service_period_start"]),
            service_period_end=date.fromisoformat(row["service_period_end"]),
            days_worked=row["days_worked"],
            amount=row["amount"],
            docx_path=row["docx_path"],
            pdf_path=row["pdf_path"],
            created_at=row["created_at"],
        )
