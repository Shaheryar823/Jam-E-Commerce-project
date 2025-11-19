# managers/order_manager.py
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ORDERS_FILE = os.path.join(BASE_DIR, "data", "orders.json")


class OrderManager:
    orders = []

    @classmethod
    def load_orders(cls):
        """Load orders from JSON file into memory."""
        if not os.path.exists(ORDERS_FILE):
            with open(ORDERS_FILE, 'w') as f:
                json.dump([], f)

        with open(ORDERS_FILE, 'r') as f:
            cls.orders = json.load(f)

    @classmethod
    def save_orders(cls):
        """Save current orders to JSON file."""
        with open(ORDERS_FILE, 'w') as f:
            json.dump(cls.orders, f, indent=4)

    @classmethod
    def add_order(cls, user_data, items, total):
        """Add a new order and return it."""
        next_id = (cls.orders[0]["id"] + 1) if cls.orders else 1

        order = {
            "id": next_id,
            "user": user_data,
            "items": items,
            "total": round(total, 2),
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Pending"
        }

        cls.orders.insert(0, order)
        cls.save_orders()
        return order

    @classmethod
    def get_all(cls):
        return cls.orders

    @classmethod
    def get_by_email(cls, email):
        return [o for o in cls.orders if o.get("user", {}).get("email", "").lower() == email.lower()]
    
    @classmethod
    def get(cls, oid):
        return next((o for o in cls.orders if str(o["id"]) == str(oid)), None)


