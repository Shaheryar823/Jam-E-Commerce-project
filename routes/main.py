from flask import Blueprint, render_template, url_for, session, request, jsonify, flash, redirect
from managers.product_manager import ProductManager
from managers.order_manager import OrderManager
from managers.customer_manager import CustomerManager
from managers.cart_manager import CartManager
from utils.email_utils import send_email

main_bp = Blueprint('main', __name__)

# Load data on app startup
OrderManager.load_orders()
ProductManager.load_products()
CustomerManager.load_customers()


# ---------------------------
# Home / Index
# ---------------------------
@main_bp.route('/')
def index():
    return render_template('index.html', products=ProductManager.get_all())


# ---------------------------
# Product page
# ---------------------------
@main_bp.route('/product/<int:pid>')
def product_page(pid):
    product = ProductManager.get(pid)
    if not product:
        return "Product not found", 404
    return render_template('product_page.html', product=product)


# ---------------------------
# Cart routes
# ---------------------------
@main_bp.route('/cart')
def cart():
    cart = CartManager.get_cart(session)
    cart_products, total, total_qty = CartManager.build_cart_details(cart)
    return render_template('cart.html', cart_products=cart_products, total=total, total_qty=total_qty)


@main_bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = str(data.get('id'))
    CartManager.add_to_cart(session, product_id)
    total_items = CartManager.get_total_qty(session)
    return jsonify({"message": "Added to cart successfully!", "cartCount": total_items})


@main_bp.route('/update_cart', methods=['POST'])
def update_cart():
    data = request.get_json()
    product_id = str(data.get('id'))
    action = data.get('action')
    CartManager.update_cart(session, product_id, action)

    cart_products, total, total_qty = CartManager.build_cart_details(session.get('cart', {}))
    qty = session['cart'].get(product_id, 0)

    return jsonify({
        "success": True,
        "total": total,
        "total_qty": total_qty,
        "qty": qty
    })


@main_bp.route('/remove_item', methods=['POST'])
def remove_item():
    data = request.get_json()
    product_id = str(data.get('id'))
    CartManager.remove_item(session, product_id)

    cart_products, total, total_qty = CartManager.build_cart_details(session.get('cart', {}))
    return jsonify({"success": True, "total": total, "total_qty": total_qty})


@main_bp.route('/cart_count')
def cart_count():
    total_qty = CartManager.get_total_qty(session)
    return jsonify({"count": total_qty})


# ---------------------------
# Checkout
# ---------------------------
@main_bp.route('/checkout', methods=['POST'])
def checkout():
    cart = CartManager.get_cart(session)
    if not cart:
        return jsonify({"success": False, "message": "Your cart is empty."}), 400
    return jsonify({"success": True, "redirect": url_for('main.checkout_details')})


@main_bp.route('/checkout/details', methods=['GET', 'POST'])
def checkout_details():
    if request.method == 'POST':
        # 1. Collect user data
        user_data = {
            "name": request.form.get('name'),
            "email": request.form.get('email'),
            "phone": request.form.get('phone'),
            "address": request.form.get('address'),
        }

        cart = CartManager.get_cart(session)
        if not cart:
            flash("Your cart is empty.", "warning")
            return redirect(url_for('main.cart'))

        # 2. Build cart product list
        cart_products, total, total_qty = CartManager.build_cart_details(cart)

        # 3. Create order
        order = OrderManager.add_order(user_data=user_data, items=cart_products, total=total)
        order_id = order["id"]

        # 4. Update customer
        CustomerManager.add_or_update_customer(user_data, order_id)

        # 5. Clear cart + save user session
        CartManager.clear_cart(session)
        session['user_info'] = user_data
        session.modified = True

        # 6. Send confirmation email
        send_email(
            to=user_data["email"],
            subject="Your Order Has Been Placed",
            message=f"""
Dear {user_data['name']},

Thank you for your order!
Your order ID is {order_id}.

We will notify you when the status updates.

Regards,
Jams Store
""")

        return redirect(url_for('main.checkout_success'))

    # GET request
    return render_template('checkout_details.html')


# ---------------------------
# Checkout success
# ---------------------------
@main_bp.route('/checkout/success')
def checkout_success():
    user = session.get('user_info', {})
    return render_template('success.html', user=user)


# ---------------------------
# Order tracking
# ---------------------------
@main_bp.route('/track', methods=['GET', 'POST'])
def track_order():
    if request.method == "POST":
        email = request.form.get("email").strip().lower()
        return redirect(url_for("main.track_by_email", email=email))
    return render_template("track_order.html")


@main_bp.route('/track/email/<email>')
def track_by_email(email):
    email = email.lower()
    user_orders = OrderManager.get_by_email(email)
    if not user_orders:
        return render_template("track_not_found.html", email=email)
    return render_template("track_result_email.html", orders=user_orders, email=email)
