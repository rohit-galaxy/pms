from flask import Blueprint, render_template, request, jsonify, session
from app.models.brand import (
    fetch_all_brands, fetch_brand_by_id, create_brand, update_brand,
    toggle_brand_status, soft_delete_brand, fetch_brands_by_category,
    check_brand_name_exists
)
from app.models.category import fetch_active_categories

brand_bp = Blueprint('brand_bp', __name__)

@brand_bp.route("/")
def brands():
    brands = fetch_all_brands()
    categories = fetch_active_categories()
    return render_template("brand.html", brands=brands, categories=categories)

@brand_bp.route("/get/<int:id>")
def get_brand(id):
    brand = fetch_brand_by_id(id)
    if brand:
        return jsonify(brand)
    return jsonify({"error": "Brand not found"}), 404

@brand_bp.route("/create", methods=["POST"])
def create():
    name = request.form.get("name", "").strip()
    category_id = request.form.get("category_id")
    if not name or not category_id:
        return jsonify({"success": False, "message": "Name and category are required."}), 400
    if check_brand_name_exists(name, category_id):
        return jsonify({"success": False, "message": "This brand already exists in the selected category."}), 409

    new_id = create_brand(name, category_id)
    if new_id is None:
        return jsonify({"success": False, "message": "This brand already exists in the selected category."}), 409
    return jsonify({"success": True, "id": new_id, "message": "Brand created successfully."})

@brand_bp.route("/update/<int:id>", methods=["POST"])
def update(id):
    name = request.form.get("name", "").strip()
    category_id = request.form.get("category_id")
    if not name or not category_id:
        return jsonify({"success": False, "message": "Name and category are required."}), 400
    if check_brand_name_exists(name, category_id, id):
        return jsonify({"success": False, "message": "This brand already exists in the selected category."}), 409

    success = update_brand(id, name, category_id)
    if not success:
        return jsonify({"success": False, "message": "Brand not found or unauthorized."}), 404
    return jsonify({"success": True, "message": "Brand updated successfully."})

@brand_bp.route("/toggle-status/<int:id>", methods=["POST"])
def toggle_status(id):
    new_status = toggle_brand_status(id)
    if new_status is None:
        return jsonify({"success": False, "message": "Brand not found or unauthorized"}), 404
    return jsonify({"success": True, "status": new_status})

@brand_bp.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    soft_delete_brand(id)
    return jsonify({"success": True, "message": "Brand deleted successfully."})

@brand_bp.route("/brands/<int:category_id>")
def get_brands(category_id):
    brands = fetch_brands_by_category(category_id)
    return jsonify(brands)

@brand_bp.route("/check-name")
def check_name():
    name = request.args.get("name", "").strip()
    category_id = request.args.get("category_id")
    exclude_id = request.args.get("exclude_id", default=None, type=int)
    if not name or not category_id:
        return jsonify({"exists": False})
    exists = check_brand_name_exists(name, category_id, exclude_id)
    return jsonify({"exists": exists})
