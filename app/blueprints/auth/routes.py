from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, g
from werkzeug.security import check_password_hash
from app import get_connection
from functools import wraps


auth_bp = Blueprint("auth_bp", __name__)


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            if request.accept_mimetypes.best == "application/json" or request.is_json:
                return jsonify({"error": "Unauthorized"}), 401
            return redirect(url_for("auth_bp.login_page"))
        return view_func(*args, **kwargs)
    return wrapped


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            if request.accept_mimetypes.best == "application/json" or request.is_json:
                return jsonify({"error": "Forbidden"}), 403
            return redirect(url_for("product_bp.index"))
        return view_func(*args, **kwargs)
    return wrapped


@auth_bp.get("/login")
def login_page():
    if session.get("user_id"):
        return redirect(url_for("users_bp.index")) if session.get("is_admin") else redirect(url_for("product_bp.index"))
    return render_template("auth/login.html")


@auth_bp.post("/login")
def login_post():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    if not email or not password:
        return render_template("auth/login.html", error="Email and password are required")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, email, password_hash, is_admin FROM users WHERE email=%s AND status='1'", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return render_template("auth/login.html", error="Invalid credentials")

    session["user_id"] = user["id"]
    session["is_admin"] = bool(user["is_admin"]) if user.get("is_admin") is not None else False

    return redirect(url_for("users_bp.index")) if session["is_admin"] else redirect(url_for("product_bp.index"))


@auth_bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth_bp.login_page"))