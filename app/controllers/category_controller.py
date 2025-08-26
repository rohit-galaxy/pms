from flask import Blueprint, render_template, request, jsonify, g
from app.models.category import (
    fetch_all_categories, fetch_category_by_id, create_category,
    update_category, toggle_category_status, soft_delete_category,
    fetch_active_categories
)
from app.blueprints.auth.routes import login_required

category_bp = Blueprint('category_bp', __name__)

@category_bp.route("/categories")
@login_required
def categories():
	categories = fetch_all_categories(g.current_user_id, g.current_user_is_admin)
	return render_template("category.html", categories=categories)

@category_bp.route("/category/get/<int:id>", methods=["GET"])
@login_required
def get_category(id):
	category = fetch_category_by_id(id, g.current_user_id, g.current_user_is_admin)
	if category:
		return jsonify(category)
	return jsonify({"error": "Category not found"}), 404

@category_bp.route("/category/create", methods=["POST"])
@login_required
def create():
	name = request.form.get("name")
	if not name:
		return jsonify({"success": False, "message": "Name is required."}), 400
	create_category(name, g.current_user_id)
	return jsonify({"success": True, "message": "Category created successfully."})

@category_bp.route("/category/update/<int:id>", methods=["POST"])
@login_required
def update(id):
	name = request.form.get("name")
	if not name:
		return jsonify({"success": False, "message": "Name is required."}), 400
	success = update_category(id, name, g.current_user_id, g.current_user_is_admin)
	if not success:
		return jsonify({"success": False, "message": "Category not found or not permitted"}), 404
	return jsonify({"success": True, "message": "Category updated successfully."})

@category_bp.route("/category/toggle-status/<int:id>", methods=["POST"])
@login_required
def toggle_status(id):
	new_status = toggle_category_status(id, g.current_user_id, g.current_user_is_admin)
	if new_status is None:
		return jsonify({"success": False, "message": "Category not found"}), 404
	return jsonify({"success": True, "status": new_status})

@category_bp.route("/category/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
	success = soft_delete_category(id, g.current_user_id, g.current_user_is_admin)
	if not success:
		return jsonify({"success": False, "message": "Category not found"}), 404
	return jsonify({"success": True, "message": "Category deleted successfully."})
