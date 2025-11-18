import json
from managers.product_manager import ProductManager

class CartManager:
    """
    Handles all cart-related operations:
    - Adding/removing/updating items
    - Calculating totals
    - Building cart details for templates
    """

    @staticmethod
    def get_cart(session):
        """Get cart from session, ensure it's a dict"""
        if 'cart' not in session:
            session['cart'] = {}
        return session['cart']

    @staticmethod
    def add_to_cart(session, product_id):
        """Add a product to the cart or increase quantity by 1"""
        cart = CartManager.get_cart(session)
        cart[product_id] = cart.get(product_id, 0) + 1
        session.modified = True

    @staticmethod
    def update_cart(session, product_id, action):
        """Increase or decrease product quantity in cart"""
        cart = CartManager.get_cart(session)
        if product_id in cart:
            if action == 'increase':
                cart[product_id] += 1
            elif action == 'decrease':
                cart[product_id] = max(1, cart[product_id] - 1)
        else:
            if action == 'increase':
                cart[product_id] = 1
        session.modified = True

    @staticmethod
    def remove_item(session, product_id):
        """Remove a product from the cart"""
        cart = CartManager.get_cart(session)
        if product_id in cart:
            cart.pop(product_id)
            session.modified = True

    @staticmethod
    def clear_cart(session):
        """Empty the cart"""
        session.pop('cart', None)
        session.modified = True

    @staticmethod
    def get_totals(session):
        """Return total price and total quantity of items in cart"""
        cart = CartManager.get_cart(session)
        total = 0
        total_qty = 0
        for product in ProductManager.get_all():
            pid = str(product['id'])
            if pid in cart:
                qty = cart[pid]
                total += product['price'] * qty
                total_qty += qty
        return round(total, 2), total_qty

    @staticmethod
    def get_total_qty(session):
        """Return total quantity of items in cart"""
        cart = CartManager.get_cart(session)
        return sum(cart.values())

    @staticmethod
    def build_cart_details(cart):
        """
        Build a detailed cart product list for templates:
        Returns: cart_products[], total price, total quantity
        """
        cart_products = []
        total = 0
        total_qty = 0
        for product in ProductManager.get_all():
            pid = str(product['id'])
            qty = cart.get(pid, 0)
            if qty > 0:
                subtotal = round(product['price'] * qty, 2)
                cart_products.append({
                    "id": product['id'],
                    "name": product['name'],
                    "description": product.get('description', ''),
                    "price": product['price'],
                    "image": product.get('image', ''),
                    "quantity": qty,
                    "subtotal": subtotal
                })
                total += subtotal
                total_qty += qty
        total = round(total, 2)
        return cart_products, total, total_qty

    @staticmethod
    def load_cart_from_session(session):
        """Initialize cart if not present"""
        if 'cart' not in session:
            session['cart'] = {}
