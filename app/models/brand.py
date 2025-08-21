from app import get_connection

def fetch_all_brands():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.*, c.name AS category_name 
        FROM product_brand b 
        JOIN product_category c ON b.category_id = c.id 
        WHERE b.status != '2' 
        ORDER BY b.created_at DESC
    """)
    brands = cursor.fetchall()
    cursor.close()
    conn.close()
    return brands

def fetch_brand_by_id(brand_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM product_brand WHERE id=%s AND status != '2'", (brand_id,))
    brand = cursor.fetchone()
    cursor.close()
    conn.close()
    return brand

def fetch_brands_by_category(category_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM product_brand WHERE category_id=%s AND status='1' ORDER BY name", (category_id,))
    brands = cursor.fetchall()
    cursor.close()
    conn.close()
    return brands

def create_brand(name, category_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id FROM product_brand WHERE name=%s AND category_id=%s AND status != '2'",
        (name, category_id)
    )
    exists = cursor.fetchone()
    if exists:
        cursor.close()
        conn.close()
        return None
    cursor.execute(
        "INSERT INTO product_brand (name, category_id, status) VALUES (%s, %s, '1')",
        (name, category_id)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return new_id

def update_brand(brand_id, name, category_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id FROM product_brand WHERE name=%s AND category_id=%s AND status != '2' AND id != %s",
        (name, category_id, brand_id)
    )
    exists = cursor.fetchone()
    if exists:
        cursor.close()
        conn.close()
        return False
    cursor = conn.cursor()
    cursor.execute("UPDATE product_brand SET name=%s, category_id=%s WHERE id=%s", (name, category_id, brand_id))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def toggle_brand_status(brand_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT status FROM product_brand WHERE id=%s", (brand_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return None
    new_status = "0" if row["status"] == "1" else "1"
    cursor.execute("UPDATE product_brand SET status=%s WHERE id=%s", (new_status, brand_id))
    conn.commit()
    cursor.close()
    conn.close()
    return new_status

def soft_delete_brand(brand_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE product_brand SET status='2' WHERE id=%s", (brand_id,))
    conn.commit()
    cursor.close()
    conn.close()
