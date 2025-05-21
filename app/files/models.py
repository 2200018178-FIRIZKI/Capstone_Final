import uuid
from datetime import datetime, timezone
from app.extensions import db


class File(db.Model):
    __tablename__ = "files"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name = db.Column(
        db.String(255), nullable=False, index=True
    )  # Nama file yang disimpan (bisa di-generate unik)
    original_file_name = db.Column(db.String(255))  # Nama file asli dari pengguna
    file_type = db.Column(db.String(100), nullable=False, index=True)  # MIME type
    file_size_bytes = db.Column(db.BigInteger, nullable=False)
    storage_path = db.Column(
        db.String(512), nullable=False
    )  # Path atau key di cloud storage
    quality_metrics = db.Column(db.JSON)  # Metrik kualitas
    content_id = db.Column(
        db.String(36), db.ForeignKey("contents.id"), nullable=True
    )  # Relasi opsional ke konten
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.id"), nullable=False
    )  # Pengguna yang mengunggah
    uploaded_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relasi ke user
    uploader = db.relationship(
        "User", backref=db.backref("uploaded_files", lazy="dynamic")
    )
    # Relasi ke content (jika file ini adalah bagian dari konten)
    content = db.relationship(
        "Content", backref=db.backref("associated_files", lazy="dynamic")
    )

    def __repr__(self):
        return f"<File {self.original_file_name or self.file_name}>"
