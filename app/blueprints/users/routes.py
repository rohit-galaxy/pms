from flask import Blueprint, request, jsonify, render_template
from app import get_connection
from app.blueprints.auth.routes import login_required, admin_required
from werkzeug.security import generate_password_hash


users_bp = Blueprint("users_bp", __name__)


@users_bp.get("/")
@login_required
@admin_required
def index():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, is_admin, status FROM users WHERE status != '2' ORDER BY created_at DESC")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("users/index.html", users=users)


@users_bp.post("/create")
@login_required
@admin_required
def create_user():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    is_admin = 1 if request.form.get("is_admin") in ("1", "true", "on") else 0
    if not name or not email or not password:
        return jsonify({"success": False, "message": "Name, email, password required"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM users WHERE email=%s AND status != '2'", (email,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": "Email already exists"}), 409

    cursor = conn.cursor()
    hash_ = generate_password_hash(password)
    cursor.execute("INSERT INTO users (name, email, password_hash, is_admin, status) VALUES (%s, %s, %s, %s, '1')", (name, email, hash_, is_admin))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"success": True, "id": new_id})


@users_bp.post("/update/<int:user_id>")
@login_required
@admin_required
def update_user(user_id: int):
    name = request.form.get("name", "").strip()
    is_admin = 1 if request.form.get("is_admin") in ("1", "true", "on") else 0
    if not name:
        return jsonify({"success": False, "message": "Name required"}), 400
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name=%s, is_admin=%s WHERE id=%s", (name, is_admin, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@users_bp.post("/reset-password/<int:user_id>")
@login_required
@admin_required
def reset_password(user_id: int):
    password = request.form.get("password", "")
    if not password:
        return jsonify({"success": False, "message": "Password required"}), 400
    conn = get_connection()
    cursor = conn.cursor()
    hash_ = generate_password_hash(password)
    cursor.execute("UPDATE users SET password_hash=%s WHERE id=%s", (hash_, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@users_bp.post("/toggle-status/<int:user_id>")
@login_required
@admin_required
def toggle_status(user_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT status FROM users WHERE id=%s", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": "User not found"}), 404
    new_status = '0' if row['status'] == '1' else '1'
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status=%s WHERE id=%s", (new_status, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True, "status": new_status})


@users_bp.post("/delete/<int:user_id>")
@login_required
@admin_required
def delete_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status='2' WHERE id=%s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})