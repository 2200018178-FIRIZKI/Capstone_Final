# app/contents/routes.py
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.auth.models import User
from app.categories.models import Category
from .models import Content, ContentCategory
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid  # Untuk memastikan ID konsisten jika dibuat manual

# Buat Blueprint untuk modul contents
contents_bp = Blueprint("contents_bp", __name__, url_prefix="/contents")


@contents_bp.route("", methods=["POST"])
@jwt_required()
def create_content():
    """
    Endpoint untuk membuat konten baru.
    Menerima title, content_type, data_url (opsional), metadata_tags (opsional),
    dan category_ids (array ID kategori) dalam format JSON.
    Memerlukan autentikasi JWT.
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()

    if not data:
        return (
            jsonify({"msg": "Request body tidak boleh kosong (JSON diperlukan)"}),
            400,
        )

    title = data.get("title")
    content_type = data.get("content_type")  # Misal: 'image', 'text', 'video'
    data_url = data.get("data_url")  # URL ke file atau teks konten jika pendek
    metadata_tags = data.get(
        "metadata_tags"
    )  # Bisa berupa list atau dict, disimpan sebagai JSON
    category_ids = data.get("category_ids")  # Diharapkan berupa list ID kategori

    if not title or not content_type:
        return jsonify({"msg": "Title dan content_type diperlukan"}), 400

    # Validasi category_ids jika diberikan
    categories_to_assign = []
    if category_ids:
        if not isinstance(category_ids, list):
            return jsonify({"msg": "category_ids harus berupa array/list"}), 400
        for cat_id in category_ids:
            category = Category.query.get(
                str(cat_id)
            )  # Pastikan ID adalah string jika UUID
            if not category:
                return (
                    jsonify({"msg": f"Kategori dengan ID {cat_id} tidak ditemukan"}),
                    404,
                )
            categories_to_assign.append(category)

    new_content = Content(
        title=title,
        content_type=content_type,
        data_url=data_url,
        metadata_tags=metadata_tags,
        user_id=current_user_id,
    )

    try:
        db.session.add(new_content)
        # Jika ada kategori yang akan di-assign, buat entri di ContentCategory
        if categories_to_assign:
            for category in categories_to_assign:
                # new_content.id belum ada sebelum commit, jadi kita commit dulu kontennya
                # atau kita bisa buat relasi melalui objek ContentCategory secara langsung
                # setelah new_content memiliki ID.
                # Cara yang lebih aman adalah commit new_content dulu, lalu assign kategori.
                # Atau, jika menggunakan relasi backref, bisa langsung:
                # new_content.categories_assoc.append(ContentCategory(category=category))
                # tapi ini memerlukan new_content.id, jadi kita buat setelah commit konten.
                pass  # Penanganan asosiasi setelah commit

        db.session.commit()  # Commit untuk mendapatkan new_content.id

        # Sekarang assign kategori setelah new_content punya ID
        if categories_to_assign:
            for category in categories_to_assign:
                assoc = ContentCategory(
                    content_id=new_content.id, category_id=category.id
                )
                db.session.add(assoc)
            db.session.commit()  # Commit asosiasi

        content_id_str = str(new_content.id)

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Gagal membuat konten", "error": str(e)}), 500

    # Siapkan data kategori untuk respons
    assigned_categories_data = []
    if new_content.categories_assoc:  # Akses melalui relasi yang sudah didefinisikan
        for assoc in new_content.categories_assoc:
            assigned_categories_data.append(
                {"id": str(assoc.category.id), "name": assoc.category.name}
            )

    return (
        jsonify(
            {
                "msg": "Konten berhasil dibuat",
                "content": {
                    "id": content_id_str,
                    "title": new_content.title,
                    "content_type": new_content.content_type,
                    "data_url": new_content.data_url,
                    "metadata_tags": new_content.metadata_tags,
                    "user_id": new_content.user_id,
                    "created_at": new_content.created_at.isoformat() + "Z",
                    "updated_at": new_content.updated_at.isoformat() + "Z",
                    "categories": assigned_categories_data,
                },
            }
        ),
        201,
    )


@contents_bp.route("", methods=["GET"])
def get_all_contents():
    """
    Endpoint untuk mendapatkan daftar semua konten.
    Mendukung filter berdasarkan category_id.
    """
    category_id_filter = request.args.get("category_id")
    query = Content.query.order_by(Content.created_at.desc())

    if category_id_filter:
        # Filter konten yang termasuk dalam kategori tertentu
        # Ini memerlukan join dengan tabel content_categories
        query = query.join(Content.categories_assoc).filter(
            ContentCategory.category_id == category_id_filter
        )
        # Alternatif jika ingin lebih eksplisit:
        # query = query.join(ContentCategory, Content.id == ContentCategory.content_id)\
        #              .filter(ContentCategory.category_id == category_id_filter)

    contents = query.all()
    output = []
    for content_item in contents:
        categories_data = []
        for assoc in content_item.categories_assoc:
            categories_data.append(
                {"id": str(assoc.category.id), "name": assoc.category.name}
            )

        content_data = {
            "id": str(content_item.id),
            "title": content_item.title,
            "content_type": content_item.content_type,
            "data_url": content_item.data_url,
            "metadata_tags": content_item.metadata_tags,
            "user_id": str(content_item.user_id),
            "created_at": content_item.created_at.isoformat() + "Z",
            "updated_at": content_item.updated_at.isoformat() + "Z",
            "categories": categories_data,
        }
        output.append(content_data)

    return jsonify(output), 200


@contents_bp.route("/<string:content_id>", methods=["GET"])
def get_content_by_id(content_id):
    """
    Endpoint untuk mendapatkan detail satu konten berdasarkan ID.
    """
    content_item = Content.query.get(content_id)
    if not content_item:
        return jsonify({"msg": "Konten tidak ditemukan"}), 404

    categories_data = []
    for assoc in content_item.categories_assoc:
        categories_data.append(
            {"id": str(assoc.category.id), "name": assoc.category.name}
        )

    return (
        jsonify(
            {
                "id": str(content_item.id),
                "title": content_item.title,
                "content_type": content_item.content_type,
                "data_url": content_item.data_url,
                "metadata_tags": content_item.metadata_tags,
                "user_id": str(content_item.user_id),
                "created_at": content_item.created_at.isoformat() + "Z",
                "updated_at": content_item.updated_at.isoformat() + "Z",
                "categories": categories_data,
            }
        ),
        200,
    )


@contents_bp.route("/<string:content_id>/metadata", methods=["PUT"])
@jwt_required()
def update_content_metadata(content_id):
    """
    Endpoint untuk memperbarui metadata (seperti tags) dari sebuah konten.
    Juga bisa digunakan untuk memperbarui kategori yang terasosiasi.
    Memerlukan autentikasi JWT.
    """
    content_item = Content.query.get(content_id)
    if not content_item:
        return jsonify({"msg": "Konten tidak ditemukan"}), 404

    # Otorisasi: Pastikan hanya pemilik konten yang bisa update (opsional)
    # current_user_id = get_jwt_identity()
    # if str(content_item.user_id) != current_user_id:
    #     return jsonify({"msg": "Anda tidak berhak mengubah konten ini"}), 403

    data = request.get_json()
    if not data:
        return (
            jsonify({"msg": "Request body tidak boleh kosong (JSON diperlukan)"}),
            400,
        )

    updated = False
    if "title" in data:
        content_item.title = data["title"]
        updated = True
    if "content_type" in data:
        content_item.content_type = data["content_type"]
        updated = True
    if "data_url" in data:
        content_item.data_url = data["data_url"]
        updated = True
    if "metadata_tags" in data:
        content_item.metadata_tags = data.get("metadata_tags")  # Bisa null
        updated = True

    if "category_ids" in data:
        new_category_ids = data.get("category_ids")
        if not isinstance(new_category_ids, list) and new_category_ids is not None:
            return (
                jsonify({"msg": "category_ids harus berupa array/list atau null"}),
                400,
            )

        # Hapus asosiasi kategori lama
        ContentCategory.query.filter_by(content_id=content_item.id).delete()

        # Tambah asosiasi kategori baru
        if new_category_ids:
            for cat_id in new_category_ids:
                category = Category.query.get(str(cat_id))
                if not category:
                    db.session.rollback()  # Batalkan penghapusan asosiasi lama jika ada kategori baru yang tidak valid
                    return (
                        jsonify(
                            {"msg": f"Kategori dengan ID {cat_id} tidak ditemukan"}
                        ),
                        404,
                    )
                assoc = ContentCategory(
                    content_id=content_item.id, category_id=category.id
                )
                db.session.add(assoc)
        updated = True

    if not updated:
        return jsonify({"msg": "Tidak ada data yang diubah"}), 200

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return (
            jsonify({"msg": "Gagal memperbarui metadata konten", "error": str(e)}),
            500,
        )

    # Ambil ulang data kategori setelah update
    categories_data = []
    for assoc in content_item.categories_assoc:
        categories_data.append(
            {"id": str(assoc.category.id), "name": assoc.category.name}
        )

    return (
        jsonify(
            {
                "msg": "Metadata konten berhasil diperbarui",
                "content": {
                    "id": str(content_item.id),
                    "title": content_item.title,
                    "content_type": content_item.content_type,
                    "data_url": content_item.data_url,
                    "metadata_tags": content_item.metadata_tags,
                    "categories": categories_data,
                    "updated_at": content_item.updated_at.isoformat() + "Z",
                },
            }
        ),
        200,
    )


@contents_bp.route("/<string:content_id>", methods=["DELETE"])
@jwt_required()
def delete_content(content_id):
    """
    Endpoint untuk menghapus konten.
    Memerlukan autentikasi JWT.
    """
    content_item = Content.query.get(content_id)
    if not content_item:
        return jsonify({"msg": "Konten tidak ditemukan"}), 404

    # Otorisasi: Pastikan hanya pemilik konten yang bisa delete (opsional)
    # current_user_id = get_jwt_identity()
    # if str(content_item.user_id) != current_user_id:
    #     return jsonify({"msg": "Anda tidak berhak menghapus konten ini"}), 403

    try:
        # Asosiasi di ContentCategory akan terhapus otomatis karena cascade di model Content.categories_assoc
        db.session.delete(content_item)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Gagal menghapus konten", "error": str(e)}), 500

    return jsonify({"msg": "Konten berhasil dihapus"}), 200
