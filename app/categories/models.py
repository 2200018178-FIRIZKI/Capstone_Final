# app/categories/models.py
import uuid
from datetime import datetime, timezone
from app.extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text)
    parent_id = db.Column(
        db.String(36), db.ForeignKey("categories.id"), nullable=True, index=True
    )  # Menggunakan String(36) untuk konsistensi dengan ID
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

    # Relasi untuk anak kategori (children)
    children = db.relationship(
        "Category", backref=db.backref("parent", remote_side=[id]), lazy="dynamic"
    )
    # Relasi ke content_categories (akan dibuat nanti di model Content)
    # contents = db.relationship('ContentCategory', back_populates='category', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category {self.name}>"

    # Sesuaikan tipe data kolom id dan parent_id jika Anda menggunakan UUID asli PostgreSQL di skema SQL
    # Contoh untuk UUID asli:
    # id = db.Column(db.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # parent_id = db.Column(db.dialects.postgresql.UUID(as_uuid=True), db.ForeignKey('categories.id'), nullable=True, index=True)
    # created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow) # timezone=True untuk TIMESTAMP WITH TIME ZONE
    # updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
