Jam E-Commerce

A simple e-commerce web application built with Flask, allowing users to browse products, add them to a cart, checkout, and track orders. The project also includes an admin panel to manage products, customers, and orders.

Features
User Panel

Browse products with images, descriptions, and prices.

Add products to the cart and update quantities.

Checkout with a form to submit user information.

Receive email notifications after successful order placement.

Track orders using email.

Admin Panel

Add, edit, delete, and toggle product availability.

View all orders and update their status.

View customers and their order history.

Project Structure
jams_ecommerce/
│
├── app.py
├── config.py
├── requirements.txt
├── .env
├── data/
│   ├── products.json
│   ├── orders.json
│   └── customers.json
├── routes/
│   ├── main.py
│   └── admin.py
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── admin/
│   ├── base.html
│   ├── index.html
│   └── cart.html
└── utils/
    └── email_utils.py

Installation

Clone the repository

git clone <your-repo-url>
cd jams_ecommerce


Create a virtual environment and activate it

python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate


Install dependencies

pip install -r requirements.txt


Create a .env file in the root directory

SECRET_KEY=your_random_secret_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=yourpassword
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USERNAME=you@example.com
EMAIL_PASSWORD=your_email_password


Run the application

flask run


Open your browser and go to: http://127.0.0.1:5000

Usage
User Panel

Browse products on the home page.

Add items to the cart using the "Add to Cart" button.

Checkout and receive an email confirmation.

Track your orders via email.

Admin Panel

Access via /admin/login

Manage products, orders, and customers.

Screenshots & Demo

Home Page


Product Page


Cart


Admin Dashboard


Notes / Tips

Ensure your .env file is correctly configured for email notifications.

To reset your database, modify or delete JSON files in the data/ folder.

For production, use Gunicorn or uWSGI with Nginx instead of the Flask development server.

Prices are stored as float values in products.json; ensure correct rounding in calculations.

Dependencies

Flask

Flask-WTF

python-dotenv

Werkzeug (for password hashing)

License

This project is open-source and available under the MIT License.