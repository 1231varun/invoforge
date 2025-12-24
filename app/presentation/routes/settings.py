"""Settings API routes"""
from flask import Blueprint, jsonify, request

from app.container import get_container

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/config")
def get_config():
    """Get frontend configuration"""
    container = get_container()

    config = container.settings_use_case.get_config()
    return jsonify(config)


@settings_bp.route("/settings", methods=["GET"])
def get_settings():
    """Get all settings"""
    container = get_container()

    try:
        response = container.settings_use_case.get_settings()

        if response.success:
            return jsonify({
                "success": True,
                "settings": response.settings.to_dict()
            })
        else:
            return jsonify({"success": False, "error": response.error}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@settings_bp.route("/settings", methods=["POST"])
def save_settings():
    """Save settings"""
    data = request.json
    container = get_container()

    try:
        response = container.settings_use_case.save_settings(data)

        if response.success:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": response.error}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

