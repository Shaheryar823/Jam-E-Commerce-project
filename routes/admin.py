from flask import Blueprint, session, redirect, url_for, render_template, request
from functools import wraps
import json
import os
from werkzeug.security import check_password_hash, generate_password_hash
from managers.product_manager import ProductManager


ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD_HASH = generate_password_hash(os.getenv("ADMIN_PASSWORD"))
ProductManager.load_products()

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# -----------------------------
# JSON HELPERS
# -----------------------------
def load_data(file):
    try:
        with open(f"data/{file}", "r") as f:
            return json.load(f)
    except:
        return []

def save_data(file, data):
    with open(f"data/{file}", "w") as f:
        json.dump(data, f, indent=4)

# -----------------------------
# ADMIN LOGIN CHECK DECORATOR
# -----------------------------
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get("is_admin"):
            return func(*args, **kwargs)
        return redirect(url_for("admin.login"))
    return wrapper

# -----------------------------
# ADMIN LOGIN
# -----------------------------
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get("is_admin"):
        return redirect(url_for("admin.dashboard"))

    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session["is_admin"] = True
            session.permanent = True
            return redirect(url_for("admin.dashboard"))
        else:
            error = "Invalid username or password"

    return render_template("admin/admin_login.html", error=error)


# -----------------------------
# DASHBOARD HOME
# -----------------------------
@admin_bp.route('/')
@admin_required
def dashboard():
    orders = load_data("orders.json")
    customers = load_data("customers.json")
    products = ProductManager.get_all()

    return render_template(
        'admin/dashboard.html',
        total_orders=len(orders),
        total_customers=len(customers),
        total_products=len(products)
    )

# -----------------------------
# VIEW ALL ORDERS
# -----------------------------
@admin_bp.route('/orders')
@admin_required
def view_orders():
    orders = load_data("orders.json")
    return render_template('admin/view_orders.html', orders=orders)

# -----------------------------
# VIEW SINGLE ORDER
# -----------------------------
@admin_bp.route('/orders/<int:oid>')
@admin_required
def order_details(oid):
    orders = load_data("orders.json")
    order = next((o for o in orders if o["id"] == oid), None)

    if not order:
        return "Order not found", 404

    return render_template('admin/order_details.html', order=order)

# -----------------------------
# UPDATE ORDER STATUS
# -----------------------------
@admin_bp.route('/orders/update/<oid>', methods=['POST'])
@admin_required
def update_order_status(oid):
    new_status = request.form.get("status")

    orders = load_data("orders.json")

    for o in orders:
        if str(o["id"]) == str(oid):
            o["status"] = new_status
            break

    save_data("orders.json", orders)

    from utils.email_utils import send_email

    send_email(
        to=o["user"]["email"],
        subject="Order Status Updated",
        message=f"Hello {o['user']['name']},\n\nYour order #{oid} status has been updated to: {new_status}.\n\nThank you for shopping with us!"
    )


    return redirect(url_for("admin.order_details", oid=oid))

# -----------------------------
# VIEW ALL CUSTOMERS
# -----------------------------
@admin_bp.route('/customers')
@admin_required
def view_customers():
    customers = load_data("customers.json")
    return render_template("admin/view_customers.html", customers=customers)

# -----------------------------
# VIEW CUSTOMER DETAILS + ORDERS
# -----------------------------
@admin_bp.route('/customers/<cid>')
@admin_required
def customer_details(cid):
    customers = load_data("customers.json")
    orders = load_data("orders.json")

    customer = next((c for c in customers if str(c["id"]) == str(cid)), None)

    if not customer:
        return "Customer not found"

    customer_orders = [
        o for o in orders if str(o["id"]) in str(customer['orders'])
    ]

    return render_template(
        "admin/customer_details.html",
        customer=customer,
        orders=customer_orders
    )

# -----------------------------
# VIEW ALL PRODUCTS
# -----------------------------
@admin_bp.route('/products')
@admin_required
def manage_products():
    products = ProductManager.get_all()
    return render_template("admin/manage_products.html", products=products)

# -----------------------------
# ADD PRODUCT
# -----------------------------
@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == "POST":
        products = ProductManager.get_all()

        new_product = {
            "name": request.form.get("name"),
            "price": float(request.form.get("price")),
            "description": request.form.get("description"),
            "image": request.form.get("image")
        }

        ProductManager.add_product(new_product)

        return redirect(url_for("admin.manage_products"))

    return render_template("admin/add_product.html")

# -----------------------------
# EDIT PRODUCT
# -----------------------------
@admin_bp.route('/products/edit/<int:pid>', methods=['GET', 'POST'])
@admin_required
def edit_product(pid):
    products = ProductManager.get_all()
    product = next((p for p in products if p["id"] == pid), None)

    if not product:
        return "Product not found"

    if request.method == "POST":
        new_product = {
            "name": request.form.get("name"),
            "price": float(request.form.get("price")),
            "description": request.form.get("description"),
            "image": request.form.get("image")
        }

        ProductManager.update_product(pid, new_product)
        return redirect(url_for("admin.manage_products"))

    return render_template("admin/edit_product.html", product=product)

# -----------------------------
# DELETE PRODUCT
# -----------------------------
@admin_bp.route('/products/delete/<int:pid>')
@admin_required
def delete_product(pid):
    ProductManager.delete_product(pid)
    return redirect(url_for("admin.manage_products"))

# -----------------------------
# TOGGLE PRODUCT STATUS
# -----------------------------
@admin_bp.route('/products/toggle/<int:pid>')
@admin_required
def toggle_product(pid):
    product = ProductManager.get(pid)
    if not product:
        return "Product not found",404
    
    new_status = "available" if product.get("status") == "out-of-stock" else "out-of-stock"

    ProductManager.update_product(pid, {"status": new_status})
    return redirect(url_for("admin.manage_products"))

# -----------------------------
# LOGOUT
# -----------------------------
@admin_bp.route('/logout')
@admin_required
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin.login"))
