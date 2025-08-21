from flask import Blueprint, render_template, request, jsonify
from app.models.category import (
    fetch_all_categories, fetch_category_by_id, create_category,
    update_category, toggle_category_status, soft_delete_category
)

category_bp = Blueprint('category_bp', __name__)

@category_bp.route("/categories")
def categories():
    categories = fetch_all_categories()
    return render_template("category.html", categories=categories)

@category_bp.route("/category/get/<int:id>", methods=["GET"])
def get_category(id):
    category = fetch_category_by_id(id)
    if category:
        return jsonify(category)
    return jsonify({"error": "Category not found"}), 404

@category_bp.route("/category/create", methods=["POST"])
def create():
    name = request.form.get("name")
    if not name:
        return jsonify({"success": False, "message": "Name is required."}), 400
    create_category(name)
    return jsonify({"success": True, "message": "Category created successfully."})

@category_bp.route("/category/update/<int:id>", methods=["POST"])
def update(id):
    name = request.form.get("name")
    if not name:
        return jsonify({"success": False, "message": "Name is required."}), 400
    update_category(id, name)
    return jsonify({"success": True, "message": "Category updated successfully."})

@category_bp.route("/category/toggle-status/<int:id>", methods=["POST"])
def toggle_status(id):
    new_status = toggle_category_status(id)
    if new_status is None:
        return jsonify({"success": False, "message": "Category not found"}), 404
    return jsonify({"success": True, "status": new_status})

@category_bp.route("/category/delete/<int:id>", methods=["POST"])
def delete(id):
    soft_delete_category(id)
    return jsonify({"success": True, "message": "Category deleted (soft delete)."})
