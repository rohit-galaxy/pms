from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import select
from ...extensions import db
from ...models.user import User
from ...models.catalog import Product

admin_bp = Blueprint("admin", __name__)


def _require_admin():
	if not current_user.is_authenticated or not current_user.is_admin:
		flash("Not authorized", "danger")
		return False
	return True


@admin_bp.get("/dashboard")
@login_required
def dashboard():
	if not _require_admin():
		return redirect(url_for("catalog.user_dashboard"))
	stats = {
		"total_users": db.session.execute(select(User).order_by(User.id)).scalars().count() if False else User.query.count(),
		"total_products": Product.query.count(),
	}
	return render_template("admin/dashboard.html", stats=stats)


@admin_bp.get("/users")
@login_required
def users():
	if not _require_admin():
		return redirect(url_for("catalog.user_dashboard"))
	users = User.query.order_by(User.created_at.desc()).all()
	return render_template("admin/users.html", users=users)


@admin_bp.get("/products")
@login_required
def products():
	if not _require_admin():
		return redirect(url_for("catalog.user_dashboard"))
	products = Product.query.order_by(Product.created_at.desc()).all()
	return render_template("admin/products.html", products=products)