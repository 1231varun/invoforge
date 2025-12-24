"""Settings repository interface (port)"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from app.core.entities.settings import Settings


class SettingsRepository(ABC):
    """Interface for settings persistence operations"""

    @abstractmethod
    def get(self, key: str, default: str = "") -> str:
        """Get a single setting value"""
        pass

    @abstractmethod
    def set(self, key: str, value: str) -> None:
        """Set a single setting value"""
        pass

    @abstractmethod
    def get_all(self) -> Settings:
        """Get all settings as a Settings entity"""
        pass

    @abstractmethod
    def save_all(self, settings: Dict[str, Any]) -> None:
        """Save multiple settings at once"""
        pass

    @abstractmethod
    def is_setup_complete(self) -> bool:
        """Check if initial setup has been completed"""
        pass
