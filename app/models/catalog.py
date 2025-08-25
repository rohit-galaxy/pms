from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Numeric, Text, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db


class Category(db.Model):
	__tablename__ = "categories"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	name: Mapped[str] = mapped_column(String(120), nullable=False)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

	products = relationship("Product", back_populates="category")
	owner = relationship("User", back_populates="categories")


class Brand(db.Model):
	__tablename__ = "brands"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	name: Mapped[str] = mapped_column(String(120), nullable=False)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

	products = relationship("Product", back_populates="brand")
	owner = relationship("User", back_populates="brands")


class Product(db.Model):
	__tablename__ = "products"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	title: Mapped[str] = mapped_column(String(200), nullable=False)
	description: Mapped[str | None] = mapped_column(Text)
	price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
	quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

	category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
	brand_id: Mapped[int | None] = mapped_column(ForeignKey("brands.id"))
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

	creator = relationship("User", back_populates="products")
	category = relationship("Category", back_populates="products")
	brand = relationship("Brand", back_populates="products")