# app/__init__.py
import os
from flask import Flask
from .config import config_by_name, Config  # Pastikan Config diimpor jika merujuknya
from .extensions import db, migrate, jwt

# --- TAMBAHKAN IMPOR UNTUK ML ---
from . import ml_services  # Impor modul ml_services

# --- AKHIR IMPOR ML ---


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    # Muat konfigurasi dari objek berdasarkan nama konfigurasi
    selected_config = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(selected_config)
    print(f" * Loading configuration: {config_name}")

    # Pastikan folder upload ada
    upload_folder = app.config.get("UPLOAD_FOLDER")
    if upload_folder and not os.path.exists(upload_folder):
        try:
            os.makedirs(upload_folder)
            print(f" * Created upload folder: {upload_folder}")
        except OSError as e:
            app.logger.error(
                f"Gagal membuat folder upload '{upload_folder}' pada startup: {e}"
            )

    # Atur MAX_CONTENT_LENGTH di aplikasi Flask dari objek Config
    # Ambil dari config yang sudah dimuat, atau fallback ke Config dasar
    app.config["MAX_CONTENT_LENGTH"] = app.config.get(
        "MAX_CONTENT_LENGTH", Config.MAX_CONTENT_LENGTH
    )

    # --- MEMUAT MODEL ML SAAT STARTUP ---
    try:
        # Menggunakan app_context() memastikan konfigurasi aplikasi (seperti logger) tersedia
        with app.app_context():
            ml_services.load_model_and_preprocessors()
    except FileNotFoundError as e:
        app.logger.error(
            f"PENTING: File model ML tidak ditemukan. Aplikasi mungkin tidak berfungsi dengan benar untuk fitur ML. Error: {e}"
        )
        # Anda bisa memutuskan apakah akan menghentikan aplikasi atau tidak
        # raise SystemExit(f"Kritis: File model ML tidak ditemukan: {e}")
    except Exception as e:
        app.logger.error(
            f"KRUSIAL: Gagal memuat model Machine Learning atau preprocessor saat startup aplikasi: {str(e)}",
            exc_info=True,
        )
        # Pertimbangkan untuk menghentikan aplikasi jika model adalah komponen inti
        # raise SystemExit(f"Kritis: Model ML gagal dimuat: {str(e)}")
    # --- AKHIR MEMUAT MODEL ML ---

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # --- REGISTRASI BLUEPRINT ---
    from .auth.routes import auth_bp

    app.register_blueprint(auth_bp)

    from .categories.routes import categories_bp

    app.register_blueprint(categories_bp)

    from .contents.routes import contents_bp

    app.register_blueprint(contents_bp)

    from .targets.routes import targets_bp

    app.register_blueprint(targets_bp)

    from .files.routes import files_bp

    app.register_blueprint(files_bp)

    from .ml_routes import ml_bp  # <-- Impor ml_bp

    app.register_blueprint(ml_bp)  # <-- Daftarkan ml_bp
    # --- AKHIR REGISTRASI BLUEPRINT ---

    # Impor model database di dalam konteks aplikasi agar terdeteksi oleh Flask-Migrate
    with app.app_context():
        from .auth import models as auth_models
        from .categories import models as categories_models
        from .contents import models as contents_models
        from .files import models as files_models
        from .targets import models as targets_models

    @app.route("/hello")  # Route tes sederhana
    def hello():
        return (
            "Hello, World! Aplikasi Flask Anda berjalan dengan konfigurasi: "
            + config_name
        )

    return app
