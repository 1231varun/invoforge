"""Leave API routes"""

from datetime import datetime

from flask import Blueprint, jsonify, request

from app.application.use_cases.manage_leaves import AddLeaveRequest
from app.container import get_container

leaves_bp = Blueprint("leaves", __name__)


@leaves_bp.route("/leaves", methods=["GET"])
def list_leaves():
    """List leaves"""
    container = get_container()

    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    start = request.args.get("start")
    end = request.args.get("end")

    try:
        if start and end:
            response = container.leaves_use_case.get_leaves_for_calendar(start, end)
        elif year and month:
            response = container.leaves_use_case.get_leaves_for_month(year, month)
        else:
            response = container.leaves_use_case.get_all_leaves(year)

        if response.success:
            return jsonify(
                {
                    "success": True,
                    "leaves": [l.to_dict() for l in response.leaves],
                    "count": response.count,
                }
            )
        else:
            return jsonify({"success": False, "error": response.error}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@leaves_bp.route("/leaves/events", methods=["GET"])
def leaves_events():
    """Get leaves as FullCalendar events"""
    container = get_container()

    start = request.args.get("start", "")
    end = request.args.get("end", "")

    try:
        if start and end:
            response = container.leaves_use_case.get_leaves_for_calendar(start, end)
        else:
            response = container.leaves_use_case.get_all_leaves()

        if response.success:
            events = [l.to_calendar_event() for l in response.leaves]
            return jsonify(events)
        else:
            return jsonify([])

    except Exception:
        return jsonify([])


@leaves_bp.route("/leaves", methods=["POST"])
def add_leave():
    """Add a new leave"""
    data = request.json
    container = get_container()

    try:
        leave_date = datetime.strptime(data["leave_date"], "%Y-%m-%d").date()
        reason = data.get("reason", "")

        req = AddLeaveRequest(leave_date=leave_date, reason=reason)
        response = container.leaves_use_case.add_leave(req)

        if response.success:
            return jsonify({"success": True, "leave": response.leave.to_dict()})
        else:
            return jsonify({"success": False, "error": response.error}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@leaves_bp.route("/leaves/<int:leave_id>", methods=["DELETE"])
def delete_leave(leave_id: int):
    """Delete a leave by ID"""
    container = get_container()

    try:
        response = container.leaves_use_case.remove_leave(leave_id)
        return jsonify({"success": response.success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@leaves_bp.route("/leaves/by-date/<leave_date>", methods=["DELETE"])
def delete_leave_by_date(leave_date: str):
    """Delete a leave by date"""
    container = get_container()

    try:
        date_obj = datetime.strptime(leave_date, "%Y-%m-%d").date()
        response = container.leaves_use_case.remove_leave_by_date(date_obj)
        return jsonify({"success": response.success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@leaves_bp.route("/working-days")
def working_days():
    """Get working days for a date range or month"""
    container = get_container()

    # Support both date range and year/month for backwards compatibility
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    try:
        if start_date_str and end_date_str:
            # Use date range
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            response = container.working_days_use_case.execute_for_range(start_date, end_date)
        else:
            # Use year/month (backwards compatible)
            response = container.working_days_use_case.execute(year, month)

        if response.success:
            return jsonify(
                {
                    "success": True,
                    "total_weekdays": response.total_weekdays,
                    "leaves": response.leaves,
                    "working_days": response.working_days,
                    "leave_dates": response.leave_dates or [],
                }
            )
        else:
            return jsonify({"success": False, "error": response.error}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
