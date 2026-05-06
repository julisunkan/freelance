import os
from flask import Flask, render_template, request
from models import init_db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, 'templates'),
        static_folder=os.path.join(BASE_DIR, 'static'),
    )
    app.secret_key = os.environ.get('NDA_SECRET_KEY', 'nda-generator-secret-2024')

    from routes.main import main_bp
    from routes.signing import signing_bp
    from routes.export import export_bp
    from routes.admin import admin_bp
    from routes.audit import audit_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(signing_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(audit_bp)

    @app.after_request
    def add_sw_header(response):
        if request.path.endswith('/sw.js'):
            # Allow the SW to claim the app root (e.g. /nda/ when mounted)
            scope = (request.script_root or '') + '/'
            response.headers['Service-Worker-Allowed'] = scope
        return response

    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html', code=404, message='Page not found.'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error.html', code=403, message='Access denied.'), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', code=500, message='Internal server error.'), 500

    with app.app_context():
        init_db()

    return app


app = create_app()
