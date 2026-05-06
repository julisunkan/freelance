import os
from flask import Flask, render_template, send_from_directory
from models import init_db

ADMIN_SECRET = "julisunkan"


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'freelancer-proposal-builder-secret-2024')

    from routes.proposals import proposals_bp
    from routes.admin import admin_bp
    from routes.export_routes import export_bp
    from routes.api import api_bp

    app.register_blueprint(proposals_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(api_bp)

    @app.route('/sw.js')
    def service_worker():
        return send_from_directory('static', 'sw.js',
                                   mimetype='application/javascript')

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    with app.app_context():
        init_db()

    return app


app = create_app()
