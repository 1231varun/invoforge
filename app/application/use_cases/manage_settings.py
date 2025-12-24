"""Manage Settings Use Case"""
from dataclasses import dataclass
from typing import Any, Dict, Optional

from app.core.entities.settings import Settings
from app.core.interfaces.settings_repository import SettingsRepository


@dataclass
class SettingsResponse:
    success: bool
    settings: Optional[Settings] = None
    error: Optional[str] = None


class ManageSettingsUseCase:
    """
    Use case for managing application settings.
    """

    def __init__(self, settings_repository: SettingsRepository):
        self._settings = settings_repository

    def get_settings(self) -> SettingsResponse:
        """Get all settings"""
        try:
            settings = self._settings.get_all()
            return SettingsResponse(success=True, settings=settings)
        except Exception as e:
            return SettingsResponse(success=False, error=str(e))

    def save_settings(self, data: Dict[str, Any]) -> SettingsResponse:
        """Save settings from dictionary"""
        try:
            self._settings.save_all(data)
            settings = self._settings.get_all()
            return SettingsResponse(success=True, settings=settings)
        except Exception as e:
            return SettingsResponse(success=False, error=str(e))

    def is_setup_complete(self) -> bool:
        """Check if initial setup is complete"""
        return self._settings.is_setup_complete()

    def get_config(self) -> Dict[str, Any]:
        """Get configuration for frontend"""
        settings = self._settings.get_all()
        return {
            "rate": settings.daily_rate,
            "currency": settings.currency,
            "setup_complete": settings.setup_complete
        }

