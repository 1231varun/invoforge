"""Update Checker Service - Checks GitHub for new releases"""
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional

from app.version import GITHUB_RELEASES_URL, __version__, is_newer_version


@dataclass
class UpdateInfo:
    """Information about an available update"""
    available: bool
    current_version: str
    latest_version: Optional[str] = None
    download_url: Optional[str] = None
    release_notes: Optional[str] = None
    error: Optional[str] = None


class UpdateChecker:
    """
    Checks GitHub releases for available updates.
    
    Works for desktop app deployments where the service worker
    update mechanism doesn't apply.
    """

    TIMEOUT = 5  # seconds

    def check_for_updates(self) -> UpdateInfo:
        """
        Check GitHub releases API for newer version.
        
        Returns UpdateInfo with update details or error.
        """
        try:
            # Create request with User-Agent (required by GitHub API)
            request = urllib.request.Request(
                GITHUB_RELEASES_URL,
                headers={
                    'User-Agent': f'InvoForge/{__version__}',
                    'Accept': 'application/vnd.github.v3+json'
                }
            )

            with urllib.request.urlopen(request, timeout=self.TIMEOUT) as response:
                data = json.loads(response.read().decode('utf-8'))

            latest_version = data.get('tag_name', '').lstrip('v')

            if not latest_version:
                return UpdateInfo(
                    available=False,
                    current_version=__version__,
                    error="Could not parse latest version"
                )

            # Check if update is available
            update_available = is_newer_version(latest_version)

            # Get download URL for the appropriate asset
            download_url = data.get('html_url', '')

            # Get release notes (body)
            release_notes = data.get('body', '')[:500]  # Truncate to 500 chars

            return UpdateInfo(
                available=update_available,
                current_version=__version__,
                latest_version=latest_version,
                download_url=download_url,
                release_notes=release_notes if update_available else None
            )

        except urllib.error.URLError as e:
            return UpdateInfo(
                available=False,
                current_version=__version__,
                error=f"Network error: {str(e.reason)}"
            )
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return UpdateInfo(
                    available=False,
                    current_version=__version__,
                    error="No releases found"
                )
            return UpdateInfo(
                available=False,
                current_version=__version__,
                error=f"GitHub API error: {e.code}"
            )
        except json.JSONDecodeError:
            return UpdateInfo(
                available=False,
                current_version=__version__,
                error="Invalid response from GitHub"
            )
        except Exception as e:
            return UpdateInfo(
                available=False,
                current_version=__version__,
                error=str(e)
            )

