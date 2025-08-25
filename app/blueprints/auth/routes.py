from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from ...extensions import db, bcrypt
from ...models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/login")
def login():
	if current_user.is_authenticated:
		return redirect(url_for("index"))
	return render_template("auth/login.html")


@auth_bp.post("/login")
def login_post():
	email = request.form.get("email", "").strip().lower()
	password = request.form.get("password", "")
	user = User.query.filter_by(email=email).first()
	if not user:
		flash("Invalid credentials", "danger")
		return redirect(url_for("auth.login"))

	# Initially allow plaintext '123456' match; later switch to hash check
	if user.password == password or bcrypt.check_password_hash(user.password, password):
		login_user(user)
		if user.is_admin:
			return redirect(url_for("admin.dashboard"))
		return redirect(url_for("catalog.user_dashboard"))

	flash("Invalid credentials", "danger")
	return redirect(url_for("auth.login"))


@auth_bp.get("/register")
@login_required
def register():
	# Only Super Admin can create other Super Admins or Users
	if not current_user.is_admin:
		flash("Not authorized", "danger")
		return redirect(url_for("catalog.user_dashboard"))
	return render_template("auth/register.html")


@auth_bp.post("/register")
@login_required
def register_post():
	if not current_user.is_admin:
		flash("Not authorized", "danger")
		return redirect(url_for("catalog.user_dashboard"))

	first_name = request.form.get("first_name", "").strip()
	last_name = request.form.get("last_name", "").strip()
	email = request.form.get("email", "").strip().lower()
	is_admin = request.form.get("is_admin") == "1"

	if not first_name or not last_name or not email:
		flash("All fields are required", "warning")
		return redirect(url_for("auth.register"))

	exists = User.query.filter_by(email=email).first()
	if exists:
		flash("Email already exists", "danger")
		return redirect(url_for("auth.register"))

	# Placeholder default password; later we will hash properly
	default_password = "123456"
	# Optionally store a hash now so we are future-proof
	hashed = bcrypt.generate_password_hash(default_password).decode()
	new_user = User(
		first_name=first_name,
		last_name=last_name,
		email=email,
		password=hashed,  # store hashed but also accept plaintext during login as per requirement
		is_admin=is_admin,
	)
	db.session.add(new_user)
	db.session.commit()
	flash("User created with default password 123456", "success")
	return redirect(url_for("admin.users"))


@auth_bp.post("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for("auth.login"))