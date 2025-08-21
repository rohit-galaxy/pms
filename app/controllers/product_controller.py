from flask import Blueprint, render_template, request, jsonify, current_app
from app.models.product import (
    fetch_all_products, fetch_product_by_id, create_product,
    update_product, toggle_product_status, soft_delete_product
)
from app.models.category import fetch_active_categories
from app.models.brand import fetch_all_brands

product_bp = Blueprint('product_bp', __name__)

@product_bp.route("/")
def index():
    categories = fetch_active_categories()
    products = fetch_all_products()
    return render_template("product.html", categories=categories, products=products)

@product_bp.route("/product/get/<int:id>")
def get_product(id):
    product = fetch_product_by_id(id)
    if product:
        return jsonify(product)    
    return jsonify({"error": "Product not found"}), 404

@product_bp.route("/product/create", methods=["POST"])
def create():
    name = request.form.get("name")
    category_id = request.form.get("category_id")
    brand_id = request.form.get("brand_id")
    file = request.files.get("image")
    if not name or not category_id or not brand_id:
        return jsonify({"success": False, "message": "Please fill all required fields."}), 400
    create_product(name, category_id, brand_id, file, current_app)
    return jsonify({"success": True, "message": "Product created successfully."})

@product_bp.route("/product/update/<int:id>", methods=["POST"])
def update(id):
    name = request.form.get("name")
    category_id = request.form.get("category_id")
    brand_id = request.form.get("brand_id")
    file = request.files.get("image")
    if not name or not category_id or not brand_id:
        return jsonify({"success": False, "message": "Please fill all required fields."}), 400
    update_product(id, name, category_id, brand_id, file, current_app)
    return jsonify({"success": True, "message": "Product updated successfully."})

@product_bp.route("/product/toggle-status/<int:id>", methods=["POST"])
def toggle_status(id):
    new_status = toggle_product_status(id)
    if new_status is None:
        return jsonify({"success": False, "message": "Product not found"}), 404
    return jsonify({"success": True, "status": new_status})

@product_bp.route("/product/delete/<int:id>", methods=["POST"])
def delete(id):
    soft_delete_product(id)
    return jsonify({"success": True, "message": "Product deleted (soft delete)."})
