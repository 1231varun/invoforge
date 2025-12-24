"""Dashboard API routes"""

from flask import Blueprint, jsonify

from app.container import get_container
from app.core.services.update_checker import UpdateChecker
from app.version import __version__

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/check-update")
def check_update():
    """Check for app updates from GitHub releases"""
    try:
        checker = UpdateChecker()
        update_info = checker.check_for_updates()

        return jsonify(
            {
                "success": True,
                "current_version": update_info.current_version,
                "update_available": update_info.available,
                "latest_version": update_info.latest_version,
                "download_url": update_info.download_url,
                "release_notes": update_info.release_notes,
                "error": update_info.error,
            }
        )
    except Exception as e:
        return jsonify(
            {
                "success": False,
                "current_version": __version__,
                "update_available": False,
                "error": str(e),
            }
        )


@dashboard_bp.route("/dashboard")
def get_dashboard():
    """Get dashboard data"""
    container = get_container()

    try:
        response = container.dashboard_use_case.execute()

        if response.success:
            return jsonify(
                {
                    "success": True,
                    "stats": {
                        "total_invoices": response.stats.total_invoices,
                        "total_earned": response.stats.total_earned,
                        "leaves_this_year": response.stats.leaves_this_year,
                        "last_invoice": response.stats.last_invoice,
                    },
                    "current_month": {
                        "year": response.current_month.year,
                        "month": response.current_month.month,
                        "month_name": response.current_month.month_name,
                        "total_weekdays": response.current_month.total_weekdays,
                        "leaves": response.current_month.leaves,
                        "working_days": response.current_month.working_days,
                    },
                    "next_invoice_number": response.next_invoice_number,
                    "currency": response.currency,
                }
            )
        else:
            return jsonify({"success": False, "error": response.error}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
