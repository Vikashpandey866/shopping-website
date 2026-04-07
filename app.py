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
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    
    # ── Configuration ──────────────────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'shopverse-super-secret-key-2024')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'shopverse-jwt-secret-2024')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopverse.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens don't expire (for demo)

    # Ensure uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ── Extensions ─────────────────────────────────────────────────────────────
    CORS(app, origins='*', supports_credentials=True)
    JWTManager(app)
    db.init_app(app)

    # ── Blueprints ─────────────────────────────────────────────────────────────
    app.register_blueprint(auth_bp,     url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(cart_bp,     url_prefix='/api/cart')
    app.register_blueprint(orders_bp,   url_prefix='/api/orders')
    app.register_blueprint(admin_bp,    url_prefix='/api/admin')

    # ── Serve uploaded images ───────────────────────────────────────────────────
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # ── Serve frontend (SPA catch-all) ─────────────────────────────────────────
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
        if path and os.path.exists(os.path.join(frontend_dir, path)):
            return send_from_directory(frontend_dir, path)
        return send_from_directory(frontend_dir, 'index.html')

    # ── Init DB & seed data ─────────────────────────────────────────────────────
    with app.app_context():
        init_db(app)

    return app


if __name__ == '__main__':
    app = create_app()
    print("🛍️  ShopVerse server running at http://localhost:5000")
    app.run(debug=True, port=5000)
