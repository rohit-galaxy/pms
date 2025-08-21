import os
import uuid
from werkzeug.utils import secure_filename
from app import get_connection

def fetch_all_products():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT p.id, p.name, p.status, c.name AS category_name, b.name AS brand_name, p.image_path
        FROM product p
        JOIN product_category c ON p.category_id = c.id
        JOIN product_brand b ON p.brand_id = b.id
        WHERE p.status != '2'
        ORDER BY p.created_at DESC
    """
    cursor.execute(query)
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products

def fetch_product_by_id(product_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM product WHERE id=%s AND status != '2'", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    return product

def create_product(name, category_id, brand_id, file, app):
    filename = None
    if file and file.filename and allowed_file(file.filename, app):
        filename = secure_filename(str(uuid.uuid4()) + "_" + file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        file.save(save_path)
    conn = get_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO product (name, category_id, brand_id, image_path, status) VALUES (%s, %s, %s, %s, '1')"
    cursor.execute(sql, (name, category_id, brand_id, filename))
    conn.commit()
    cursor.close()
    conn.close()

def update_product(product_id, name, category_id, brand_id, file, app):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT image_path FROM product WHERE id=%s", (product_id,))
    old = cursor.fetchone()
    old_img = old["image_path"] if old else None
    cursor.close()
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
    sql = "UPDATE product SET name=%s, category_id=%s, brand_id=%s, image_path=%s WHERE id=%s"
    cursor.execute(sql, (name, category_id, brand_id, filename, product_id))
    conn.commit()
    cursor.close()
    conn.close()

def toggle_product_status(product_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT status FROM product WHERE id=%s", (product_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return None
    new_status = "0" if row["status"] == "1" else "1"
    cursor.execute("UPDATE product SET status=%s WHERE id=%s", (new_status, product_id))
    conn.commit()
    cursor.close()
    conn.close()
    return new_status

def soft_delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE product SET status='2' WHERE id=%s", (product_id,))
    conn.commit()
    cursor.close()
    conn.close()

def allowed_file(filename, app):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_IMAGE_EXTENSIONS"]
    )
