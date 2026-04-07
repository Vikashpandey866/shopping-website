"""
ShopVerse - Orders Routes
Checkout, order history, mock payment integration
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db, Order, OrderItem, CartItem, Product
import uuid

orders_bp = Blueprint('orders', __name__)


# ── Create Order (Checkout) ─────────────────────────────────────────────────────
@orders_bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    address = data.get('address', '')
    
    # Get user's cart
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400
    
    # Validate stock and calculate total
    total = 0
    for item in cart_items:
        if item.product.stock < item.quantity:
            return jsonify({'error': f'Insufficient stock for {item.product.name}'}), 400
        total += item.product.price * item.quantity
    
    # Mock payment - generate a fake payment ID
    # In production: integrate Razorpay/Stripe here
    payment_id = f'PAY-{uuid.uuid4().hex[:12].upper()}'
    
    # Create order
    order = Order(
        user_id=user_id,
        total=round(total, 2),
        status='paid',
        payment_id=payment_id,
        address=address
    )
    db.session.add(order)
    db.session.flush()  # Get order.id before commit
    
    # Create order items and decrement stock
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=cart_item.product.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )
        # Fix: order_item should reference order, not product
        order_item.order_id = order.id
        cart_item.product.stock -= cart_item.quantity
        db.session.add(order_item)
    
    # Clear the cart
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    return jsonify({
        'message': 'Order placed successfully',
        'order': order.to_dict(),
        'payment_id': payment_id
    }), 201


# ── Get Order History ───────────────────────────────────────────────────────────
@orders_bp.route('/history', methods=['GET'])
@jwt_required()
def order_history():
    user_id = int(get_jwt_identity())
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders])


# ── Get Single Order ────────────────────────────────────────────────────────────
@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    user_id = int(get_jwt_identity())
    order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()
    return jsonify(order.to_dict())


# ── Mock Payment Verify ─────────────────────────────────────────────────────────
@orders_bp.route('/verify-payment', methods=['POST'])
@jwt_required()
def verify_payment():
    """
    Mock payment verification endpoint.
    In production: verify Razorpay signature here.
    """
    data = request.get_json()
    # Always return success for mock
    return jsonify({
        'verified': True,
        'message': 'Payment verified (mock)',
        'payment_id': data.get('payment_id')
    })
