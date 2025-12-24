"""Page routes - HTML views"""

from datetime import datetime
from pathlib import Path

from flask import Blueprint, redirect, render_template, send_from_directory, url_for

from app.container import get_container
from app.version import COPYRIGHT_START_YEAR, __version__

pages_bp = Blueprint("pages", __name__)


def get_copyright_year():
    """
    Get the copyright year, ensuring it's never less than the app's release year.
    Protects against incorrect system clocks showing past dates.
    """
    return max(COPYRIGHT_START_YEAR, datetime.now().year)


def get_template_context(**kwargs):
    """Get common template context with version and year"""
    return {"version": __version__, "year": get_copyright_year(), **kwargs}


# Static directory for PWA assets
STATIC_DIR = Path(__file__).parent.parent.parent.parent / "static"


@pages_bp.route("/sw.js")
def service_worker():
    """Serve service worker from root with dynamic version injection"""
    from flask import Response

    sw_path = STATIC_DIR / "sw.js"
    with open(sw_path, "r") as f:
        content = f.read()

    # Inject version from single source of truth
    content = content.replace("{{VERSION}}", __version__)

    return Response(content, mimetype="application/javascript")


@pages_bp.route("/")
def index():
    """Landing page / dashboard"""
    container = get_container()
    if not container.settings_use_case.is_setup_complete():
        return redirect(url_for("pages.setup"))

    settings = container.settings_use_case.get_settings().settings
    return render_template(
        "index.html", **get_template_context(defaults=settings, active_tab="dashboard")
    )


@pages_bp.route("/invoice")
def invoice():
    """Invoice generator page"""
    container = get_container()
    if not container.settings_use_case.is_setup_complete():
        return redirect(url_for("pages.setup"))

    settings = container.settings_use_case.get_settings().settings
    return render_template(
        "index.html", **get_template_context(defaults=settings, active_tab="invoice")
    )


@pages_bp.route("/leaves")
def leaves():
    """Leave calendar page"""
    container = get_container()
    if not container.settings_use_case.is_setup_complete():
        return redirect(url_for("pages.setup"))

    settings = container.settings_use_case.get_settings().settings
    return render_template(
        "index.html", **get_template_context(defaults=settings, active_tab="leaves")
    )


@pages_bp.route("/history")
def history():
    """Invoice history page"""
    container = get_container()
    if not container.settings_use_case.is_setup_complete():
        return redirect(url_for("pages.setup"))

    settings = container.settings_use_case.get_settings().settings
    return render_template(
        "index.html", **get_template_context(defaults=settings, active_tab="history")
    )


@pages_bp.route("/settings")
def settings():
    """Settings page"""
    container = get_container()
    if not container.settings_use_case.is_setup_complete():
        return redirect(url_for("pages.setup"))

    settings_data = container.settings_use_case.get_settings().settings
    return render_template(
        "index.html", **get_template_context(defaults=settings_data, active_tab="settings")
    )


@pages_bp.route("/setup")
def setup():
    """First-time setup page"""
    container = get_container()
    if container.settings_use_case.is_setup_complete():
        return redirect(url_for("pages.index"))

    settings = container.settings_use_case.get_settings().settings
    return render_template("setup.html", **get_template_context(defaults=settings))
