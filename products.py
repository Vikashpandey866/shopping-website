"""
ShopVerse - Products Routes
CRUD operations, search, filter, and image upload
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from werkzeug.utils import secure_filename
from database import db, Product, User
import os, uuid

products_bp = Blueprint('products', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ── List / Search / Filter Products ────────────────────────────────────────────
@products_bp.route('/', methods=['GET'])
def get_products():
    query    = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by  = request.args.get('sort', 'created_at')   # price_asc|price_desc|rating|name
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    
    q = Product.query
    
    # Text search across name and description
    if query:
        like = f'%{query}%'
        q = q.filter(db.or_(Product.name.ilike(like), Product.description.ilike(like)))
    
    if category:
        q = q.filter_by(category=category)
    if min_price is not None:
        q = q.filter(Product.price >= min_price)
    if max_price is not None:
        q = q.filter(Product.price <= max_price)
    
    # Sorting
    sort_map = {
        'price_asc':  Product.price.asc(),
        'price_desc': Product.price.desc(),
        'rating':     Product.rating.desc(),
        'name':       Product.name.asc(),
        'created_at': Product.created_at.desc()
    }
    q = q.order_by(sort_map.get(sort_by, Product.created_at.desc()))
    
    paginated = q.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'products':    [p.to_dict() for p in paginated.items],
        'total':       paginated.total,
        'pages':       paginated.pages,
        'current_page': page
    })


# ── Get Categories ──────────────────────────────────────────────────────────────
@products_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = db.session.query(Product.category).distinct().all()
    return jsonify([c[0] for c in categories])


# ── Get Single Product ──────────────────────────────────────────────────────────
@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())


# ── Create Product (Admin only) ─────────────────────────────────────────────────
@products_bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    user = _get_admin_user()
    
    # Handle both JSON and form-data (for image upload)
    if request.is_json:
        data = request.get_json()
        image_url = data.get('image', '')
    else:
        data = request.form.to_dict()
        image_url = _handle_image_upload() or data.get('image', '')
    
    product = Product(
        name=data['name'],
        description=data['description'],
        price=float(data['price']),
        category=data['category'],
        stock=int(data.get('stock', 0)),
        image=image_url,
        rating=float(data.get('rating', 4.0))
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Product created', 'product': product.to_dict()}), 201


# ── Update Product (Admin only) ─────────────────────────────────────────────────
@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    _get_admin_user()
    product = Product.query.get_or_404(product_id)
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
        new_image = _handle_image_upload()
        if new_image:
            product.image = new_image
    
    for field in ['name', 'description', 'category']:
        if field in data:
            setattr(product, field, data[field])
    if 'price' in data:
        product.price = float(data['price'])
    if 'stock' in data:
        product.stock = int(data['stock'])
    if 'rating' in data:
        product.rating = float(data['rating'])
    if 'image' in data and request.is_json:
        product.image = data['image']
    
    db.session.commit()
    return jsonify({'message': 'Product updated', 'product': product.to_dict()})


# ── Delete Product (Admin only) ─────────────────────────────────────────────────
@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    _get_admin_user()
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'})


# ── Upload Product Image ────────────────────────────────────────────────────────
@products_bp.route('/upload-image', methods=['POST'])
@jwt_required()
def upload_image():
    _get_admin_user()
    url = _handle_image_upload()
    if not url:
        return jsonify({'error': 'No valid image file provided'}), 400
    return jsonify({'url': url})


# ── Helpers ─────────────────────────────────────────────────────────────────────
def _get_admin_user():
    """Verify JWT and return admin user, else abort 403."""
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        from flask import abort
        abort(403, description='Admin access required')
    return user


def _handle_image_upload():
    """Save uploaded image file and return its URL path."""
    file = request.files.get('image')
    if not file or not allowed_file(file.filename):
        return None
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    return f'/uploads/{filename}'
