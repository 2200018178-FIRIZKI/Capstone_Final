# app/contents/models.py
import uuid
from datetime import datetime, timezone
from app.extensions import db


class Content(db.Model):
    __tablename__ = "contents"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False, index=True)
    content_type = db.Column(db.String(50), nullable=False, index=True)
    data_url = db.Column(db.Text)
    metadata_tags = db.Column(db.JSON)  # Menggunakan db.JSON untuk JSONB di PostgreSQL
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.id"), nullable=False
    )  # Relasi ke tabel users
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

    # Relasi ke user (author)
    author = db.relationship("User", backref=db.backref("contents", lazy="dynamic"))
    # Relasi ke content_categories
    categories_assoc = db.relationship(
        "ContentCategory", back_populates="content", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Content {self.title}>"


# Tabel asosiasi untuk relasi many-to-many antara Content dan Category
class ContentCategory(db.Model):
    __tablename__ = "content_categories"

    content_id = db.Column(
        db.String(36), db.ForeignKey("contents.id"), primary_key=True
    )
    category_id = db.Column(
        db.String(36), db.ForeignKey("categories.id"), primary_key=True
    )
    assigned_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Definisikan relasi kembali ke Content dan Category
    content = db.relationship("Content", back_populates="categories_assoc")
    category = db.relationship(
        "Category",
        backref=db.backref(
            "contents_assoc", lazy="dynamic", cascade="all, delete-orphan"
        ),
    )

    def __repr__(self):
        return f"<ContentCategory content_id={self.content_id} category_id={self.category_id}>"

    # Sesuaikan tipe data kolom id dan foreign key jika Anda menggunakan UUID asli PostgreSQL
    # Contoh untuk UUID asli:
    # id = db.Column(db.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # user_id = db.Column(db.dialects.postgresql.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    # content_id = db.Column(db.dialects.postgresql.UUID(as_uuid=True), db.ForeignKey('contents.id'), primary_key=True)
    # category_id = db.Column(db.dialects.postgresql.UUID(as_uuid=True), db.ForeignKey('categories.id'), primary_key=True)
    # created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    # updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    # assigned_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
