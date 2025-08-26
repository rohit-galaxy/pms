import os
import uuid
import random
from werkzeug.utils import secure_filename
from app import get_connection


def fetch_all_products(user_id: int, is_admin: bool):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT p.id, p.name, p.status, p.product_code,
               c.name AS category_name, b.name AS brand_name, p.image_path
        FROM product p
        JOIN product_category c ON p.category_id = c.id
        JOIN product_brand b ON p.brand_id = b.id
        WHERE p.status != '2'
    """
    params = []
    if not is_admin:
        query += " AND p.user_id = %s"
        params.append(user_id)
    query += " ORDER BY p.created_at DESC"
    cursor.execute(query, params)
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products


def fetch_product_by_id(product_id: int, user_id: int, is_admin: bool):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM product WHERE id=%s AND status != '2'"
    params = [product_id]
    if not is_admin:
        query += " AND user_id = %s"
        params.append(user_id)
    cursor.execute(query, params)
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    return product


def generate_unique_product_code():
    conn = get_connection()
    cursor = conn.cursor()

    while True:
        code = f"RDS{random.randint(10000, 99999)}"
        cursor.execute("SELECT 1 FROM product WHERE product_code = %s", (code,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return code


def create_product(name, category_id, brand_id, product_code, file, app, owner_user_id: int):
    filename = None
    if file and file.filename and allowed_file(file.filename, app):
        filename = secure_filename(str(uuid.uuid4()) + "_" + file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        file.save(save_path)

    if not product_code:
        product_code = generate_unique_product_code()

    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO product (name, category_id, brand_id, image_path, status, product_code, user_id)
        VALUES (%s, %s, %s, %s, '1', %s, %s)
    """
    cursor.execute(sql, (name, category_id, brand_id, filename, product_code, owner_user_id))
    conn.commit()
    cursor.close()
    conn.close()


def update_product(product_id, name, category_id, brand_id, file, app, user_id: int, is_admin: bool) -> bool:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT user_id, image_path FROM product WHERE id=%s", (product_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return False
    if not is_admin and row["user_id"] != user_id:
        cursor.close()
        conn.close()
        return False

    old_img = row["image_path"]

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

    cursor = conn.cursor()
    sql = """
        UPDATE product
        SET name=%s, category_id=%s, brand_id=%s, image_path=%s
        WHERE id=%s
    """
    cursor.execute(sql, (name, category_id, brand_id, filename, product_id))
    conn.commit()
    cursor.close()
    conn.close()
    return True


def toggle_product_status(product_id: int, user_id: int, is_admin: bool):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT status, user_id FROM product WHERE id=%s"
    cursor.execute(query, (product_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return None
    if not is_admin and row["user_id"] != user_id:
        cursor.close()
        conn.close()
        return None

    new_status = "0" if row["status"] == "1" else "1"
    cursor = conn.cursor()
    cursor.execute("UPDATE product SET status=%s WHERE id=%s", (new_status, product_id))
    conn.commit()
    cursor.close()
    conn.close()
    return new_status


def soft_delete_product(product_id: int, user_id: int, is_admin: bool) -> bool:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id FROM product WHERE id=%s", (product_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return False
    if not is_admin and row["user_id"] != user_id:
        cursor.close()
        conn.close()
        return False

    cursor = conn.cursor()
    cursor.execute("UPDATE product SET status='2' WHERE id=%s", (product_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return True


def allowed_file(filename, app):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_IMAGE_EXTENSIONS"]
    )


def check_product_name_exists(name, exclude_id=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    if exclude_id:
        cursor.execute(
            "SELECT id FROM product WHERE name = %s AND status != '2' AND id != %s",
            (name, exclude_id)
        )
    else:
        cursor.execute("SELECT id FROM product WHERE name = %s AND status != '2'", (name,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    return product is not None
