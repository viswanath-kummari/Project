from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from backend.models import db, Inventory, Product, StockMovement
from backend.auth import token_required, admin_required, log_audit

inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/inventory')

@inventory_bp.route('', methods=['GET'])
@token_required
def get_inventory():
    """List current stock balances, categories, thresholds and alerts"""
    category = request.args.get('category')
    filter_status = request.args.get('status') # 'low_stock', 'out_of_stock', 'in_stock'
    search = request.args.get('search')

    query = Inventory.query.join(Product, Inventory.product_id == Product.id)
    if category and category != 'all':
        query = query.filter(Product.category == category)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%') | Product.sku.ilike(f'%{search}%'))

    records = query.all()
    results = []
    
    low_stock_count = 0
    out_of_stock_count = 0
    total_stock_kg = 0.0
    total_stock_pcs = 0.0

    for item in records:
        d = item.to_dict()
        if d['status'] == 'low_stock':
            low_stock_count += 1
        elif d['status'] == 'out_of_stock':
            out_of_stock_count += 1

        if d['unit'] == 'KG':
            total_stock_kg += d['current_stock']
        else:
            total_stock_pcs += d['current_stock']

        if filter_status and d['status'] != filter_status:
            continue
        results.append(d)

    return jsonify({
        'inventory': results,
        'summary': {
            'total_items': len(results),
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'total_stock_kg': round(total_stock_kg, 3),
            'total_stock_pcs': int(total_stock_pcs)
        }
    })

@inventory_bp.route('/adjustment', methods=['POST'])
@admin_required
def adjust_stock():
    """Admin records incoming stock, inventory recount, or manual correction"""
    data = request.get_json() or {}
    product_id = data.get('product_id')
    adjustment_type = data.get('type', 'ADJUSTMENT') # 'PURCHASE', 'ADJUSTMENT'
    quantity = float(data.get('quantity', 0.0))
    reason = data.get('reason', '').strip()

    if not product_id or quantity == 0:
        return jsonify({'error': 'Product and non-zero quantity are required.'}), 400

    inv = Inventory.query.filter_by(product_id=product_id).first_or_404()
    prod = Product.query.get(product_id)

    prev_stock = inv.current_stock
    new_stock = round(prev_stock + quantity, 3)

    if new_stock < 0:
        return jsonify({'error': f"Stock cannot be reduced below zero. Current stock is {prev_stock} {prod.unit}."}), 400

    inv.current_stock = new_stock
    inv.last_restocked_at = datetime.now(timezone.utc)

    mov = StockMovement(
        product_id=prod.id,
        movement_type=adjustment_type,
        quantity=quantity,
        unit=prod.unit,
        previous_stock=prev_stock,
        new_stock=new_stock,
        reference_id=f"MANUAL-{int(datetime.now().timestamp())}",
        reason=reason or f"Manual stock adjustment ({'+' if quantity > 0 else ''}{quantity} {prod.unit})",
        created_by=request.current_user.id
    )
    db.session.add(mov)
    db.session.commit()

    log_audit(request.current_user, 'STOCK_ADJUSTED', 'INVENTORY', {
        'product': prod.name,
        'adjustment': quantity,
        'previous': prev_stock,
        'new': new_stock,
        'reason': reason
    })

    return jsonify({
        'message': f"Stock for {prod.name} updated to {new_stock} {prod.unit}.",
        'inventory': inv.to_dict()
    })

@inventory_bp.route('/wastage', methods=['POST'])
@token_required
def record_wastage():
    """Record spoilage, trimming losses, bone scrap, or expired meat with mandatory reason"""
    data = request.get_json() or {}
    product_id = data.get('product_id')
    quantity = float(data.get('quantity', 0.0))
    reason = data.get('reason', '').strip()

    if not product_id or quantity <= 0:
        return jsonify({'error': 'Product ID and positive quantity are required.'}), 400

    if not reason:
        return jsonify({'error': 'A detailed reason is mandatory when recording wastage or spoilage.'}), 400

    inv = Inventory.query.filter_by(product_id=product_id).first_or_404()
    prod = Product.query.get(product_id)

    prev_stock = inv.current_stock
    if prev_stock < quantity:
        return jsonify({'error': f"Cannot write off {quantity} {prod.unit}. Available stock is only {prev_stock} {prod.unit}."}), 400

    new_stock = round(prev_stock - quantity, 3)
    inv.current_stock = new_stock

    mov = StockMovement(
        product_id=prod.id,
        movement_type='WASTAGE',
        quantity=-quantity,
        unit=prod.unit,
        previous_stock=prev_stock,
        new_stock=new_stock,
        reference_id=f"WASTAGE-{int(datetime.now().timestamp())}",
        reason=reason,
        created_by=request.current_user.id
    )
    db.session.add(mov)
    db.session.commit()

    log_audit(request.current_user, 'WASTAGE_RECORDED', 'INVENTORY', {
        'product': prod.name,
        'quantity': quantity,
        'reason': reason
    })

    return jsonify({
        'message': f"Recorded {quantity} {prod.unit} wastage for {prod.name}.",
        'inventory': inv.to_dict()
    })

@inventory_bp.route('/movements', methods=['GET'])
@token_required
def get_movements():
    """Audit ledger of all stock incoming, sales, and wastage movements"""
    product_id = request.args.get('product_id')
    mov_type = request.args.get('type')
    
    query = StockMovement.query
    if product_id:
        query = query.filter_by(product_id=product_id)
    if mov_type and mov_type != 'all':
        query = query.filter_by(movement_type=mov_type)

    movements = query.order_by(StockMovement.created_at.desc()).limit(150).all()
    return jsonify({'movements': [m.to_dict() for m in movements]})
