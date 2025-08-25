from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db, login_manager


class User(db.Model, UserMixin):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	first_name: Mapped[str] = mapped_column(String(100), nullable=False)
	last_name: Mapped[str] = mapped_column(String(100), nullable=False)
	email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
	password: Mapped[str] = mapped_column(String(255), nullable=False, default="123456")
	is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

	products = relationship("Product", back_populates="creator", cascade="all, delete-orphan")
	categories = relationship("Category", back_populates="owner", cascade="all, delete-orphan")
	brands = relationship("Brand", back_populates="owner", cascade="all, delete-orphan")

	def get_full_name(self) -> str:
		return f"{self.first_name} {self.last_name}"

	@property
	def is_super_admin(self) -> bool:
		return bool(self.is_admin)


@login_manager.user_loader
def load_user(user_id: str):
	return User.query.get(int(user_id))