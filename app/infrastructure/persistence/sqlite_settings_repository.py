"""SQLite Settings Repository Implementation"""
from typing import Any, Dict

from app.core.entities.settings import Settings
from app.core.interfaces.settings_repository import SettingsRepository
from app.infrastructure.persistence.database import Database


class SQLiteSettingsRepository(SettingsRepository):
    """SQLite implementation of SettingsRepository"""

    def __init__(self, database: Database):
        self._db = database

    def get(self, key: str, default: str = "") -> str:
        with self._db.connection() as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = ?",
                (key,)
            ).fetchone()
            return row["value"] if row else default

    def set(self, key: str, value: str) -> None:
        with self._db.connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )

    def get_all(self) -> Settings:
        with self._db.connection() as conn:
            rows = conn.execute("SELECT key, value FROM settings").fetchall()
            data = {row["key"]: row["value"] for row in rows}
            return Settings.from_dict(data)

    def save_all(self, settings: Dict[str, Any]) -> None:
        with self._db.connection() as conn:
            for key, value in settings.items():
                if isinstance(value, bool):
                    value = "true" if value else "false"
                conn.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                    (key, str(value))
                )

    def is_setup_complete(self) -> bool:
        return self.get("setup_complete", "false").lower() == "true"

