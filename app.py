from flask import Flask, session, render_template
from routes.main import main_bp
from routes.admin import admin_bp
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from config import Config
import os

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

csrf = CSRFProtect(app)

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(admin_bp)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
