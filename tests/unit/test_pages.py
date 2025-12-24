"""Tests for pages routes"""

import os
from unittest.mock import patch


class TestIsStandaloneMode:
    """Tests for is_standalone_mode function"""

    def test_returns_true_when_invoforge_data_set(self):
        """Should return True when INVOFORGE_DATA env var is set"""
        with patch.dict(os.environ, {"INVOFORGE_DATA": "/some/path"}):
            from app.presentation.routes.pages import is_standalone_mode

            # Re-import to get fresh evaluation
            assert is_standalone_mode() is True

    def test_returns_false_when_invoforge_data_not_set(self):
        """Should return False when INVOFORGE_DATA env var is not set"""
        env = os.environ.copy()
        env.pop("INVOFORGE_DATA", None)
        with patch.dict(os.environ, env, clear=True):
            from app.presentation.routes.pages import is_standalone_mode

            assert is_standalone_mode() is False


class TestQuitEndpoint:
    """Tests for /api/quit endpoint"""

    def test_quit_returns_403_in_dev_mode(self, app_client):
        """Should return 403 when not in standalone mode"""
        response = app_client.post("/api/quit")
        assert response.status_code == 403
        assert b"standalone" in response.data.lower()
