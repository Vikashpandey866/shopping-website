"""
ShopVerse - Authentication Routes
Handles user registration, login, and profile management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User

auth_bp = Blueprint('auth', __name__)


# ── Register ────────────────────────────────────────────────────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    for field in ['name', 'email', 'password']:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check duplicate email
    if User.query.filter_by(email=data['email'].lower()).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create user with hashed password
    user = User(
        name=data['name'].strip(),
        email=data['email'].lower().strip(),
        password=generate_password_hash(data['password'])
    )
    db.session.add(user)
    db.session.commit()
    
    # Issue JWT token immediately
    token = create_access_token(identity=str(user.id))
    return jsonify({
        'message': 'Account created successfully',
        'token': token,
        'user': user.to_dict()
    }), 201


# ── Login ───────────────────────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=data['email'].lower()).first()
    
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    token = create_access_token(identity=str(user.id))
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    })


# ── Get Current User Profile ────────────────────────────────────────────────────
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())


# ── Update Profile ──────────────────────────────────────────────────────────────
@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if data.get('name'):
        user.name = data['name'].strip()
    if data.get('password'):
        user.password = generate_password_hash(data['password'])
    
    db.session.commit()
    return jsonify({'message': 'Profile updated', 'user': user.to_dict()})
