# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# Jika Anda berencana menggunakan Flask-CORS (untuk menangani Cross-Origin Resource Sharing)
# from flask_cors import CORS
# Jika Anda berencana menggunakan Flask-Marshmallow (untuk serialisasi/deserialisasi objek)
# from flask_marshmallow import Marshmallow

# Inisialisasi instance SQLAlchemy
# Ini akan digunakan untuk berinteraksi dengan database.
db = SQLAlchemy()

# Inisialisasi instance Migrate
# Ini akan digunakan untuk menangani migrasi skema database dengan Alembic.
# Instance ini akan dihubungkan dengan aplikasi Flask dan instance SQLAlchemy di app/__init__.py.
migrate = Migrate()

# Inisialisasi instance JWTManager
# Ini akan digunakan untuk menangani autentikasi berbasis JSON Web Token.
jwt = JWTManager()

# Contoh jika Anda menggunakan ekstensi lain:
# cors = CORS()
# ma = Marshmallow()

# Anda bisa menambahkan inisialisasi ekstensi lain di sini
# sesuai kebutuhan proyek Anda.
