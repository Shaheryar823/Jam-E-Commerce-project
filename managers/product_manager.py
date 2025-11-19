import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PRODUCTS_FILE = os.path.join(BASE_DIR, "data", "products.json")


class ProductManager:
    products = []

    # -------------------------
    # Load and Save
    # -------------------------
    @classmethod
    def load_products(cls):
        file_path = os.path.abspath(PRODUCTS_FILE)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                cls.products = json.load(f)
        else:
            cls.products = []

    @classmethod
    def save_products(cls):
        file_path = os.path.abspath(PRODUCTS_FILE)
        with open(file_path, 'w') as f:
            json.dump(cls.products, f, indent=4)

    # -------------------------
    # Basic Getters
    # -------------------------
    @classmethod
    def get_all(cls):
        return cls.products

    @classmethod
    def get(cls, pid):
        product = next((p for p in cls.products if p["id"] == pid), None)
        return product

    # -------------------------
    # Admin Functions
    # -------------------------
    @classmethod
    def generate_id(cls):
        """Create safe auto-increment ID based on last product."""
        if not cls.products:
            return 1
        return cls.products[-1]["id"] + 1

    @classmethod
    def add_product(cls, product_data):
        """Add a new product (admin)"""
        new_product = {
            "id": cls.generate_id(),
            "name": product_data.get("name"),
            "description": product_data.get("description"),
            "price": float(product_data.get("price")),
            "image": product_data.get("image"),
            "status": "available"
        }

        cls.products.append(new_product)
        cls.save_products()
        return new_product

    @classmethod
    def update_product(cls, pid, updated_data):
        """Edit a product"""
        product = cls.get(pid)
        if not product:
            return None

        product["name"] = updated_data.get("name", product["name"])
        product["description"] = updated_data.get("description", product["description"])
        product["price"] = float(updated_data.get("price", product["price"]))
        product["image"] = updated_data.get("image", product["image"])
        product["status"] = updated_data.get("status", product["status"])

        cls.save_products()
        return product

    @classmethod
    def delete_product(cls, pid):
        """Delete product from list + save"""
        cls.products = [p for p in cls.products if p["id"] != pid]
        cls.save_products()
        return True
