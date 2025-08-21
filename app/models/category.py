from app import get_connection

def fetch_all_categories():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM product_category WHERE status != '2' ORDER BY created_at DESC")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return categories

def fetch_active_categories():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM product_category WHERE status='1' ORDER BY name")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return categories

def fetch_category_by_id(category_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM product_category WHERE id=%s AND status != '2'", (category_id,))
    category = cursor.fetchone()
    cursor.close()
    conn.close()
    return category

def create_category(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO product_category (name, status) VALUES (%s, '1')", (name,))
    conn.commit()
    cursor.close()
    conn.close()

def update_category(category_id, name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE product_category SET name=%s WHERE id=%s", (name, category_id))
    conn.commit()
    cursor.close()
    conn.close()

def toggle_category_status(category_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT status FROM product_category WHERE id=%s", (category_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return None
    new_status = "0" if row["status"] == "1" else "1"
    cursor.execute("UPDATE product_category SET status=%s WHERE id=%s", (new_status, category_id))
    conn.commit()
    cursor.close()
    conn.close()
    return new_status

def soft_delete_category(category_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE product_category SET status='2' WHERE id=%s", (category_id,))
    conn.commit()
    cursor.close()
    conn.close()
