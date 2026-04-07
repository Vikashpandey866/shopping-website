"""
ShopVerse - Admin Routes
Dashboard stats, user management, order management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db, User, Product, Order, OrderItem
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)


def require_admin():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        from flask import abort
        abort(403, description='Admin access required')
    return user


# ── Dashboard Stats ─────────────────────────────────────────────────────────────
@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def dashboard_stats():
    require_admin()
    
    total_revenue = db.session.query(func.sum(Order.total)).filter_by(status='paid').scalar() or 0
    
    return jsonify({
        'total_users':    User.query.count(),
        'total_products': Product.query.count(),
        'total_orders':   Order.query.count(),
        'total_revenue':  round(total_revenue, 2),
        'low_stock':      Product.query.filter(Product.stock < 5).count()
    })


# ── All Users ───────────────────────────────────────────────────────────────────
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    require_admin()
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users])


# ── All Orders ──────────────────────────────────────────────────────────────────
@admin_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_all_orders():
    require_admin()
    orders = Order.query.order_by(Order.created_at.desc()).all()
    result = []
    for o in orders:
        d = o.to_dict()
        d['user_name'] = o.user.name if o.user else 'Unknown'
        d['user_email'] = o.user.email if o.user else ''
        result.append(d)
    return jsonify(result)


# ── Update Order Status ─────────────────────────────────────────────────────────
@admin_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    require_admin()
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    order.status = data.get('status', order.status)
    db.session.commit()
    return jsonify({'message': 'Order status updated', 'order': order.to_dict()})


# ── Delete User ─────────────────────────────────────────────────────────────────
@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    require_admin()
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})
