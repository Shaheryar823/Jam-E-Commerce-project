from flask import Blueprint, render_template, url_for, session, request, jsonify, flash,redirect
import json, os
from managers.product_manager import ProductManager
from managers.order_manager import OrderManager




main_bp = Blueprint('main', __name__)

# Load products from JSON file once when app starts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CUSTOMERS_FILE = os.path.join(BASE_DIR, '../data/customers.json')
OrderManager.load_orders()
ProductManager.load_products()

@main_bp.route('/')
def index():
    return render_template('index.html', products=ProductManager.get_all())


@main_bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = str(data.get('id'))

    if 'cart' not in session:
        session['cart'] = {}

    # Add 1 to quantity
    session['cart'][product_id] = session['cart'].get(product_id, 0) + 1
    session.modified = True

    # Return total quantity in cart
    total_items = sum(session['cart'].values())
    return jsonify({"message": "Added to cart successfully!", "cartCount": total_items})

@main_bp.route('/product/<int:pid>')
def product_page(pid):
    # Find the product by ID
    product = ProductManager.get(pid)
    if not product:
        return "Product not found", 404

    return render_template('product_page.html', product=product)



@main_bp.route('/cart')
def cart():
    cart_items = session.get('cart', {})  # {product_id: quantity}
    cart_products = []
    total = 0
    total_qty = 0

    for p in ProductManager.get_all():
        qty = cart_items.get(str(p["id"]), 0)
        if qty > 0:
            cart_products.append({
                "id": p["id"],
                "name": p["name"],
                "description": p["description"],
                "price": p["price"],
                "image": p["image"],
                "quantity": qty,
                "subtotal": round(p["price"] * qty, 2)
            })
            total += p["price"] * qty
            total_qty = total_qty + qty 

    total = round(total, 2)  # round total to 2 decimal places
    return render_template('cart.html', cart_products=cart_products, total=total, total_qty = total_qty)

@main_bp.route('/update_cart', methods=['POST'])
def update_cart():
    data = request.get_json()
    pid = str(data.get('id'))
    action = data.get('action')

    if 'cart' not in session:
        session['cart'] = {}

    if pid in session['cart']:
        if action == 'increase':
            session['cart'][pid] += 1
        elif action == 'decrease':
            session['cart'][pid] = max(1, session['cart'][pid] - 1)
    else:
        if action == 'increase':
            session['cart'][pid] = 1

    session.modified = True

    # Recalculate totals
    total = 0
    total_qty = 0
    for p in ProductManager.get_all():
        if str(p["id"]) in session['cart']:
            qty = session['cart'][str(p["id"])]
            total += p["price"] * qty
            total_qty += qty

    # Return also the updated quantity for this product
    return jsonify({
        "success": True,
        "total": round(total, 2),
        "total_qty": total_qty,
        "qty": session['cart'][pid]
    })



# Remove an item from cart
@main_bp.route('/remove_item', methods=['POST'])
def remove_item():
    data = request.get_json()
    pid = str(data.get('id'))

    if 'cart' in session and pid in session['cart']:
        session['cart'].pop(pid)
        session.modified = True

    # Recalculate totals
    total = 0
    total_qty = 0
    for p in ProductManager.get_all():
        if str(p["id"]) in session.get('cart', {}):
            qty = session['cart'][str(p["id"])]
            total += p["price"] * qty
            total_qty += qty

    return jsonify({"success": True, "total": round(total, 2), "total_qty": total_qty})

@main_bp.route('/cart_count')
def cart_count():
    cart = session.get('cart', {})  # {product_id: quantity}
    total_qty = sum(cart.values()) if isinstance(cart, dict) else 0
    return jsonify({"count": total_qty})


# Checkout (AJAX - step 1)
@main_bp.route('/checkout', methods=['POST'])
def checkout():
    cart_items = session.get('cart', {})
    if not cart_items:
        return jsonify({"success": False, "message": "Your cart is empty."}), 400

    # Redirect user to the checkout form
    return jsonify({"success": True, "redirect": url_for('main.checkout_details')})


# Checkout details (form - step 2)
@main_bp.route('/checkout/details', methods=['GET', 'POST'])
def checkout_details():
    if request.method == 'POST':
        user_data = {
            "name": request.form.get('name'),
            "email": request.form.get('email'),
            "phone": request.form.get('phone'),
            "address": request.form.get('address'),
        }

        cart_items = session.get('cart', {})
        if not cart_items:
            flash("Your cart is empty.", "warning")
            return redirect(url_for('main.cart'))

        cart_products = []
        total = 0

        for p in ProductManager.get_all():
            qty = cart_items.get(str(p["id"]), 0)
            if qty > 0:
                item_total = round(p["price"] * qty, 2)
                cart_products.append({
                    "id": p["id"],
                    "name": p["name"],
                    "price": p["price"],
                    "quantity": qty,
                    "subtotal": item_total
                })
                total += item_total

        # ---------------------------------------
        # save and Load current orders to calculate next ID
        # ---------------------------------------
        next_id = OrderManager.add_order(user_data, cart_products, total)['id']

        # -------------------------------------------
        #  SAVE / UPDATE CUSTOMER FILE
        # -------------------------------------------

        # Load existing customers
        try:
            with open(CUSTOMERS_FILE, 'r') as cf:
                customers = json.load(cf)
        except FileNotFoundError:
            customers = []

        # Check if customer already exists (match by email)
        existing_customer = next((c for c in customers if c["email"] == user_data["email"]), None)

        if existing_customer:
            # ⭐ Customer exists → add current order ID into their record
            existing_customer["orders"].append(next_id)

        else:
            # ⭐ New customer → create new entry
            new_customer_id = (customers[0]["id"] + 1) if customers else 1

            new_customer = {
                "id": new_customer_id,
                "name": user_data["name"],
                "email": user_data["email"],
                "phone": user_data["phone"],
                "address": user_data["address"],
                "orders": [next_id]
            }

            customers.insert(0, new_customer)

        # Save customer file
        with open(CUSTOMERS_FILE, 'w') as cf:
            json.dump(customers, cf, indent=4)


        session['user_info'] = user_data
        session.pop('cart', None)
        session.modified = True

        from utils.email_utils import send_email

        # After placing order
        send_email(
            to=user_data["email"],
            subject="Your Order Has Been Placed",
            message=f"Dear {user_data['name']},\n\nThank you for your order!\nYour order ID is {next_id}.\n\nWe will update you when your status changes.\n\nRegards,\nJams Store"
        )


        return redirect(url_for('main.checkout_success'))

    return render_template('checkout_details.html')



# Checkout success (step 3)
@main_bp.route('/checkout/success')
def checkout_success():
    user = session.get('user_info', {})
    return render_template('success.html', user=user)

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
