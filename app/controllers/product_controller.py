from flask import Blueprint, render_template, request, jsonify, current_app, g
from app.models.product import (
    fetch_all_products, fetch_product_by_id, create_product,
    update_product, toggle_product_status, soft_delete_product,
    check_product_name_exists
)
from app.models.category import fetch_active_categories
from app.models.brand import fetch_all_brands
from app.blueprints.auth.routes import login_required

product_bp = Blueprint('product_bp', __name__)

@product_bp.route("/")
@login_required
def index():
    categories = fetch_active_categories(g.current_user_id, g.current_user_is_admin)
    products = fetch_all_products(g.current_user_id, g.current_user_is_admin)
    return render_template("product.html", categories=categories, products=products)

@product_bp.route("/product/get/<int:id>")
@login_required
def get_product(id):
    product = fetch_product_by_id(id, g.current_user_id, g.current_user_is_admin)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

@product_bp.route("/product/create", methods=["POST"])
@login_required
def create():
    name = request.form.get("name")
    product_code = request.form.get("product_code")
    category_id = request.form.get("category_id")
    brand_id = request.form.get("brand_id")
    file = request.files.get("image")

    if not name or not category_id or not brand_id:
        return jsonify({"success": False, "message": "Please fill all required fields."}), 400

    create_product(name, category_id, brand_id, product_code, file, current_app, g.current_user_id)
    return jsonify({"success": True, "message": "Product created successfully."})

@product_bp.route("/product/update/<int:id>", methods=["POST"])
@login_required
def update(id):
    name = request.form.get("name")
    category_id = request.form.get("category_id")
    brand_id = request.form.get("brand_id")
    file = request.files.get("image")

    if not name or not category_id or not brand_id:
        return jsonify({"success": False, "message": "Please fill all required fields."}), 400

    success = update_product(id, name, category_id, brand_id, file, current_app, g.current_user_id, g.current_user_is_admin)
    if not success:
        return jsonify({"success": False, "message": "Product not found or not permitted"}), 404
    return jsonify({"success": True, "message": "Product updated successfully."})

@product_bp.route("/product/toggle-status/<int:id>", methods=["POST"])
@login_required
def toggle_status(id):
    new_status = toggle_product_status(id, g.current_user_id, g.current_user_is_admin)
    if new_status is None:
        return jsonify({"success": False, "message": "Product not found"}), 404
    return jsonify({"success": True, "status": new_status})

@product_bp.route("/product/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    success = soft_delete_product(id, g.current_user_id, g.current_user_is_admin)
    if not success:
        return jsonify({"success": False, "message": "Product not found"}), 404
    return jsonify({"success": True, "message": "Product deleted successfully."})

@product_bp.route("/product/check-name", methods=["GET"])
@login_required
def check_product_name():
    name = request.args.get("name", "").strip()
    exclude_id = request.args.get("exclude_id", default=None, type=int)

    if not name:
        return jsonify({"exists": False})

    exists = check_product_name_exists(name, exclude_id)
    return jsonify({"exists": exists})
