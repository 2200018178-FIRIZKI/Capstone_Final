# app/files/routes.py
import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from app.extensions import db
from .models import File  # Impor model File
from flask_jwt_extended import jwt_required, get_jwt_identity

files_bp = Blueprint("files_bp", __name__, url_prefix="/files")


def allowed_file(filename):
    """Memeriksa apakah ekstensi file diizinkan."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


@files_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_file_route():  # Mengganti nama fungsi agar tidak bentrok dengan impor 'upload_file'
    current_user_id = get_jwt_identity()

    if "file" not in request.files:
        return jsonify({"msg": "Tidak ada bagian 'file' dalam request"}), 400

    file_to_upload = request.files["file"]  # Mengganti nama variabel agar lebih jelas

    if file_to_upload.filename == "":
        return jsonify({"msg": "Tidak ada file yang dipilih untuk diunggah"}), 400

    if file_to_upload and allowed_file(file_to_upload.filename):
        original_filename = secure_filename(file_to_upload.filename)
        file_extension = (
            original_filename.rsplit(".", 1)[1].lower()
            if "." in original_filename
            else ""
        )
        unique_filename_on_server = (
            f"{uuid.uuid4().hex}.{file_extension}"  # Nama file di server
        )

        upload_folder_path = current_app.config["UPLOAD_FOLDER"]

        if not os.path.exists(upload_folder_path):
            try:
                os.makedirs(upload_folder_path)
            except OSError as e:
                current_app.logger.error(f"Gagal membuat folder upload: {e}")
                return (
                    jsonify(
                        {
                            "msg": "Gagal menyiapkan folder upload di server",
                            "error": str(e),
                        }
                    ),
                    500,
                )

        file_server_path = os.path.join(upload_folder_path, unique_filename_on_server)

        try:
            file_to_upload.save(file_server_path)
            file_size_on_server = os.path.getsize(file_server_path)

            new_file_entry = File(
                file_name=unique_filename_on_server,
                original_file_name=original_filename,
                file_type=file_to_upload.mimetype,
                file_size_bytes=file_size_on_server,
                storage_path=file_server_path,  # Untuk lokal, ini path di server
                user_id=current_user_id,
            )
            db.session.add(new_file_entry)
            db.session.commit()
            file_id_str = str(new_file_entry.id)

        except Exception as e:
            db.session.rollback()
            if os.path.exists(file_server_path):  # Hapus file jika gagal simpan ke DB
                try:
                    os.remove(file_server_path)
                except OSError as remove_err:
                    current_app.logger.error(
                        f"Gagal menghapus file parsial: {remove_err}"
                    )
            current_app.logger.error(f"Gagal memproses unggahan: {e}")
            return (
                jsonify(
                    {"msg": "Gagal memproses file unggahan di server", "error": str(e)}
                ),
                500,
            )

        return (
            jsonify(
                {
                    "msg": "File berhasil diunggah",
                    "file_info": {
                        "id": file_id_str,
                        "file_name_server": new_file_entry.file_name,
                        "original_file_name": new_file_entry.original_file_name,
                        "file_type": new_file_entry.file_type,
                        "file_size_bytes": new_file_entry.file_size_bytes,
                        "uploaded_at": new_file_entry.uploaded_at.isoformat() + "Z",
                        "download_url": f"/files/download/{file_id_str}",
                    },
                }
            ),
            201,
        )
    else:
        return jsonify({"msg": "Tipe file tidak diizinkan atau file tidak valid"}), 400


@files_bp.route("/download/<string:file_id>", methods=["GET"])
@jwt_required()  # Lindungi endpoint download jika perlu
def download_file_route(file_id):  # Mengganti nama fungsi
    current_user_id = get_jwt_identity()  # Untuk otorisasi jika perlu
    file_entry = File.query.get(file_id)

    if not file_entry:
        return jsonify({"msg": "File tidak ditemukan"}), 404

    # Implementasi otorisasi: Misalnya, hanya pemilik yang bisa download
    # if str(file_entry.user_id) != current_user_id:
    #     return jsonify({"msg": "Anda tidak berhak mengunduh file ini"}), 403

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    filename_on_server = file_entry.file_name  # Nama file yang disimpan di server

    try:
        return send_from_directory(
            directory=upload_folder,
            path=filename_on_server,
            as_attachment=True,
            download_name=file_entry.original_file_name,  # Nama yang dilihat pengguna saat download
        )
    except FileNotFoundError:
        current_app.logger.error(
            f"File tidak ditemukan di server: {os.path.join(upload_folder, filename_on_server)}"
        )
        return jsonify({"msg": "File fisik tidak ditemukan di server"}), 404


@files_bp.route("/<string:file_id>/info", methods=["GET"])
@jwt_required()
def get_file_info_route(file_id):  # Mengganti nama fungsi
    current_user_id = get_jwt_identity()
    file_entry = File.query.filter_by(
        id=file_id
    ).first()  # Tambahkan user_id jika info hanya untuk pemilik

    if not file_entry:
        return jsonify({"msg": "Informasi file tidak ditemukan"}), 404

    # Implementasi otorisasi: Misalnya, hanya pemilik yang bisa lihat info
    # if str(file_entry.user_id) != current_user_id:
    #     return jsonify({"msg": "Anda tidak berhak melihat informasi file ini"}), 403

    return (
        jsonify(
            {
                "id": str(file_entry.id),
                "file_name_server": file_entry.file_name,
                "original_file_name": file_entry.original_file_name,
                "file_type": file_entry.file_type,
                "file_size_bytes": file_entry.file_size_bytes,
                "uploaded_at": file_entry.uploaded_at.isoformat() + "Z",
                "user_id": str(file_entry.user_id),
                "content_id": (
                    str(file_entry.content_id) if file_entry.content_id else None
                ),
                "quality_metrics": file_entry.quality_metrics,
            }
        ),
        200,
    )
