from flask import Blueprint, render_template, request, jsonify
from app.models.brand import (
    fetch_all_brands, fetch_brand_by_id, create_brand, update_brand,
    toggle_brand_status, soft_delete_brand, fetch_brands_by_category
)
from app.models.category import fetch_active_categories

brand_bp = Blueprint('brand_bp', __name__)

@brand_bp.route("/brands")
def brands():
    brands = fetch_all_brands()
    categories = fetch_active_categories()
    return render_template("brand.html", brands=brands, categories=categories)

@brand_bp.route("/brand/get/<int:id>", methods=["GET"])
def get_brand(id):
    brand = fetch_brand_by_id(id)
    if brand:
        return jsonify(brand)
    return jsonify({"error": "Brand not found"}), 404

@brand_bp.route("/brand/create", methods=["POST"])
def create():
    name = request.form.get("name").strip()
    category_id = request.form.get("category_id")
    if not name or not category_id:
        return jsonify({"success": False, "message": "Name and category are required."}), 400
    new_id = create_brand(name, category_id)
    if new_id is None:
        return jsonify({"success": False, "message": "This brand already exists in the selected category."}), 409
    return jsonify({"success": True, "id": new_id, "message": "Brand created successfully."})

@brand_bp.route("/brand/update/<int:id>", methods=["POST"])
def update(id):
    name = request.form.get("name").strip()
    category_id = request.form.get("category_id")
    if not name or not category_id:
        return jsonify({"success": False, "message": "Name and category are required."}), 400
    success = update_brand(id, name, category_id)
    if not success:
        return jsonify({"success": False, "message": "This brand already exists in the selected category."}), 409
    return jsonify({"success": True, "message": "Brand updated successfully."})

@brand_bp.route("/brand/toggle-status/<int:id>", methods=["POST"])
def toggle_status(id):
    new_status = toggle_brand_status(id)
    if new_status is None:
        return jsonify({"success": False, "message": "Brand not found"}), 404
    return jsonify({"success": True, "status": new_status})

@brand_bp.route("/brand/delete/<int:id>", methods=["POST"])
def delete(id):
    soft_delete_brand(id)
    return jsonify({"success": True, "message": "Brand deleted (soft delete)."})

@brand_bp.route("/brands/<int:category_id>")
def get_brands(category_id):
    brands = fetch_brands_by_category(category_id)
    return jsonify(brands)
