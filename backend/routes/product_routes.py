from flask import Blueprint, request, jsonify
from backend.models import db, Product, Inventory, StockMovement
from backend.auth import token_required, admin_required, log_audit

product_bp = Blueprint('products', __name__, url_prefix='/api/products')

@product_bp.route('', methods=['GET'])
@token_required
def get_products():
    category = request.args.get('category')
    search = request.args.get('search')
    is_admin = (request.current_user.role == 'admin')

    query = Product.query
    if not is_admin:
        query = query.filter_by(is_active=True)

    if category and category != 'all':
        query = query.filter_by(category=category)

    if search:
        query = query.filter(Product.name.ilike(f'%{search}%') | Product.sku.ilike(f'%{search}%'))

    products = query.order_by(Product.name.asc()).all()

    # Join stock from inventory
    result = []
    for p in products:
        p_dict = p.to_dict()
        if not is_admin:
            # Hide cost price from regular employees
            p_dict.pop('cost_price', None)
        
        # Attach current stock
        inv = Inventory.query.filter_by(product_id=p.id).first()
        p_dict['current_stock'] = round(float(inv.current_stock), 3) if inv else 0.0
        p_dict['stock_status'] = 'out_of_stock' if p_dict['current_stock'] <= 0 else (
            'low_stock' if p_dict['current_stock'] <= p.min_stock_level else 'in_stock'
        )
        result.append(p_dict)

    return jsonify({'products': result})

@product_bp.route('/<product_id>', methods=['GET'])
@token_required
def get_product_detail(product_id):
    p = Product.query.get_or_404(product_id)
    p_dict = p.to_dict()
    if request.current_user.role != 'admin':
        p_dict.pop('cost_price', None)
    inv = Inventory.query.filter_by(product_id=p.id).first()
    p_dict['current_stock'] = round(float(inv.current_stock), 3) if inv else 0.0
    return jsonify({'product': p_dict})

@product_bp.route('', methods=['POST'])
@admin_required
def create_product():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    sku = data.get('sku', '').strip()
    category = data.get('category', 'poultry')
    unit = data.get('unit', 'KG').upper()
    selling_price = float(data.get('selling_price', 0.0))
    cost_price = float(data.get('cost_price', 0.0))
    min_stock_level = float(data.get('min_stock_level', 5.0))
    initial_stock = float(data.get('initial_stock', 0.0))
    description = data.get('description', '')
    image_url = data.get('image_url', '').strip()

    if not name or not sku:
        return jsonify({'error': 'Product name and SKU are required.'}), 400

    if unit not in ('KG', 'PCS'):
        return jsonify({'error': 'Unit must be either KG or PCS.'}), 400

    if category == 'beef' or 'beef' in name.lower():
        return jsonify({'error': 'Beef products are not allowed in this system.'}), 400

    if Product.query.filter_by(sku=sku).first():
        return jsonify({'error': f'Product with SKU {sku} already exists.'}), 400

    prod = Product(
        name=name,
        sku=sku,
        category=category,
        unit=unit,
        selling_price=selling_price,
        cost_price=cost_price,
        min_stock_level=min_stock_level,
        description=description,
        image_url=image_url,
        is_active=True
    )
    db.session.add(prod)
    db.session.flush()

    # Create associated inventory record
    inv = Inventory(
        product_id=prod.id,
        current_stock=initial_stock,
        unit=unit
    )
    db.session.add(inv)

    if initial_stock > 0:
        mov = StockMovement(
            product_id=prod.id,
            movement_type='PURCHASE',
            quantity=initial_stock,
            unit=unit,
            previous_stock=0.0,
            new_stock=initial_stock,
            reference_id='INITIAL-STOCK',
            reason='Initial catalog setup stock balance',
            created_by=request.current_user.id
        )
        db.session.add(mov)

    db.session.commit()
    log_audit(request.current_user, 'PRODUCT_CREATED', 'PRODUCTS', {'sku': sku, 'name': name})
    return jsonify({'message': 'Product created successfully', 'product': prod.to_dict()}), 201

@product_bp.route('/<product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    prod = Product.query.get_or_404(product_id)
    data = request.get_json() or {}

    if 'name' in data:
        prod.name = data['name'].strip()
    if 'category' in data:
        prod.category = data['category']
    if 'unit' in data and data['unit'].upper() in ('KG', 'PCS'):
        prod.unit = data['unit'].upper()
    if 'selling_price' in data:
        prod.selling_price = float(data['selling_price'])
    if 'cost_price' in data:
        prod.cost_price = float(data['cost_price'])
    if 'min_stock_level' in data:
        prod.min_stock_level = float(data['min_stock_level'])
    if 'description' in data:
        prod.description = data['description']
    if 'image_url' in data:
        prod.image_url = data['image_url'].strip()
    if 'is_active' in data:
        prod.is_active = bool(data['is_active'])

    db.session.commit()
    log_audit(request.current_user, 'PRODUCT_UPDATED', 'PRODUCTS', {'product_id': prod.id, 'sku': prod.sku})
    return jsonify({'message': 'Product updated successfully', 'product': prod.to_dict()})

@product_bp.route('/<product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    prod = Product.query.get_or_404(product_id)
    prod.is_active = False # Safe deactivation for audit preservation (SRS FR-10)
    db.session.commit()
    log_audit(request.current_user, 'PRODUCT_DEACTIVATED', 'PRODUCTS', {'product_id': prod.id, 'sku': prod.sku})
    return jsonify({'message': 'Product deactivated successfully'})
