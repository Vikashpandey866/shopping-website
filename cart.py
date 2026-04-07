"""
ShopVerse - Cart Routes
Add, update, remove cart items for authenticated users
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db, CartItem, Product

cart_bp = Blueprint('cart', __name__)


# ── Get Cart ────────────────────────────────────────────────────────────────────
@cart_bp.route('/', methods=['GET'])
@jwt_required()
def get_cart():
    user_id = int(get_jwt_identity())
    items = CartItem.query.filter_by(user_id=user_id).all()
    total = sum(i.product.price * i.quantity for i in items if i.product)
    return jsonify({
        'items': [i.to_dict() for i in items],
        'total': round(total, 2),
        'count': sum(i.quantity for i in items)
    })


# ── Add to Cart ─────────────────────────────────────────────────────────────────
@cart_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    product_id = data.get('product_id')
    quantity   = int(data.get('quantity', 1))
    
    if not product_id:
        return jsonify({'error': 'product_id required'}), 400
    
    product = Product.query.get_or_404(product_id)
    
    # Check stock
    if product.stock < quantity:
        return jsonify({'error': 'Insufficient stock'}), 400
    
    # Update existing or create new cart item
    item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(item)
    
    db.session.commit()
    return jsonify({'message': 'Added to cart', 'item': item.to_dict()})


# ── Update Quantity ─────────────────────────────────────────────────────────────
@cart_bp.route('/update/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(item_id):
    user_id = int(get_jwt_identity())
    item = CartItem.query.filter_by(id=item_id, user_id=user_id).first_or_404()
    data = request.get_json()
    quantity = int(data.get('quantity', 1))
    
    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = quantity
    
    db.session.commit()
    return jsonify({'message': 'Cart updated'})


# ── Remove Item ─────────────────────────────────────────────────────────────────
@cart_bp.route('/remove/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    user_id = int(get_jwt_identity())
    item = CartItem.query.filter_by(id=item_id, user_id=user_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item removed'})


# ── Clear Cart ──────────────────────────────────────────────────────────────────
@cart_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    user_id = int(get_jwt_identity())
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({'message': 'Cart cleared'})
