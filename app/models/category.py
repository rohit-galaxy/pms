from app import get_connection


def fetch_all_categories(user_id: int, is_admin: bool):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM product_category WHERE status != '2'"
    params = []
    if not is_admin:
        query += " AND user_id = %s"
        params.append(user_id)
    query += " ORDER BY created_at DESC"
    cursor.execute(query, params)
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return categories


def fetch_active_categories(user_id: int, is_admin: bool):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM product_category WHERE status='1'"
    params = []
    if not is_admin:
        query += " AND user_id = %s"
        params.append(user_id)
    query += " ORDER BY name"
    cursor.execute(query, params)
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return categories


def fetch_category_by_id(category_id, user_id: int, is_admin: bool):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM product_category WHERE id=%s AND status != '2'"
    params = [category_id]
    if not is_admin:
        query += " AND user_id = %s"
        params.append(user_id)
    cursor.execute(query, params)
    category = cursor.fetchone()
    cursor.close()
    conn.close()
    return category


def create_category(name, owner_user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO product_category (name, status, user_id) VALUES (%s, '1', %s)", (name, owner_user_id))
    conn.commit()
    cursor.close()
    conn.close()


def update_category(category_id, name, user_id: int, is_admin: bool) -> bool:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id FROM product_category WHERE id=%s", (category_id,))
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
    cursor.execute("UPDATE product_category SET name=%s WHERE id=%s", (name, category_id))
    conn.commit()
    cursor.close()
    conn.close()
    return True


def toggle_category_status(category_id, user_id: int, is_admin: bool):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT status, user_id FROM product_category WHERE id=%s", (category_id,))
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
    cursor.execute("UPDATE product_category SET status=%s WHERE id=%s", (new_status, category_id))
    conn.commit()
    cursor.close()
    conn.close()
    return new_status


def soft_delete_category(category_id, user_id: int, is_admin: bool) -> bool:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id FROM product_category WHERE id=%s", (category_id,))
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
    cursor.execute("UPDATE product_category SET status='2' WHERE id=%s", (category_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return True
