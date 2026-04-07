"""
ShopVerse - Database Models
SQLAlchemy models for Users, Products, Orders, Cart
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

# ── User Model ──────────────────────────────────────────────────────────────────
class User(db.Model):
    __tablename__ = 'users'
    
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(255), nullable=False)           # bcrypt hash
    is_admin   = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade='all, delete')
    orders     = db.relationship('Order', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id':         self.id,
            'name':       self.name,
            'email':      self.email,
            'is_admin':   self.is_admin,
            'created_at': self.created_at.isoformat()
        }


# ── Product Model ───────────────────────────────────────────────────────────────
class Product(db.Model):
    __tablename__ = 'products'
    
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price       = db.Column(db.Float, nullable=False)
    category    = db.Column(db.String(50), nullable=False)
    stock       = db.Column(db.Integer, default=0)
    image       = db.Column(db.String(300), default='')   # URL or path
    rating      = db.Column(db.Float, default=4.0)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cart_items  = db.relationship('CartItem', backref='product', lazy=True, cascade='all, delete')
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    def to_dict(self):
        return {
            'id':          self.id,
            'name':        self.name,
            'description': self.description,
            'price':       self.price,
            'category':    self.category,
            'stock':       self.stock,
            'image':       self.image,
            'rating':      self.rating,
            'created_at':  self.created_at.isoformat()
        }


# ── Cart Item Model ─────────────────────────────────────────────────────────────
class CartItem(db.Model):
    __tablename__ = 'cart_items'
    
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity   = db.Column(db.Integer, default=1)
    added_at   = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':         self.id,
            'product_id': self.product_id,
            'quantity':   self.quantity,
            'product':    self.product.to_dict() if self.product else None
        }


# ── Order Model ─────────────────────────────────────────────────────────────────
class Order(db.Model):
    __tablename__ = 'orders'
    
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total          = db.Column(db.Float, nullable=False)
    status         = db.Column(db.String(50), default='pending')   # pending|paid|shipped|delivered
    payment_id     = db.Column(db.String(200), default='')         # Razorpay / mock ID
    address        = db.Column(db.Text, default='')
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete')

    def to_dict(self):
        return {
            'id':         self.id,
            'user_id':    self.user_id,
            'total':      self.total,
            'status':     self.status,
            'payment_id': self.payment_id,
            'address':    self.address,
            'created_at': self.created_at.isoformat(),
            'items':      [i.to_dict() for i in self.items]
        }


# ── Order Item Model ────────────────────────────────────────────────────────────
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity   = db.Column(db.Integer, nullable=False)
    price      = db.Column(db.Float, nullable=False)   # price at time of purchase

    def to_dict(self):
        return {
            'id':         self.id,
            'product_id': self.product_id,
            'quantity':   self.quantity,
            'price':      self.price,
            'product':    self.product.to_dict() if self.product else None
        }


# ── Database Initialization & Seed Data ────────────────────────────────────────
def init_db(app):
    """Create tables and seed initial data if DB is empty."""
    db.create_all()
    
    # Seed only if no products exist
    if Product.query.count() == 0:
        _seed_data()


def _seed_data():
    """Insert demo products and admin user."""
    from werkzeug.security import generate_password_hash
    
    # Admin user
    admin = User(
        name='Admin User',
        email='admin@shopverse.com',
        password=generate_password_hash('admin123'),
        is_admin=True
    )
    db.session.add(admin)

    # Demo products
    products = [
        Product(name='Premium Wireless Headphones', description='High-fidelity sound with 40hr battery life, active noise cancellation, and premium leather ear cushions.', price=2499, category='Electronics', stock=50, image='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400', rating=4.8),
        Product(name='Mechanical Keyboard RGB', description='Tactile switches with per-key RGB lighting. Compact 75% layout perfect for gaming and coding.', price=3999, category='Electronics', stock=30, image='https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=400', rating=4.6),
        Product(name='Minimalist Leather Watch', description='Genuine leather strap, sapphire crystal glass, Swiss quartz movement. Water resistant to 50m.', price=5999, category='Fashion', stock=20, image='https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400', rating=4.7),
        Product(name='Running Shoes Pro X', description='Ultra-lightweight foam sole with adaptive fit system. Perfect for long-distance running.', price=4499, category='Sports', stock=45, image='https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400', rating=4.5),
        Product(name='Ceramic Coffee Mug Set', description='Set of 4 handcrafted ceramic mugs. Microwave and dishwasher safe. 350ml capacity each.', price=899, category='Home', stock=100, image='https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=400', rating=4.3),
        Product(name='Smart Fitness Tracker', description='24/7 heart rate monitoring, sleep tracking, 7-day battery. Water resistant. Compatible with iOS & Android.', price=1999, category='Electronics', stock=60, image='https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=400', rating=4.4),
        Product(name='Linen Throw Blanket', description='100% organic linen, naturally breathable and gets softer with every wash. 150cm x 200cm.', price=1299, category='Home', stock=80, image='https://images.unsplash.com/photo-1543722530-d2c3201371e7?w=400', rating=4.6),
        Product(name='Yoga Mat Premium', description='6mm thick non-slip surface with alignment lines. Eco-friendly natural rubber, includes carry strap.', price=1599, category='Sports', stock=55, image='https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400', rating=4.7),
        Product(name='Sunglasses Aviator Gold', description='Polarized UV400 lenses with gold titanium frame. Classic aviator style with modern precision optics.', price=2199, category='Fashion', stock=35, image='https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=400', rating=4.5),
        Product(name='Plant-Based Protein Powder', description='25g protein per serving, no artificial flavors. Chocolate and vanilla variants. 1kg pack.', price=1899, category='Sports', stock=90, image='https://images.unsplash.com/photo-1612540139150-4b0f5a1c9b8c?w=400', rating=4.2),
        Product(name='Portable Bluetooth Speaker', description='360° surround sound, IPX7 waterproof, 20hr playtime. Perfect for outdoors and travel.', price=2799, category='Electronics', stock=40, image='https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400', rating=4.6),
        Product(name='Linen Button-Up Shirt', description='Relaxed fit, 100% European linen. Breathable and perfect for warm weather. Available S-XXL.', price=1799, category='Fashion', stock=65, image='https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400', rating=4.4),
    ]
    
    for p in products:
        db.session.add(p)
    
    db.session.commit()
    print("✅ Database seeded with demo data")
