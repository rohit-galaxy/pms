from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.models.user import authenticate_user, fetch_user_by_email, update_user_password

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get('is_authenticated'):
        if session.get('is_admin', False):
            return redirect(url_for('user_bp.index'))
        else:
            return redirect(url_for('product_bp.index'))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = authenticate_user(email, password)
        if user:
            session.clear()
            session['user_id'] = user['id']
            session['is_admin'] = user.get('is_admin', 0) == 1
            session['role'] = 'admin' if session['is_admin'] else 'user'
            session['is_authenticated'] = True
            flash("Login successful!", "success")
            if session['is_admin']:
                return redirect(url_for('user_bp.index'))
            else:
                return redirect(url_for('product_bp.index'))
        else:
            flash("Invalid email or password.", "danger")
    print("SESSION AFTER LOGIN:", dict(session))

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth_bp.login'))

@auth_bp.route("/check-email", methods=["GET"])
def check_email():
    email = request.args.get("email", "").strip()
    exclude_id = request.args.get("exclude_id", default=None, type=int)
    if not email:
        return jsonify({"exists": False})
    user = fetch_user_by_email(email)
    exists = user is not None and (not exclude_id or user['id'] != exclude_id)
    return jsonify({"exists": exists})

@auth_bp.route("/change-password", methods=["POST"])
def change_password():
    if not session.get("is_authenticated"):
        flash("You need to log in first.", "danger")
        return redirect(url_for("auth_bp.login"))

    user_id = session["user_id"]
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if new_password != confirm_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for("user_bp.index"))

    success, message = update_user_password(user_id, old_password, new_password)
    flash(message, "success" if success else "danger")
    return redirect(url_for("user_bp.index"))
