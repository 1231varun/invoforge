"""
Invoice Generator Application

A clean architecture Flask application for generating export invoices.

Architecture:
    - core/         Domain layer (entities, services, interfaces)
    - application/  Use cases layer
    - infrastructure/  External implementations
    - presentation/    Web layer (Flask routes)
"""

from pathlib import Path

from flask import Flask


def create_app() -> Flask:
    """
    Flask application factory.

    Creates and configures the Flask application with all dependencies.
    """
    # Initialize the container first to ensure DB is ready
    from app.container import get_container

    get_container()

    # Create Flask app
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent / "templates"),
        static_folder=str(Path(__file__).parent.parent / "static"),
    )

    app.config["SECRET_KEY"] = "invoice-generator-secret"

    # Register routes
    from app.presentation.routes import register_routes

    register_routes(app)

    return app
