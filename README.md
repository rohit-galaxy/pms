# Flask RBAC Shop (Flask + MySQL)

Role-based Flask application with Super Admin and Users, supporting product ownership, categories, and brands.

## Features
- Super Admin vs User roles
- Super Admin: manage all users, products, categories, brands; view all products; DataTables listing of users
- Users: manage own products, categories, and brands; cannot see other users or all users list
- Product ownership via `products.user_id`
- Secure auth ready (stores hashed default but supports plaintext `123456` for initial login)

## Tech
- Flask, SQLAlchemy, Flask-Login, Flask-Bcrypt, Flask-Migrate
- MySQL (via PyMySQL)

## Setup
1. Python 3.10+ recommended. Install system packages as needed (for Debian/Ubuntu):
   - `sudo apt update && sudo apt install -y python3-venv python3-dev default-libmysqlclient-dev`
2. Create and activate virtualenv:
   - `python3 -m venv .venv && source .venv/bin/activate`
3. Install dependencies:
   - `pip install -r requirements.txt`
4. Configure environment: create `.env` in project root:
```
SECRET_KEY=change-me
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/flask_rbac_db
```
5. Create database and apply schema:
   - Create DB `flask_rbac_db` in MySQL
   - `mysql -u root -p flask_rbac_db < database/schema.sql`
   - `mysql -u root -p flask_rbac_db < database/seed.sql`
6. Run app:
   - `python run.py`
   - Visit http://localhost:5000

## Default Admin
- Email: `admin@example.com`
- Password: `123456`

## Structure
```
app/
  __init__.py
  extensions.py
  models/
    __init__.py
    user.py
    catalog.py
  blueprints/
    auth/
      __init__.py
      routes.py
    catalog/
      __init__.py
      routes.py
    admin/
      __init__.py
      routes.py
  templates/
    base.html
    auth/
      login.html
      register.html
    catalog/
      user_dashboard.html
      products_list.html
      product_form.html
      categories_list.html
      brands_list.html
    admin/
      dashboard.html
      users.html
      products.html
  static/
    css/app.css
    js/app.js
config.py
run.py
requirements.txt
```

## Security Note
- Login currently accepts default plaintext `123456` OR bcrypt hash for backward compatibility. After initial setup, migrate all users to hashed passwords and remove plaintext acceptance by requiring `bcrypt.check_password_hash` only.