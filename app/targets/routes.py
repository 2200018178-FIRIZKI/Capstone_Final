# app/targets/routes.py
from flask import Blueprint, request, jsonify
from datetime import datetime
from app.extensions import db
from app.auth.models import (
    User,
)  # Mungkin diperlukan untuk info 'creator' atau 'recorder'
from .models import Target, TargetProgress
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid

# Buat Blueprint untuk modul targets
targets_bp = Blueprint("targets_bp", __name__, url_prefix="/targets")

# --- Endpoint untuk Target ---


@targets_bp.route("", methods=["POST"])
@jwt_required()
def create_target():
    """
    Endpoint untuk membuat target baru.
    Memerlukan autentikasi JWT.
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()

    if not data:
        return (
            jsonify({"msg": "Request body tidak boleh kosong (JSON diperlukan)"}),
            400,
        )

    name = data.get("name")
    description = data.get("description")

    if not name:
        return jsonify({"msg": "Nama target diperlukan"}), 400

    if Target.query.filter_by(
        name=name, user_id=current_user_id
    ).first():  # Target name unik per user
        return jsonify({"msg": "Anda sudah memiliki target dengan nama ini"}), 409

    new_target = Target(name=name, description=description, user_id=current_user_id)

    try:
        db.session.add(new_target)
        db.session.commit()
        target_id_str = str(new_target.id)
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Gagal membuat target", "error": str(e)}), 500

    return (
        jsonify(
            {
                "msg": "Target berhasil dibuat",
                "target": {
                    "id": target_id_str,
                    "name": new_target.name,
                    "description": new_target.description,
                    "user_id": new_target.user_id,
                    "created_at": new_target.created_at.isoformat() + "Z",
                    "updated_at": new_target.updated_at.isoformat() + "Z",
                },
            }
        ),
        201,
    )


@targets_bp.route("", methods=["GET"])
@jwt_required()
def get_all_targets_for_user():
    """
    Endpoint untuk mendapatkan daftar semua target milik pengguna yang sedang login.
    """
    current_user_id = get_jwt_identity()
    targets = (
        Target.query.filter_by(user_id=current_user_id)
        .order_by(Target.created_at.desc())
        .all()
    )

    output = []
    for target_item in targets:
        target_data = {
            "id": str(target_item.id),
            "name": target_item.name,
            "description": target_item.description,
            "user_id": str(target_item.user_id),
            "created_at": target_item.created_at.isoformat() + "Z",
            "updated_at": target_item.updated_at.isoformat() + "Z",
        }
        output.append(target_data)

    return jsonify(output), 200


@targets_bp.route("/<string:target_id>", methods=["GET"])
@jwt_required()
def get_target_by_id(target_id):
    """
    Endpoint untuk mendapatkan detail satu target berdasarkan ID.
    Hanya bisa diakses oleh pemilik target.
    """
    current_user_id = get_jwt_identity()
    target_item = Target.query.filter_by(id=target_id, user_id=current_user_id).first()

    if not target_item:
        # Cek apakah target ada tapi bukan milik user, atau memang tidak ada
        target_exists_for_other = Target.query.get(target_id)
        if target_exists_for_other:
            return (
                jsonify({"msg": "Anda tidak berhak mengakses target ini"}),
                403,
            )  # Forbidden
        return jsonify({"msg": "Target tidak ditemukan"}), 404  # Not Found

    return (
        jsonify(
            {
                "id": str(target_item.id),
                "name": target_item.name,
                "description": target_item.description,
                "user_id": str(target_item.user_id),
                "created_at": target_item.created_at.isoformat() + "Z",
                "updated_at": target_item.updated_at.isoformat() + "Z",
            }
        ),
        200,
    )


@targets_bp.route("/<string:target_id>", methods=["PUT"])
@jwt_required()
def update_target(target_id):
    """
    Endpoint untuk memperbarui target yang ada.
    Hanya bisa diakses oleh pemilik target.
    """
    current_user_id = get_jwt_identity()
    target_item = Target.query.filter_by(id=target_id, user_id=current_user_id).first()

    if not target_item:
        target_exists_for_other = Target.query.get(target_id)
        if target_exists_for_other:
            return jsonify({"msg": "Anda tidak berhak mengubah target ini"}), 403
        return jsonify({"msg": "Target tidak ditemukan"}), 404

    data = request.get_json()
    if not data:
        return (
            jsonify({"msg": "Request body tidak boleh kosong (JSON diperlukan)"}),
            400,
        )

    updated = False
    if "name" in data:
        new_name = data["name"]
        if (
            new_name != target_item.name
            and Target.query.filter_by(name=new_name, user_id=current_user_id).first()
        ):
            return (
                jsonify({"msg": "Anda sudah memiliki target lain dengan nama ini"}),
                409,
            )
        target_item.name = new_name
        updated = True

    if "description" in data:
        target_item.description = data.get("description")
        updated = True

    if not updated:
        return jsonify({"msg": "Tidak ada data yang diubah"}), 200

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Gagal memperbarui target", "error": str(e)}), 500

    return (
        jsonify(
            {
                "msg": "Target berhasil diperbarui",
                "target": {
                    "id": str(target_item.id),
                    "name": target_item.name,
                    "description": target_item.description,
                    "updated_at": target_item.updated_at.isoformat() + "Z",
                },
            }
        ),
        200,
    )


@targets_bp.route("/<string:target_id>", methods=["DELETE"])
@jwt_required()
def delete_target(target_id):
    """
    Endpoint untuk menghapus target.
    Hanya bisa diakses oleh pemilik target.
    Akan menghapus juga semua progress terkait (karena cascade).
    """
    current_user_id = get_jwt_identity()
    target_item = Target.query.filter_by(id=target_id, user_id=current_user_id).first()

    if not target_item:
        target_exists_for_other = Target.query.get(target_id)
        if target_exists_for_other:
            return jsonify({"msg": "Anda tidak berhak menghapus target ini"}), 403
        return jsonify({"msg": "Target tidak ditemukan"}), 404

    try:
        # Entri TargetProgress akan terhapus otomatis karena cascade pada model Target.progress_entries
        db.session.delete(target_item)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Gagal menghapus target", "error": str(e)}), 500

    return jsonify({"msg": "Target berhasil dihapus"}), 200


# --- Endpoint untuk Target Progress ---


@targets_bp.route("/<string:target_id>/progress", methods=["POST"])
@jwt_required()
def add_target_progress(target_id):
    """
    Endpoint untuk menambahkan entri progress baru ke sebuah target.
    Hanya pemilik target yang bisa menambahkan progress.
    """
    current_user_id = get_jwt_identity()
    target_item = Target.query.filter_by(id=target_id, user_id=current_user_id).first()

    if not target_item:
        return (
            jsonify(
                {"msg": "Target tidak ditemukan atau Anda tidak berhak mengaksesnya"}
            ),
            404,
        )

    data = request.get_json()
    if not data:
        return (
            jsonify({"msg": "Request body tidak boleh kosong (JSON diperlukan)"}),
            400,
        )

    status = data.get("status")
    notes = data.get("notes")
    content_id = data.get("content_id")  # Opsional: ID konten terkait
    achieved_at_str = data.get("achieved_at")  # Opsional: "YYYY-MM-DDTHH:MM:SSZ"

    if not status:
        return jsonify({"msg": "Status progress diperlukan"}), 400

    achieved_at_dt = None
    if achieved_at_str:
        try:
            # Coba parse, hilangkan 'Z' jika ada dan tambahkan info timezone jika tidak ada
            if achieved_at_str.endswith("Z"):
                achieved_at_str = achieved_at_str[:-1] + "+00:00"
            achieved_at_dt = datetime.fromisoformat(achieved_at_str)
        except ValueError:
            return (
                jsonify(
                    {
                        "msg": "Format 'achieved_at' tidak valid. Gunakan format ISO 8601 (YYYY-MM-DDTHH:MM:SSZ atau YYYY-MM-DDTHH:MM:SS+00:00)"
                    }
                ),
                400,
            )

    new_progress = TargetProgress(
        target_id=target_id,
        status=status,
        notes=notes,
        content_id=content_id,  # Bisa null
        achieved_at=achieved_at_dt,  # Bisa null
        user_id=current_user_id,  # User yang mencatat progress ini
    )

    try:
        db.session.add(new_progress)
        db.session.commit()
        progress_id_str = str(new_progress.id)
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Gagal menambahkan progress", "error": str(e)}), 500

    return (
        jsonify(
            {
                "msg": "Progress berhasil ditambahkan",
                "progress": {
                    "id": progress_id_str,
                    "target_id": new_progress.target_id,
                    "status": new_progress.status,
                    "notes": new_progress.notes,
                    "content_id": new_progress.content_id,
                    "achieved_at": (
                        new_progress.achieved_at.isoformat() + "Z"
                        if new_progress.achieved_at
                        else None
                    ),
                    "user_id": new_progress.user_id,
                    "created_at": new_progress.created_at.isoformat() + "Z",
                },
            }
        ),
        201,
    )


@targets_bp.route("/<string:target_id>/progress", methods=["GET"])
@jwt_required()
def get_target_progress_entries(target_id):
    """
    Endpoint untuk mendapatkan semua entri progress dari sebuah target.
    Hanya bisa diakses oleh pemilik target.
    """
    current_user_id = get_jwt_identity()
    target_item = Target.query.filter_by(id=target_id, user_id=current_user_id).first()

    if not target_item:
        return (
            jsonify(
                {"msg": "Target tidak ditemukan atau Anda tidak berhak mengaksesnya"}
            ),
            404,
        )

    progress_entries = (
        TargetProgress.query.filter_by(target_id=target_id)
        .order_by(TargetProgress.created_at.desc())
        .all()
    )

    output = []
    for entry in progress_entries:
        progress_data = {
            "id": str(entry.id),
            "status": entry.status,
            "notes": entry.notes,
            "content_id": str(entry.content_id) if entry.content_id else None,
            "achieved_at": (
                entry.achieved_at.isoformat() + "Z" if entry.achieved_at else None
            ),
            "user_id_recorder": str(entry.user_id),  # User yang mencatat progress
            "created_at": entry.created_at.isoformat() + "Z",
            "updated_at": entry.updated_at.isoformat() + "Z",
        }
        output.append(progress_data)

    return jsonify(output), 200


# Anda bisa menambahkan endpoint untuk GET/PUT/DELETE progress spesifik berdasarkan progress_id jika diperlukan
# Contoh: GET /progress/<progress_id>, PUT /progress/<progress_id>, DELETE /progress/<progress_id>
