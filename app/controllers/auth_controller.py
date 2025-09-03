from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.models.user import authenticate_user, fetch_user_by_email, update_user_password, fetch_user_by_id

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
    flash("You have been logged out.", "info")
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
    if not user:
        return jsonify({"valid": False})

    stored_password = user["password"]
    is_valid = (old_password == stored_password)  # since you’re not hashing yet

    return jsonify({"valid": is_valid})


# -------------------- Change Password --------------------
@auth_bp.route("/change-password", methods=["POST"])
def change_password():
    if not session.get("is_authenticated"):
        flash("Unauthorized action.", "danger")
        return redirect(url_for("auth_bp.login"))

    user_id = session.get("user_id")
    old_password = request.form.get("old_password", "").strip()
    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()

    user = fetch_user_by_id(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("auth_bp.login"))

    # validate old password (only if changing own password)
    if str(user["id"]) == str(user_id) and old_password != user["password"]:
        flash("Old password is incorrect.", "danger")
        return redirect(url_for("user_bp.users"))

    if new_password != confirm_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for("user_bp.users"))

    success = update_user_password(user_id, new_password)
    if success:
        flash("Password updated successfully.", "success")
    else:
        flash("Password update failed.", "danger")

    return redirect(url_for("user_bp.users"))