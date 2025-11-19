# managers/customer_manager.py
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CUSTOMERS_FILE = os.path.join(BASE_DIR, "data", "customers.json")


class CustomerManager:
    customers = []

    @classmethod
    def load_customers(cls):
        """Load customers from JSON file into memory."""
        if not os.path.exists(CUSTOMERS_FILE):
            with open(CUSTOMERS_FILE, 'w') as f:
                json.dump([], f)

        with open(CUSTOMERS_FILE, 'r') as f:
            cls.customers = json.load(f)

    @classmethod
    def save_customers(cls):
        """Save current customers to JSON file."""
        with open(CUSTOMERS_FILE, 'w') as f:
            json.dump(cls.customers, f, indent=4)

    @classmethod
    def get_all(cls):
        return cls.customers

    @classmethod
    def get(cls, cid):
        """Get a single customer by ID"""
        return next((c for c in cls.customers if str(c["id"]) == str(cid)), None)

    @classmethod
    def add_or_update_customer(cls, user_data, order_id):
        """
        Add a new customer or update existing one.
        Returns the customer record.
        """
        existing_customer = next(
            (c for c in cls.customers if c["email"].lower() == user_data["email"].lower()), None
        )

        if existing_customer:
            # Append new order ID
            existing_customer["orders"].append(order_id)
        else:
            # Create new customer
            next_id = (cls.customers[0]["id"] + 1) if cls.customers else 1
            new_customer = {
                "id": next_id,
                "name": user_data["name"],
                "email": user_data["email"],
                "phone": user_data["phone"],
                "address": user_data["address"],
                "orders": [order_id]
            }
            cls.customers.insert(0, new_customer)
            existing_customer = new_customer

        cls.save_customers()
        return existing_customer

    @classmethod
    def get_by_email(cls, email):
        """Get a customer by email."""
        return next((c for c in cls.customers if c["email"].lower() == email.lower()), None)
