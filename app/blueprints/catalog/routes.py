from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import select
from ...extensions import db
from ...models.catalog import Product, Category, Brand

catalog_bp = Blueprint("catalog", __name__)


def _is_admin() -> bool:
	return bool(getattr(current_user, "is_admin", False))


@catalog_bp.get("/dashboard")
@login_required
def user_dashboard():
	if _is_admin():
		return redirect(url_for("admin.dashboard"))
	products = (
		db.session.execute(
			select(Product).where(Product.user_id == current_user.id).order_by(Product.created_at.desc())
		)
		.scalars()
		.all()
	)
	return render_template("catalog/user_dashboard.html", products=products)


# Products CRUD
@catalog_bp.get("/products")
@login_required
def products_list():
	query = select(Product).order_by(Product.created_at.desc())
	if not _is_admin():
		query = query.where(Product.user_id == current_user.id)
	products = db.session.execute(query).scalars().all()
	return render_template("catalog/products_list.html", products=products, is_admin=_is_admin())


@catalog_bp.get("/products/create")
@login_required
def products_create():
	if _is_admin():
		categories = Category.query.order_by(Category.name).all()
		brands = Brand.query.order_by(Brand.name).all()
	else:
		categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
		brands = Brand.query.filter_by(user_id=current_user.id).order_by(Brand.name).all()
	return render_template("catalog/product_form.html", categories=categories, brands=brands, product=None)


@catalog_bp.post("/products/create")
@login_required
def products_create_post():
	title = request.form.get("title", "").strip()
	description = request.form.get("description", "").strip()
	price = request.form.get("price", "0")
	quantity = request.form.get("quantity", "0")
	category_id = request.form.get("category_id") or None
	brand_id = request.form.get("brand_id") or None
	if not title:
		flash("Title is required", "warning")
		return redirect(url_for("catalog.products_create"))
	# Enforce that non-admins can only select their own category/brand
	if not _is_admin():
		if category_id:
			own_cat = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
			if not own_cat:
				flash("Invalid category", "danger")
				return redirect(url_for("catalog.products_create"))
		if brand_id:
			own_brand = Brand.query.filter_by(id=brand_id, user_id=current_user.id).first()
			if not own_brand:
				flash("Invalid brand", "danger")
				return redirect(url_for("catalog.products_create"))
	product = Product(
		title=title,
		description=description or None,
		price=price or 0,
		quantity=quantity or 0,
		category_id=category_id,
		brand_id=brand_id,
		user_id=current_user.id if not _is_admin() else (request.form.get("user_id") or current_user.id),
	)
	db.session.add(product)
	db.session.commit()
	flash("Product created", "success")
	return redirect(url_for("catalog.products_list"))


@catalog_bp.get("/products/<int:product_id>/edit")
@login_required
def products_edit(product_id: int):
	product = Product.query.get_or_404(product_id)
	if not _is_admin() and product.user_id != current_user.id:
		flash("Not authorized", "danger")
		return redirect(url_for("catalog.products_list"))
	if _is_admin():
		categories = Category.query.order_by(Category.name).all()
		brands = Brand.query.order_by(Brand.name).all()
	else:
		categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
		brands = Brand.query.filter_by(user_id=current_user.id).order_by(Brand.name).all()
	return render_template("catalog/product_form.html", categories=categories, brands=brands, product=product)


@catalog_bp.post("/products/<int:product_id>/edit")
@login_required
def products_edit_post(product_id: int):
	product = Product.query.get_or_404(product_id)
	if not _is_admin() and product.user_id != current_user.id:
		flash("Not authorized", "danger")
		return redirect(url_for("catalog.products_list"))
	new_category_id = request.form.get("category_id") or None
	new_brand_id = request.form.get("brand_id") or None
	if not _is_admin():
		if new_category_id:
			own_cat = Category.query.filter_by(id=new_category_id, user_id=current_user.id).first()
			if not own_cat:
				flash("Invalid category", "danger")
				return redirect(url_for("catalog.products_edit", product_id=product.id))
		if new_brand_id:
			own_brand = Brand.query.filter_by(id=new_brand_id, user_id=current_user.id).first()
			if not own_brand:
				flash("Invalid brand", "danger")
				return redirect(url_for("catalog.products_edit", product_id=product.id))
	product.title = request.form.get("title", product.title)
	product.description = request.form.get("description", product.description)
	product.price = request.form.get("price", product.price)
	product.quantity = request.form.get("quantity", product.quantity)
	product.category_id = new_category_id
	product.brand_id = new_brand_id
	db.session.commit()
	flash("Product updated", "success")
	return redirect(url_for("catalog.products_list"))


@catalog_bp.post("/products/<int:product_id>/delete")
@login_required
def products_delete(product_id: int):
	product = Product.query.get_or_404(product_id)
	if not _is_admin() and product.user_id != current_user.id:
		flash("Not authorized", "danger")
		return redirect(url_for("catalog.products_list"))
	db.session.delete(product)
	db.session.commit()
	flash("Product deleted", "success")
	return redirect(url_for("catalog.products_list"))


# Categories CRUD
@catalog_bp.get("/categories")
@login_required
def categories_list():
	query = Category.query
	if not _is_admin():
		query = query.filter_by(user_id=current_user.id)
	categories = query.order_by(Category.name).all()
	return render_template("catalog/categories_list.html", categories=categories)


@catalog_bp.post("/categories/create")
@login_required
def categories_create_post():
	name = request.form.get("name", "").strip()
	if not name:
		flash("Name is required", "warning")
		return redirect(url_for("catalog.categories_list"))
	# Prevent duplicate per user (or globally for admin if desired)
	exists = Category.query.filter_by(name=name, user_id=current_user.id if not _is_admin() else current_user.id).first()
	if exists:
		flash("Category already exists", "danger")
		return redirect(url_for("catalog.categories_list"))
	cat = Category(name=name, user_id=current_user.id)
	db.session.add(cat)
	db.session.commit()
	flash("Category created", "success")
	return redirect(url_for("catalog.categories_list"))


@catalog_bp.post("/categories/<int:category_id>/delete")
@login_required
def categories_delete(category_id: int):
	cat = Category.query.get_or_404(category_id)
	if not _is_admin() and cat.user_id != current_user.id:
		flash("Not authorized", "danger")
		return redirect(url_for("catalog.categories_list"))
	db.session.delete(cat)
	db.session.commit()
	flash("Category deleted", "success")
	return redirect(url_for("catalog.categories_list"))


# Brands CRUD
@catalog_bp.get("/brands")
@login_required
def brands_list():
	query = Brand.query
	if not _is_admin():
		query = query.filter_by(user_id=current_user.id)
	brands = query.order_by(Brand.name).all()
	return render_template("catalog/brands_list.html", brands=brands)


@catalog_bp.post("/brands/create")
@login_required
def brands_create_post():
	name = request.form.get("name", "").strip()
	if not name:
		flash("Name is required", "warning")
		return redirect(url_for("catalog.brands_list"))
	exists = Brand.query.filter_by(name=name, user_id=current_user.id if not _is_admin() else current_user.id).first()
	if exists:
		flash("Brand already exists", "danger")
		return redirect(url_for("catalog.brands_list"))
	b = Brand(name=name, user_id=current_user.id)
	db.session.add(b)
	db.session.commit()
	flash("Brand created", "success")
	return redirect(url_for("catalog.brands_list"))


@catalog_bp.post("/brands/<int:brand_id>/delete")
@login_required
def brands_delete(brand_id: int):
	b = Brand.query.get_or_404(brand_id)
	if not _is_admin() and b.user_id != current_user.id:
		flash("Not authorized", "danger")
		return redirect(url_for("catalog.brands_list"))
	db.session.delete(b)
	db.session.commit()
	flash("Brand deleted", "success")
	return redirect(url_for("catalog.brands_list"))