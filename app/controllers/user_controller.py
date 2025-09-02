from flask import Blueprint, render_template, request, jsonify, session
from app.models.user import (
    fetch_all_users, fetch_user_by_id, create_user, update_user,
    toggle_user_status, soft_delete_user, check_email_exists,
    update_user_password, authenticate_user
)
from app import role_required, login_required

user_bp = Blueprint('user_bp', __name__)

# Admin: List all users
@user_bp.route("/")
@role_required('admin')
def index():
    users = fetch_all_users()
    return render_template("users.html", users=users)

# Admin: Get single user
@user_bp.route("/get/<int:id>", methods=["GET"])
@role_required('admin')
def get_user(id):
    user = fetch_user_by_id(id)
    if user:
        user.pop('password', None)  # don’t expose password
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

# Admin: Create user
@user_bp.route("/create", methods=["POST"])
@role_required('admin')
def create():
    email = request.form.get("email")
    password = request.form.get("password")
    is_admin_flag = request.form.get("is_admin", "0")  # Expect "1" or "0"

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    is_admin = 1 if is_admin_flag in ['1', 'true', 'on'] else 0

    if check_email_exists(email):
        return jsonify({"success": False, "message": "Email already exists."}), 409

    new_id = create_user(email, password, is_admin)
    return jsonify({"success": True, "id": new_id, "message": "User created successfully."})

# Admin: Update user (password optional)
@user_bp.route("/update/<int:id>", methods=["POST"])
@role_required('admin')
def update(id):
    email = request.form.get("email")
    is_admin_flag = request.form.get("is_admin", "0")  # checkboxes send "on" or "1"
    password = request.form.get("password", None)  # Optional

    if not email:
        return jsonify({"success": False, "message": "Email is required."}), 400

    is_admin = 1 if is_admin_flag in ['1', 'true', 'on'] else 0

    if check_email_exists(email, exclude_id=id):
        return jsonify({"success": False, "message": "Email already exists."}), 409

    success = update_user(id, email, password, is_admin)
    return jsonify({"success": success, "message": "User updated successfully."})

# Admin: Toggle user active/inactive
@user_bp.route("/toggle-status/<int:id>", methods=["POST"])
@role_required('admin')
def toggle_status(id):
    new_status = toggle_user_status(id)
    if new_status is None:
        return jsonify({"success": False, "message": "User not found"}), 404
    return jsonify({"success": True, "status": new_status})

# Admin: Soft delete user
@user_bp.route("/delete/<int:id>", methods=["POST"])
@role_required('admin')
def delete(id):
    soft_delete_user(id)
    return jsonify({"success": True, "message": "User deleted successfully."})

# User + Admin: Change own password
@user_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    user_id = session.get("user_id")
    old_password = request.form.get("old_password", "").strip()
    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()

    if not old_password or not new_password or not confirm_password:
        return jsonify({"success": False, "message": "All fields are required."}), 400

    if new_password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match."}), 400

    success, message = update_user_password(user_id, old_password, new_password)
    if not success:
        return jsonify({"success": False, "message": message}), 400

    return jsonify({"success": True, "message": message})
