# app/targets/models.py
import uuid
from datetime import datetime, timezone
from app.extensions import db


class Target(db.Model):
    __tablename__ = "targets"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.id"), nullable=False
    )  # Pengguna yang membuat target
    created_at = db.Column(
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

    # Relasi ke user (creator)
    creator = db.relationship(
        "User", backref=db.backref("created_targets", lazy="dynamic")
    )
    # Relasi ke progress
    progress_entries = db.relationship(
        "TargetProgress", backref="target", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Target {self.name}>"


class TargetProgress(db.Model):
    __tablename__ = "target_progress"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    target_id = db.Column(
        db.String(36), db.ForeignKey("targets.id"), nullable=False, index=True
    )
    content_id = db.Column(
        db.String(36), db.ForeignKey("contents.id"), nullable=True
    )  # Konten terkait (opsional)
    status = db.Column(db.String(100), nullable=False, index=True)
    notes = db.Column(db.Text)
    achieved_at = db.Column(
        db.DateTime(timezone=True), nullable=True
    )  # Waktu pencapaian
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.id"), nullable=False
    )  # Pengguna yang mencatat progres
    created_at = db.Column(
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

    # Relasi ke user (yang mencatat)
    recorder = db.relationship(
        "User", backref=db.backref("recorded_progress", lazy="dynamic")
    )
    # Relasi ke content (jika ada)
    associated_content = db.relationship(
        "Content", backref=db.backref("related_progress_entries", lazy="dynamic")
    )

    def __repr__(self):
        return f"<TargetProgress {self.id} for Target {self.target_id}>"
