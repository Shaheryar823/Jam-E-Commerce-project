import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PRODUCTS_FILE = os.path.join(BASE_DIR, "data", "products.json")


class ProductManager:
    products = []

    @classmethod
    def load_products(cls):
        file_path = os.path.abspath(PRODUCTS_FILE)
        with open(file_path, 'r') as f:
            cls.products = json.load(f)

    @classmethod
    def get_all(cls):
        return cls.products

    @classmethod
    def get(cls, pid):
        return next((p for p in cls.products if p["id"] == pid), None)
