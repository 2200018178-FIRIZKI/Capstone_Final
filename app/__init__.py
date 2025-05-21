# app/__init__.py
import os
from flask import Flask
from .config import config_by_name
from .extensions import db, migrate, jwt


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    try:
        app.config.from_object(config_by_name[config_name])
        print(f" * Loading configuration: {config_name}")
    except KeyError:
        print(
            f" ! Invalid configuration name: {config_name}. Defaulting to 'development'."
        )
        app.config.from_object(config_by_name["development"])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # --- REGISTRASI BLUEPRINT ---
    from .auth.routes import auth_bp

    app.register_blueprint(auth_bp)

    from .categories.routes import categories_bp

    app.register_blueprint(categories_bp)

    from .contents.routes import contents_bp  # Impor contents_bp

    app.register_blueprint(contents_bp)  # Daftarkan contents_bp
    # --- REGISTRASI BLUEPRINT SELESAI ---

    # Impor model di dalam konteks aplikasi
    with app.app_context():
        from .auth import models as auth_models
        from .categories import models as categories_models
        from .contents import models as contents_models
        from .files import models as files_models
        from .targets import models as targets_models

        # Analytics model jika ada, akan ditambahkan nanti

    @app.route("/hello")
    def hello():
        return (
            "Hello, World! Aplikasi Flask Anda berjalan dengan konfigurasi: "
            + config_name
        )

    return app
