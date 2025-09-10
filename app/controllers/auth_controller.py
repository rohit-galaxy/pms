import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.models.user import authenticate_user, fetch_user_by_email,fetch_user_by_id
auth_bp = Blueprint('auth_bp', __name__)

# -------------------- Login --------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get('is_authenticated'):
        # Redirect based on is_admin flag
        if session.get('is_admin', False):
            return redirect(url_for('user_bp.index'))
        else:
            return redirect(url_for('product_bp.index'))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        user = authenticate_user(email, password)

        if user:
            session.clear()
            session['user_id'] = user['id']
            session['is_admin'] = bool(user.get('is_admin', 0))
            session['is_authenticated'] = True

            flash("Login successful!", "success")
            return redirect(
                url_for('user_bp.index') if session['is_admin'] else url_for('product_bp.index')
            )
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html")

# -------------------- Logout --------------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('auth_bp.login'))

# -------------------- Check Email --------------------
@auth_bp.route("/check-email", methods=["GET"])
def check_email():
    email = request.args.get("email", "").strip()
    exclude_id = request.args.get("exclude_id", default=None, type=int)

    if not email:
        return jsonify({"exists": False})

    user = fetch_user_by_email(email)
    exists = user is not None and (not exclude_id or user['id'] != exclude_id)
    return jsonify({"exists": exists})
@auth_bp.route("/validate-old-password", methods=["POST"])
def validate_old_password():
    if not session.get("is_authenticated"):
        return jsonify({"valid": False})

    user_id = session.get("user_id")
    old_password = request.form.get("old_password", "").strip()

    user = fetch_user_by_id(user_id)
    if not user or not old_password:
        return jsonify({"valid": False})

    stored_password = user["password"]
    is_valid = bcrypt.checkpw(old_password.encode("utf-8"), stored_password.encode("utf-8"))

    return jsonify({"valid": is_valid})

@auth_bp.route("/validate-login", methods=["POST"])
def validate_login():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    user = authenticate_user(email, password)
    return jsonify({"valid": user is not None})
