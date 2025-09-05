import os
import uuid
import random
from werkzeug.utils import secure_filename
from app import get_connection
from flask import session
from app.models.user import fetch_user_by_id  # Make sure this is importable


def get_user_email_prefix(user_id):
    user = fetch_user_by_id(user_id)
    if user and user.get("email"):
        return user["email"].split("@")[0]
    return "unknown"


def generate_unique_rds_code():
    conn = get_connection()
    cursor = conn.cursor()
    while True:
        code = f"RDS{random.randint(10000, 99999)}"
        cursor.execute("SELECT 1 FROM product WHERE product_code = %s", (code,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return code


def fetch_all_products():
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT p.id, p.name, p.status, p.product_code, p.created_at, p.updated_at,
               c.name AS category_name, b.name AS brand_name, p.image_path, u.email AS creator_email
        FROM product p
        JOIN product_category c ON p.category_id = c.id
        JOIN product_brand b ON p.brand_id = b.id
        JOIN users u ON p.user_id = u.id
        WHERE p.status != '2'
    """
    params = ()
    if not is_admin:
        query += " AND p.user_id = %s"
        params = (user_id,)
    query += " ORDER BY p.created_at DESC"
    cursor.execute(query, params)
    products = cursor.fetchall()
    for prod in products:
        prod["created_by"] = prod["creator_email"].split("@")[0] if prod.get("creator_email") else ""
    cursor.close()
    conn.close()
    return products


def fetch_product_by_id(product_id):
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT p.*, u.email AS creator_email
        FROM product p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = %s AND p.status != '2'
    """
    params = (product_id,)
    if not is_admin:
        query += " AND p.user_id = %s"
        params += (user_id,)
    cursor.execute(query, params)
    product = cursor.fetchone()
    if product:
        product["created_by"] = product["creator_email"].split("@")[0] if product.get("creator_email") else ""
    cursor.close()
    conn.close()
    return product


def create_product(name, category_id, brand_id, _, file, app):
    user_id = session.get('user_id')
    filename = None
    if file and file.filename and allowed_file(file.filename, app):
        filename = secure_filename(str(uuid.uuid4()) + "_" + file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        file.save(save_path)

    product_code = generate_unique_rds_code()
    created_by = get_user_email_prefix(user_id)

    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO product (name, category_id, brand_id, image_path, status, product_code, user_id, created_by)
        VALUES (%s, %s, %s, %s, '1', %s, %s, %s)
    """
    cursor.execute(sql, (name, category_id, brand_id, filename, product_code, user_id, created_by))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return new_id


def update_product(product_id, name, category_id, brand_id, file, app):
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT image_path FROM product WHERE id=%s"
    params = (product_id,)
    if not is_admin:
        query += " AND user_id = %s"
        params += (user_id,)
    cursor.execute(query, params)
    old = cursor.fetchone()
    if not old:
        cursor.close()
        conn.close()
        return False

    old_img = old["image_path"]
    filename = old_img
    if file and file.filename and allowed_file(file.filename, app):
        filename = secure_filename(str(uuid.uuid4()) + "_" + file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        file.save(save_path)
        if old_img:
            try:
                os.remove(os.path.join(app.config["UPLOAD_FOLDER"], old_img))
            except Exception:
                pass

    sql = """
        UPDATE product
        SET name=%s, category_id=%s, brand_id=%s, image_path=%s
        WHERE id=%s
    """
    if not is_admin:
        sql += " AND user_id = %s"
        params = (name, category_id, brand_id, filename, product_id, user_id)
    else:
        params = (name, category_id, brand_id, filename, product_id)
    cursor.execute(sql, params)
    conn.commit()
    cursor.close()
    conn.close()
    return True


def toggle_product_status(product_id):
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT status FROM product WHERE id=%s"
    params = (product_id,)
    if not is_admin:
        query += " AND user_id = %s"
        params += (user_id,)
    cursor.execute(query, params)
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return None

    new_status = "0" if row["status"] == "1" else "1"
    update_query = "UPDATE product SET status=%s WHERE id=%s"
    update_params = (new_status, product_id)
    if not is_admin:
        update_query += " AND user_id = %s"
        update_params += (user_id,)
    cursor.execute(update_query, update_params)
    conn.commit()
    cursor.close()
    conn.close()
    return new_status


def soft_delete_product(product_id):
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    conn = get_connection()
    cursor = conn.cursor()

    query = "UPDATE product SET status='2' WHERE id=%s"
    params = (product_id,)
    if not is_admin:
        query += " AND user_id = %s"
        params += (user_id,)
    cursor.execute(query, params)

    conn.commit()
    cursor.close()
    conn.close()
    return True


def allowed_file(filename, app):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_IMAGE_EXTENSIONS"]


def check_product_name_exists(name, exclude_id=None):
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id FROM product WHERE name = %s AND status != '2'"
    params = (name,)
    if exclude_id:
        query += " AND id != %s"
        params += (exclude_id,)
    if not is_admin:
        query += " AND user_id = %s"
        params += (user_id,)
    cursor.execute(query, params)
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    return product is not None
