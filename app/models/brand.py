from app import get_connection
from flask import session


def fetch_all_brands():
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT b.*, c.name AS category_name, b.created_at, b.updated_at
        FROM product_brand b
        JOIN product_category c ON b.category_id = c.id
        WHERE b.status != '2'
    """
    params = ()
    if not is_admin:
        query += " AND b.user_id = %s"
        params = (user_id,)
    query += " ORDER BY b.created_at DESC"
    cursor.execute(query, params)
    brands = cursor.fetchall()
    cursor.close()
    conn.close()
    return brands


def fetch_brand_by_id(brand_id):
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT *, created_at, updated_at FROM product_brand WHERE id=%s AND status != '2'"
    params = (brand_id,)
    if not is_admin:
        query += " AND user_id = %s"
        params += (user_id,)
    cursor.execute(query, params)
    brand = cursor.fetchone()
    cursor.close()
    conn.close()
    return brand


def fetch_brands_by_category(category_id):
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM product_brand WHERE category_id=%s AND status='1'"
    params = (category_id,)
    if not is_admin:
        query += " AND user_id = %s"
        params += (user_id,)
    query += " ORDER BY name"
    cursor.execute(query, params)
    brands = cursor.fetchall()
    cursor.close()
    conn.close()
    return brands


def create_brand(name, category_id):
    user_id = session.get('user_id')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM product_brand WHERE name=%s AND category_id=%s AND status != '2' AND user_id = %s",
        (name, category_id, user_id)
    )
    exists = cursor.fetchone()
    if exists:
        cursor.close()
        conn.close()
        return None

    cursor.execute(
        "INSERT INTO product_brand (name, category_id, status, user_id) VALUES (%s, %s, '1', %s)",
        (name, category_id, user_id)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return new_id


def update_brand(brand_id, name, category_id):
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT id FROM product_brand
        WHERE name=%s AND category_id=%s AND status != '2' AND id != %s
    """
    params = (name, category_id, brand_id)
    if not is_admin:
        query += " AND user_id = %s"
        params += (user_id,)
    cursor.execute(query, params)
    exists = cursor.fetchone()
    if exists:
        cursor.close()
        conn.close()
        return False

    cursor = conn.cursor()
    update_query = "UPDATE product_brand SET name=%s, category_id=%s WHERE id=%s"
    update_params = (name, category_id, brand_id)
    if not is_admin:
        update_query += " AND user_id = %s"
        update_params += (user_id,)
    cursor.execute(update_query, update_params)
    conn.commit()
    cursor.close()
    conn.close()
    return True


def toggle_brand_status(brand_id):
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT status FROM product_brand WHERE id=%s"
    params = (brand_id,)
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

    update_query = "UPDATE product_brand SET status=%s WHERE id=%s"
    update_params = (new_status, brand_id)
    if not is_admin:
        update_query += " AND user_id = %s"
        update_params += (user_id,)
    cursor.execute(update_query, update_params)
    conn.commit()
    cursor.close()
    conn.close()
    return new_status


def soft_delete_brand(brand_id):
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)
    conn = get_connection()
    cursor = conn.cursor()

    # Soft delete the brand
    query = "UPDATE product_brand SET status='2' WHERE id=%s"
    params = (brand_id,)
    if not is_admin:
        query += " AND user_id = %s"
        params += (user_id,)
    cursor.execute(query, params)

    # Soft delete all products under this brand
    prod_query = "UPDATE product SET status='2' WHERE brand_id=%s"
    prod_params = (brand_id,)
    if not is_admin:
        prod_query += " AND user_id = %s"
        prod_params += (user_id,)
    cursor.execute(prod_query, prod_params)

    conn.commit()
    cursor.close()
    conn.close()
    return True


def check_brand_name_exists(name, category_id, exclude_id=None):
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT id FROM product_brand WHERE name = %s AND category_id = %s AND status != '2'"
    params = (name, category_id)
    if exclude_id:
        query += " AND id != %s"
        params += (exclude_id,)
    if not is_admin:
        query += " AND user_id = %s"
        params += (user_id,)
    cursor.execute(query, params)
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists
