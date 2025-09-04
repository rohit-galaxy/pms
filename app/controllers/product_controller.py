from flask import Blueprint, render_template, request, jsonify, current_app
from app.models.product import (
    fetch_all_products, fetch_product_by_id, create_product,
    update_product, toggle_product_status, soft_delete_product,
    check_product_name_exists
)
from app.models.category import fetch_active_categories
from app.models.brand import fetch_brands_by_category

product_bp = Blueprint('product_bp', __name__)

@product_bp.route("/")
def index():
    categories = fetch_active_categories()
    products = fetch_all_products()
    return render_template("product.html", categories=categories, products=products)

@product_bp.route("/get/<int:id>")
def get_product(id):
    product = fetch_product_by_id(id)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

@product_bp.route("/create", methods=["POST"])
def create():
    name = request.form.get("name")
    # product_code is NOT read from the form; will be created server-side
    category_id = request.form.get("category_id")
    brand_id = request.form.get("brand_id")
    file = request.files.get("image")

    if not name or not category_id or not brand_id:
        return jsonify({"success": False, "message": "Please fill all required fields."}), 400

    # product_code generation is handled internally
    new_id = create_product(name, category_id, brand_id, None, file, current_app)
    return jsonify({"success": True, "id": new_id, "message": "Product created successfully."})

@product_bp.route("/update/<int:id>", methods=["POST"])
def update(id):
    name = request.form.get("name")
    category_id = request.form.get("category_id")
    brand_id = request.form.get("brand_id")
    file = request.files.get("image")

    if not name or not category_id or not brand_id:
        return jsonify({"success": False, "message": "Please fill all required fields."}), 400

    success = update_product(id, name, category_id, brand_id, file, current_app)
    if not success:
        return jsonify({"success": False, "message": "Product not found or unauthorized."}), 404
    return jsonify({"success": True, "message": "Product updated successfully."})

@product_bp.route("/toggle-status/<int:id>", methods=["POST"])
def toggle_status(id):
    new_status = toggle_product_status(id)
    if new_status is None:
        return jsonify({"success": False, "message": "Product not found or unauthorized"}), 404
    return jsonify({"success": True, "status": new_status})

@product_bp.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    soft_delete_product(id)
    return jsonify({"success": True, "message": "Product deleted successfully."})

@product_bp.route("/check-name", methods=["GET"])
def check_product_name():
    name = request.args.get("name", "").strip()
    exclude_id = request.args.get("exclude_id", default=None, type=int)
    if not name:
        return jsonify({"exists": False})
    exists = check_product_name_exists(name, exclude_id)
    return jsonify({"exists": exists})

@product_bp.route("/brands/<int:category_id>")
def get_brands_for_category(category_id):
    brands = fetch_brands_by_category(category_id)
    return jsonify(brands)
