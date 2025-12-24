"""SQLite Database Connection Manager"""
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "invoices.db"


class Database:
    """
    SQLite database connection manager.
    
    Provides connection pooling and schema initialization.
    """

    def __init__(self, db_path: Path = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a database connection with automatic commit/close"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_schema(self):
        """Initialize database schema"""
        with self.connection() as conn:
            # Leaves table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS leaves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    leave_date DATE NOT NULL UNIQUE,
                    reason TEXT DEFAULT ''
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_leave_date ON leaves(leave_date)"
            )

            # Invoices table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number INTEGER NOT NULL,
                    invoice_date DATE NOT NULL,
                    service_period_start DATE NOT NULL,
                    service_period_end DATE NOT NULL,
                    days_worked INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    docx_path TEXT NOT NULL,
                    pdf_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_invoice_date ON invoices(invoice_date)"
            )

            # Settings table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

