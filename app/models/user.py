from app import get_connection

def fetch_all_users():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, email, is_admin, status, created_at, updated_at FROM users WHERE status != '2' ORDER BY created_at DESC")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

def fetch_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s AND status != '2'", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def fetch_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s AND status != '2'", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def create_user(email, password, is_admin):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (email, password, is_admin, status) VALUES (%s, %s, %s, '1')",
        (email.strip(), password.strip(), is_admin)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return new_id

def update_user(user_id, email, password=None, is_admin=None):
    conn = get_connection()
    cursor = conn.cursor()
    if password:
        cursor.execute(
            "UPDATE users SET email=%s, password=%s, is_admin=%s WHERE id=%s",
            (email.strip(), password.strip(), is_admin, user_id)
        )
    else:
        cursor.execute(
            "UPDATE users SET email=%s, is_admin=%s WHERE id=%s",
            (email.strip(), is_admin, user_id)
        )
    conn.commit()
    cursor.close()
    conn.close()
    return True

def toggle_user_status(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT status FROM users WHERE id=%s", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return None
    new_status = "0" if row["status"] == "1" else "1"
    cursor.execute("UPDATE users SET status=%s WHERE id=%s", (new_status, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return new_status

def soft_delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status='2' WHERE id=%s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()

def authenticate_user(email, password):
    user = fetch_user_by_email(email)
    if user and user['password'].strip() == password.strip():
        return user
    return None

def check_email_exists(email, exclude_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    if exclude_id:
        cursor.execute("SELECT id FROM users WHERE email = %s AND id != %s", (email.strip(), exclude_id))
    else:
        cursor.execute("SELECT id FROM users WHERE email = %s", (email.strip(),))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists

def update_user_password(user_id, old_password, new_password, admin_override=False):
    """
    Update a user's password.
    - If admin_override=True → skip old password check.
    - Otherwise → verify old password before updating.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE id=%s", (user_id,))
    row = cursor.fetchone()

    if not row:
        cursor.close()
        conn.close()
        return False, "User not found."

    stored_password = row[0].strip() if row[0] is not None else ''

    if not admin_override:
        if stored_password != old_password.strip():
            cursor.close()
            conn.close()
            return False, "Old password is incorrect."

    cursor.execute("UPDATE users SET password=%s WHERE id=%s", (new_password.strip(), user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return True, "Password updated successfully."
