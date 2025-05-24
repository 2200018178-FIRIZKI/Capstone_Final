# app/config.py
import os
from dotenv import load_dotenv

# Tentukan path ke direktori root proyek
# __file__ adalah path ke file config.py saat ini (app/config.py)
# os.path.dirname(__file__) akan memberikan path ke folder app/
# os.path.join(os.path.dirname(__file__), '..') akan naik satu level ke root proyek
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Muat variabel lingkungan dari file .env yang ada di root proyek
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    """
    Konfigurasi dasar untuk aplikasi Flask.
    Variabel konfigurasi dimuat dari environment variables.
    """

    # Kunci rahasia untuk keamanan sesi dan data lainnya
    # Diambil dari environment variable SECRET_KEY, atau gunakan nilai default jika tidak ada
    SECRET_KEY = (
        os.environ.get("SECRET_KEY") or "ganti-dengan-kunci-rahasia-yang-sangat-aman"
    )

    # Konfigurasi database SQLAlchemy
    # Diambil dari environment variable DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(
        basedir, "app.db"
    )  # Default ke SQLite jika DATABASE_URL tidak diset

    # Nonaktifkan fitur pelacakan modifikasi SQLAlchemy karena memakan resource
    # dan tidak selalu dibutuhkan. Lebih baik diatur False kecuali Anda tahu membutuhkannya.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Konfigurasi JWT (JSON Web Token) Extended
    # Kunci rahasia untuk menandatangani JWT, bisa sama dengan SECRET_KEY aplikasi
    # atau kunci terpisah untuk keamanan lebih.
    JWT_SECRET_KEY = (
        os.environ.get("JWT_SECRET_KEY")
        or SECRET_KEY
        or "jwt-ganti-dengan-kunci-rahasia-lain"
    )
    JWT_ACCESS_TOKEN_EXPIRES = (
        False  # Atur False agar token tidak kedaluwarsa, atau atur timedelta
    )
    # Contoh: from datetime import timedelta
    # JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1) # Token kedaluwarsa dalam 1 jam
    # JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30) # Refresh token kedaluwarsa dalam 30 hari

    # --- KONFIGURASI UPLOAD FILE ---
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER") or os.path.join(basedir, "uploads")
    ALLOWED_EXTENSIONS = {
        "txt",
        "pdf",
        "png",
        "jpg",
        "jpeg",
        "gif",
        "doc",
        "docx",
        "xls",
        "xlsx",
    }
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Batas ukuran file: 16MB
    # --- AKHIR KONFIGURASI UPLOAD FILE ---


class DevelopmentConfig(Config):
    """Konfigurasi untuk lingkungan pengembangan."""

    DEBUG = True
    # Anda bisa menambahkan konfigurasi spesifik development di sini
    # Misalnya, menggunakan database SQLite untuk development yang lebih mudah
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'dev_app.db')


class TestingConfig(Config):
    """Konfigurasi untuk lingkungan pengujian."""

    TESTING = True
    # Biasanya menggunakan database in-memory atau database terpisah untuk testing
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # Contoh: database SQLite in-memory
    # Nonaktifkan CSRF protection dalam form saat testing (jika menggunakan Flask-WTF)
    # WTF_CSRF_ENABLED = False
    UPLOAD_FOLDER = os.path.join(basedir, "test_uploads")


class ProductionConfig(Config):
    """Konfigurasi untuk lingkungan produksi."""

    DEBUG = False
    TESTING = False
    # Pastikan semua variabel sensitif diatur melalui environment variables di server produksi
    # dan tidak ada nilai default yang tidak aman.


# Dictionary untuk memetakan nama konfigurasi ke kelasnya
# Ini akan digunakan di create_app untuk memilih konfigurasi berdasarkan environment variable
config_by_name = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig,
    default=DevelopmentConfig,  # Konfigurasi default jika FLASK_ENV tidak diset
)
