from app import get_connection
from flask import session

def fetch_all_categories():
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT *, created_at, updated_at FROM product_category WHERE status != '2'"
    params = ()
    if not is_admin:
        query += " AND user_id = %s"
        params = (user_id,)
    query += " ORDER BY created_at DESC"
    cursor.execute(query, params)
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return categories

def fetch_active_categories():
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT *, created_at, updated_at FROM product_category WHERE status='1'"
    params = ()
    if not is_admin:
        query += " AND user_id = %s"
        params = (user_id,)
    query += " ORDER BY name"
    cursor.execute(query, params)
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return categories

def fetch_category_by_id(category_id):
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT *, created_at, updated_at FROM product_category WHERE id=%s AND status != '2'"
    params = (category_id,)
    if not is_admin:
        query += " AND user_id = %s"
        params += (user_id,)
    cursor.execute(query, params)
    category = cursor.fetchone()
    cursor.close()
    conn.close()
    return category

def create_category(name):
    user_id = session.get('user_id')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO product_category (name, status, user_id) VALUES (%s, '1', %s)",
        (name, user_id)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return new_id

def update_category(category_id, name):
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    conn = get_connection()
    cursor = conn.cursor()
    query = "UPDATE product_category SET name=%s WHERE id=%s"
    params = (name, category_id)
    if not is_admin:
        query += " AND user_id = %s"
        params += (user_id,)
    cursor.execute(query, params)
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return affected > 0

def toggle_category_status(category_id):
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT status FROM product_category WHERE id=%s"
    params = (category_id,)
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

    update_query = "UPDATE product_category SET status=%s WHERE id=%s"
    update_params = (new_status, category_id)
    if not is_admin:
        update_query += " AND user_id = %s"
        update_params += (user_id,)
    cursor.execute(update_query, update_params)
    conn.commit()
    cursor.close()
    conn.close()
    return new_status

def soft_delete_category(category_id):
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)
    conn = get_connection()
    cursor = conn.cursor()

    # Soft delete the category
    query = "UPDATE product_category SET status='2' WHERE id=%s"
    params = (category_id,)
    if not is_admin:
        query += " AND user_id = %s"
        params += (user_id,)
    cursor.execute(query, params)

    # Find all brands in this category
    brand_query = "SELECT id FROM product_brand WHERE category_id=%s AND status != '2'"
    brand_params = (category_id,)
    if not is_admin:
        brand_query += " AND user_id = %s"
        brand_params += (user_id,)
    cursor.execute(brand_query, brand_params)
    brand_ids = [row[0] for row in cursor.fetchall()]

    # Soft delete those brands
    if brand_ids:
        brand_placeholders = ','.join(['%s'] * len(brand_ids))
        brand_update_query = f"UPDATE product_brand SET status='2' WHERE id IN ({brand_placeholders})"
        cursor.execute(brand_update_query, brand_ids)

        # For all these brands, soft delete all their products
        prod_update_query = f"UPDATE product SET status='2' WHERE brand_id IN ({brand_placeholders})"
        cursor.execute(prod_update_query, brand_ids)

    conn.commit()
    cursor.close()
    conn.close()
    return True


def check_category_name_exists(name, exclude_id=None):
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT id FROM product_category WHERE LOWER(name) = LOWER(%s) AND status != '2'"

    params = (name,)
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
