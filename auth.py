"""
ShopVerse - E-Commerce Backend
Main Flask Application Entry Point
"""

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from database import db, init_db
from routes.auth import auth_bp
from routes.products import products_bp
from routes.cart import cart_bp
from routes.orders import orders_bp
from routes.admin import admin_bp
import os

def create_app():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # 🔥 ROOT folder hi frontend hai
    app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')

    # ── Configuration ─────────────────────────
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'shopverse-secret')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopverse.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ── Extensions ────────────────────────────
    CORS(app)
    JWTManager(app)
    db.init_app(app)

    # ── Blueprints ────────────────────────────
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # ── Upload route ─────────────────────────
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # 🔥 FRONTEND FIX (ROOT se serve karega)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path != "" and os.path.exists(os.path.join(BASE_DIR, path)):
            return send_from_directory(BASE_DIR, path)
        return send_from_directory(BASE_DIR, 'index.html')

    # ── DB Init ──────────────────────────────
    with app.app_context():
        init_db(app)

    return app


# ✅ REQUIRED for Railway (Gunicorn)
app = create_app()


# ✅ Local + Railway compatible run
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
