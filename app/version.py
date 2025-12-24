"""InvoForge Version Information"""

__version__ = "0.1.1"
__version_info__ = (0, 1, 1)

# The year the app was first released - copyright year will never be less than this
# This protects against incorrect system clocks showing past dates
COPYRIGHT_START_YEAR = 2025

# GitHub repository for update checks
GITHUB_OWNER = "1231varun"
GITHUB_REPO = "invoforge"
GITHUB_RELEASES_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"

# Version history:
# 0.1.0 - Initial development release


def parse_version(version_str: str) -> tuple:
    """Parse version string to tuple for comparison (e.g., '1.0.0' -> (1, 0, 0))"""
    # Remove 'v' prefix if present
    version_str = version_str.lstrip("v")
    try:
        parts = version_str.split(".")
        return tuple(int(p) for p in parts[:3])
    except (ValueError, AttributeError):
        return (0, 0, 0)


def is_newer_version(remote_version: str, current_version: str = __version__) -> bool:
    """Check if remote version is newer than current version"""
    remote = parse_version(remote_version)
    current = parse_version(current_version)
    return remote > current
