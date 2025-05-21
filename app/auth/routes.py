# app/auth/routes.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from .models import User  # Impor model User dari modul auth

# Buat Blueprint untuk modul auth
# 'auth_bp' adalah nama Blueprint, __name__ adalah nama modul import,
# url_prefix akan menambahkan '/auth' di depan semua route dalam Blueprint ini.
auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register_user():
    """
    Endpoint untuk registrasi pengguna baru.
    Menerima username, email, dan password dalam format JSON.
    """
    data = request.get_json()

    if not data:
        return (
            jsonify({"msg": "Request body tidak boleh kosong (JSON diperlukan)"}),
            400,
        )

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"msg": "Username, email, dan password diperlukan"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username sudah digunakan"}), 409  # 409 Conflict

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email sudah terdaftar"}), 409

    # Buat user baru
    new_user = User(username=username, email=email)
    new_user.set_password(password)  # Gunakan metode set_password untuk hashing

    try:
        db.session.add(new_user)
        db.session.commit()
        # Dapatkan ID pengguna setelah commit untuk disertakan dalam token atau respons
        user_id_str = str(new_user.id)
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Gagal membuat pengguna", "error": str(e)}), 500

    # Buat access token untuk pengguna yang baru terdaftar (opsional, bisa juga hanya setelah login)
    # access_token = create_access_token(identity=user_id_str) # Menggunakan ID pengguna sebagai identity

    return (
        jsonify(
            {
                "msg": "Pengguna berhasil terdaftar",
                "user": {
                    "id": user_id_str,
                    "username": new_user.username,
                    "email": new_user.email,
                },
                # "access_token": access_token # Jika ingin langsung memberikan token
            }
        ),
        201,
    )  # 201 Created


@auth_bp.route("/login", methods=["POST"])
def login_user():
    """
    Endpoint untuk login pengguna.
    Menerima username (atau email) dan password dalam format JSON.
    Mengembalikan access token jika berhasil.
    """
    data = request.get_json()

    if not data:
        return (
            jsonify({"msg": "Request body tidak boleh kosong (JSON diperlukan)"}),
            400,
        )

    identifier = data.get("identifier")  # Bisa username atau email
    password = data.get("password")

    if not identifier or not password:
        return (
            jsonify({"msg": "Identifier (username/email) dan password diperlukan"}),
            400,
        )

    # Coba cari user berdasarkan username atau email
    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()

    if user and user.check_password(password):
        # Jika user ditemukan dan password cocok, buat access token
        user_id_str = str(user.id)
        access_token = create_access_token(identity=user_id_str)
        return (
            jsonify(
                access_token=access_token, user_id=user_id_str, username=user.username
            ),
            200,
        )
    else:
        # Jika user tidak ditemukan atau password salah
        return (
            jsonify({"msg": "Username/email atau password salah"}),
            401,
        )  # 401 Unauthorized


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()  # Endpoint ini memerlukan autentikasi JWT
def get_user_profile():
    """
    Endpoint untuk mendapatkan profil pengguna yang sedang login.
    Memerlukan token JWT yang valid di header Authorization.
    """
    current_user_id = get_jwt_identity()  # Dapatkan identity (ID pengguna) dari token
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"msg": "Pengguna tidak ditemukan"}), 404

    return (
        jsonify(
            {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at.isoformat() + "Z",
            }
        ),
        200,
    )


# Anda bisa menambahkan endpoint lain di sini, misalnya untuk logout, refresh token, dll.
