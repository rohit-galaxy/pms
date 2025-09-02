from flask import Blueprint, render_template, request, jsonify
from app.models.category import (
    fetch_all_categories, fetch_category_by_id, create_category, update_category,
    toggle_category_status, soft_delete_category, check_category_name_exists
)

category_bp = Blueprint("category_bp", __name__, url_prefix="/categories")

@category_bp.route("/")
def categories():
    categories = fetch_all_categories()
    return render_template("category.html", categories=categories)

@category_bp.route("/get/<int:id>")
def get_category(id):
    category = fetch_category_by_id(id)
    if category:
        return jsonify(category)
    return jsonify({"error": "Category not found"}), 404

@category_bp.route("/create", methods=["POST"])
def create():
    name = request.form.get("name", "").strip()
    if not name:
        return jsonify({"success": False, "message": "Name is required."}), 400
    if check_category_name_exists(name):
        return jsonify({"success": False, "message": "Category already exists."}), 409
    new_id = create_category(name)
    return jsonify({
        "success": True,
        "id": new_id,
        "status": "1",
        "message": "Category created successfully."
    })

@category_bp.route("/update/<int:id>", methods=["POST"])
def update(id):
    name = request.form.get("name", "").strip()
    if not name:
        return jsonify({"success": False, "message": "Name is required."}), 400
    if check_category_name_exists(name, exclude_id=id):
        return jsonify({"success": False, "message": "Category already exists."}), 409
    success = update_category(id, name)
    if not success:
        return jsonify({"success": False, "message": "Category not found"}), 404
    return jsonify({"success": True, "message": "Category updated successfully."})

@category_bp.route("/toggle-status/<int:id>", methods=["POST"])
def toggle_status(id):
    new_status = toggle_category_status(id)
    if new_status is None:
        return jsonify({"success": False, "message": "Category not found"}), 404
    return jsonify({"success": True, "status": new_status})

@category_bp.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    success = soft_delete_category(id)
    if not success:
        return jsonify({"success": False, "message": "Category not found"}), 404
    return jsonify({"success": True, "message": "Category deleted successfully."})

@category_bp.route("/check-name", methods=["GET"])
def check_name():
    name = request.args.get("name", "").strip()
    exclude_id = request.args.get("exclude_id", default=None, type=int)
    exists = check_category_name_exists(name, exclude_id)
    return jsonify({"exists": exists})
