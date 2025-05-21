# app/categories/routes.py
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.auth.models import User  # Untuk relasi atau otorisasi di masa depan
from .models import Category  # Impor model Category
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)  # Untuk melindungi endpoint jika diperlukan

# Buat Blueprint untuk modul categories
categories_bp = Blueprint("categories_bp", __name__, url_prefix="/categories")


@categories_bp.route("", methods=["POST"])
@jwt_required()  # Contoh: Hanya user yang login bisa membuat kategori
def create_category():
    """
    Endpoint untuk membuat kategori baru.
    Memerlukan autentikasi JWT.
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()  # Dapatkan ID user yang sedang login

    if not data:
        return (
            jsonify({"msg": "Request body tidak boleh kosong (JSON diperlukan)"}),
            400,
        )

    name = data.get("name")
    description = data.get("description")
    parent_id = data.get("parent_id")  # ID dari parent category (opsional)

    if not name:
        return jsonify({"msg": "Nama kategori diperlukan"}), 400

    if Category.query.filter_by(name=name).first():
        return jsonify({"msg": "Nama kategori sudah ada"}), 409

    # Validasi parent_id jika diberikan
    if parent_id:
        parent_category = Category.query.get(parent_id)
        if not parent_category:
            return jsonify({"msg": "Parent category tidak ditemukan"}), 404

    new_category = Category(
        name=name,
        description=description,
        parent_id=parent_id,
        # Anda bisa menambahkan user_id jika ingin mencatat siapa yang membuat kategori,
        # misalnya: created_by_user_id = current_user_id (perlu penyesuaian model)
    )

    try:
        db.session.add(new_category)
        db.session.commit()
        category_id_str = str(new_category.id)
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Gagal membuat kategori", "error": str(e)}), 500

    return (
        jsonify(
            {
                "msg": "Kategori berhasil dibuat",
                "category": {
                    "id": category_id_str,
                    "name": new_category.name,
                    "description": new_category.description,
                    "parent_id": new_category.parent_id,  # Akan null jika tidak ada parent
                    "created_at": new_category.created_at.isoformat() + "Z",
                    "updated_at": new_category.updated_at.isoformat() + "Z",
                },
            }
        ),
        201,
    )


@categories_bp.route("", methods=["GET"])
def get_all_categories():
    """
    Endpoint untuk mendapatkan daftar semua kategori.
    Nantinya bisa ditambahkan filter dan paginasi.
    """
    # Untuk sementara, ambil semua kategori
    # Pertimbangkan paginasi untuk data yang besar
    categories = Category.query.order_by(Category.name).all()

    output = []
    for category in categories:
        category_data = {
            "id": str(category.id),
            "name": category.name,
            "description": category.description,
            "parent_id": str(category.parent_id) if category.parent_id else None,
            "created_at": category.created_at.isoformat() + "Z",
            "updated_at": category.updated_at.isoformat() + "Z",
            # Anda bisa menambahkan jumlah konten atau subkategori jika diperlukan
        }
        output.append(category_data)

    return jsonify(output), 200


@categories_bp.route("/<string:category_id>", methods=["GET"])
def get_category_by_id(category_id):
    """
    Endpoint untuk mendapatkan detail satu kategori berdasarkan ID.
    """
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"msg": "Kategori tidak ditemukan"}), 404

    # Anda bisa menambahkan logika untuk menampilkan subkategori atau konten terkait
    # Misalnya, mengambil children:
    # children = [{"id": str(child.id), "name": child.name} for child in category.children.all()]

    return (
        jsonify(
            {
                "id": str(category.id),
                "name": category.name,
                "description": category.description,
                "parent_id": str(category.parent_id) if category.parent_id else None,
                "created_at": category.created_at.isoformat() + "Z",
                "updated_at": category.updated_at.isoformat() + "Z",
                # "children": children # Jika ingin menampilkan subkategori
            }
        ),
        200,
    )


@categories_bp.route("/<string:category_id>", methods=["PUT"])
@jwt_required()  # Contoh: Hanya user yang login bisa update
def update_category(category_id):
    """
    Endpoint untuk memperbarui kategori yang ada.
    Memerlukan autentikasi JWT.
    """
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"msg": "Kategori tidak ditemukan"}), 404

    data = request.get_json()
    if not data:
        return (
            jsonify({"msg": "Request body tidak boleh kosong (JSON diperlukan)"}),
            400,
        )

    # Update field jika ada di request body
    if "name" in data:
        # Cek apakah nama baru sudah digunakan oleh kategori lain
        existing_category_with_name = Category.query.filter(
            Category.name == data["name"], Category.id != category_id
        ).first()
        if existing_category_with_name:
            return (
                jsonify({"msg": "Nama kategori sudah digunakan oleh kategori lain"}),
                409,
            )
        category.name = data["name"]

    if "description" in data:
        category.description = data.get("description")  # Bisa null

    if "parent_id" in data:
        parent_id_new = data.get("parent_id")
        if parent_id_new:
            # Validasi parent_id baru
            if (
                parent_id_new == category.id
            ):  # Tidak boleh menjadi parent dari dirinya sendiri
                return (
                    jsonify(
                        {
                            "msg": "Kategori tidak bisa menjadi parent dari dirinya sendiri"
                        }
                    ),
                    400,
                )
            parent_category_new = Category.query.get(parent_id_new)
            if not parent_category_new:
                return jsonify({"msg": "Parent category baru tidak ditemukan"}), 404
            category.parent_id = parent_id_new
        else:  # Jika parent_id dikirim sebagai null/kosong, berarti jadi top-level
            category.parent_id = None

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Gagal memperbarui kategori", "error": str(e)}), 500

    return (
        jsonify(
            {
                "msg": "Kategori berhasil diperbarui",
                "category": {
                    "id": str(category.id),
                    "name": category.name,
                    "description": category.description,
                    "parent_id": (
                        str(category.parent_id) if category.parent_id else None
                    ),
                    "updated_at": category.updated_at.isoformat() + "Z",
                },
            }
        ),
        200,
    )


@categories_bp.route("/<string:category_id>", methods=["DELETE"])
@jwt_required()  # Contoh: Hanya user yang login bisa delete
def delete_category(category_id):
    """
    Endpoint untuk menghapus kategori.
    Memerlukan autentikasi JWT.
    """
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"msg": "Kategori tidak ditemukan"}), 404

    # Pertimbangkan apa yang terjadi pada subkategori atau konten terkait
    # Jika ada subkategori, apakah mereka juga dihapus, atau parent_id-nya di-set NULL?
    # Model Category kita sudah memiliki `ON DELETE SET NULL` untuk `parent_id` di skema DB,
    # dan relasi `children` di model.
    # Jika ada konten yang terkait, bagaimana penanganannya?
    # Untuk saat ini, kita hanya menghapus kategori.
    # Jika ada foreign key constraint yang menghalangi, penghapusan akan gagal.
    # Model Category.contents_assoc memiliki cascade="all, delete-orphan"
    # yang akan menghapus entri di content_categories jika kategori dihapus.

    try:
        # Jika ada subkategori, dan Anda ingin mereka menjadi top-level:
        # for child in category.children:
        #     child.parent_id = None
        # db.session.commit() # Commit perubahan pada children dulu jika ada

        db.session.delete(category)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Periksa apakah error disebabkan oleh foreign key constraint dari tabel lain
        # yang belum di-handle relasinya (misalnya, jika ada konten yang masih terkait langsung
        # dan tidak ada cascade delete di relasi tersebut).
        return jsonify({"msg": "Gagal menghapus kategori", "error": str(e)}), 500

    return jsonify({"msg": "Kategori berhasil dihapus"}), 200
