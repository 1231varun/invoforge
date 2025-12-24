"""Route modules for different domains"""

from app.presentation.routes.dashboard import dashboard_bp
from app.presentation.routes.invoices import invoices_bp
from app.presentation.routes.leaves import leaves_bp
from app.presentation.routes.pages import pages_bp
from app.presentation.routes.settings import settings_bp


def register_routes(app):
    """Register all route blueprints with the Flask app"""
    app.register_blueprint(pages_bp)
    app.register_blueprint(invoices_bp, url_prefix="/api")
    app.register_blueprint(leaves_bp, url_prefix="/api")
    app.register_blueprint(settings_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
