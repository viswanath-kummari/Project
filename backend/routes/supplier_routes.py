from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from backend.models import db, Supplier, Purchase, PurchaseItem, Product, Inventory, StockMovement, Payment
from backend.auth import token_required, admin_required, log_audit

supplier_bp = Blueprint('suppliers', __name__, url_prefix='/api/suppliers')

@supplier_bp.route('', methods=['GET'])
@token_required
def get_suppliers():
    suppliers = Supplier.query.order_by(Supplier.company_name.asc()).all()
    return jsonify({'suppliers': [s.to_dict() for s in suppliers]})

@supplier_bp.route('', methods=['POST'])
@admin_required
def create_supplier():
    data = request.get_json() or {}
    company_name = data.get('company_name', '').strip()
    contact_person = data.get('contact_person', '').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip()
    address = data.get('address', '').strip()
    gst_or_tax_id = data.get('gst_or_tax_id', '').strip()

    if not company_name or not phone:
        return jsonify({'error': 'Supplier company name and phone are required.'}), 400

    s = Supplier(
        company_name=company_name,
        contact_person=contact_person,
        phone=phone,
        email=email,
        address=address,
        gst_or_tax_id=gst_or_tax_id,
        outstanding_balance=0.0
    )
    db.session.add(s)
    db.session.commit()

    log_audit(request.current_user, 'SUPPLIER_CREATED', 'SUPPLIERS', {'company_name': company_name})
    return jsonify({'message': 'Supplier created successfully', 'supplier': s.to_dict()}), 201

@supplier_bp.route('/<supplier_id>', methods=['GET'])
@admin_required
def get_supplier_detail(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    purchases = Purchase.query.filter_by(supplier_id=supplier.id).order_by(Purchase.purchase_date.desc()).limit(15).all()
    d = supplier.to_dict()
    d['purchases'] = [p.to_dict() for p in purchases]
    return jsonify({'supplier': d})

@supplier_bp.route('/<supplier_id>', methods=['PUT'])
@admin_required
def update_supplier(supplier_id):
    s = Supplier.query.get_or_404(supplier_id)
    data = request.get_json() or {}

    if 'company_name' in data:
        s.company_name = data['company_name']
    if 'contact_person' in data:
        s.contact_person = data['contact_person']
    if 'phone' in data:
        s.phone = data['phone']
    if 'email' in data:
        s.email = data['email']
    if 'address' in data:
        s.address = data['address']
    if 'gst_or_tax_id' in data:
        s.gst_or_tax_id = data['gst_or_tax_id']
    if 'outstanding_balance' in data:
        s.outstanding_balance = float(data['outstanding_balance'])

    db.session.commit()
    return jsonify({'message': 'Supplier updated successfully', 'supplier': s.to_dict()})

# Purchases and Stock Intake
@supplier_bp.route('/purchases', methods=['GET'])
@admin_required
def list_purchases():
    purchases = Purchase.query.order_by(Purchase.created_at.desc()).limit(100).all()
    return jsonify({'purchases': [p.to_dict() for p in purchases]})

@supplier_bp.route('/purchases', methods=['POST'])
@admin_required
def record_purchase():
    """Create purchase order intake, restock inventory, and adjust supplier ledger"""
    data = request.get_json() or {}
    supplier_id = data.get('supplier_id')
    invoice_no = data.get('purchase_invoice_no', f"PO-{int(datetime.now().timestamp())}")
    items = data.get('items', [])
    paid_amount = float(data.get('paid_amount', 0.0))
    notes = data.get('notes', '')

    if not items:
        return jsonify({'error': 'No items in purchase intake.'}), 400

    supplier = None
    if supplier_id:
        supplier = Supplier.query.get(supplier_id)

    total_amount = 0.0
    for it in items:
        total_amount += round(float(it['quantity']) * float(it['unit_cost_price']), 2)

    payment_status = 'PAID' if paid_amount >= total_amount else ('PARTIAL' if paid_amount > 0 else 'PENDING')
    due_amount = max(0.0, total_amount - paid_amount)

    purchase = Purchase(
        purchase_invoice_no=invoice_no,
        supplier_id=supplier.id if supplier else None,
        supplier_name=supplier.company_name if supplier else 'Direct Farm / Wholesale',
        total_amount=total_amount,
        paid_amount=paid_amount,
        payment_status=payment_status,
        notes=notes,
        created_by=request.current_user.id
    )
    db.session.add(purchase)
    db.session.flush()

    # Update supplier balance
    if supplier and due_amount > 0:
        supplier.outstanding_balance = round(supplier.outstanding_balance + due_amount, 2)

    # Add items, update inventory and stock movements
    for it in items:
        prod = Product.query.get(it['product_id'])
        if not prod:
            continue
        qty = float(it['quantity'])
        cost = float(it['unit_cost_price'])

        # Optionally update cost price on product
        prod.cost_price = cost

        p_item = PurchaseItem(
            purchase_id=purchase.id,
            product_id=prod.id,
            product_name=prod.name,
            unit=prod.unit,
            quantity=qty,
            unit_cost_price=cost,
            total_cost=round(qty * cost, 2)
        )
        db.session.add(p_item)

        inv = Inventory.query.filter_by(product_id=prod.id).first()
        if not inv:
            inv = Inventory(product_id=prod.id, current_stock=0.0, unit=prod.unit)
            db.session.add(inv)
            db.session.flush()

        prev_stock = inv.current_stock
        new_stock = round(prev_stock + qty, 3)
        inv.current_stock = new_stock
        inv.last_restocked_at = datetime.now(timezone.utc)

        mov = StockMovement(
            product_id=prod.id,
            movement_type='PURCHASE',
            quantity=qty,
            unit=prod.unit,
            previous_stock=prev_stock,
            new_stock=new_stock,
            reference_id=invoice_no,
            reason=f"Purchase Intake #{invoice_no} ({supplier.company_name if supplier else 'Direct'})",
            created_by=request.current_user.id
        )
        db.session.add(mov)

    db.session.commit()
    log_audit(request.current_user, 'PURCHASE_INTAKE', 'PURCHASES', {
        'invoice_no': invoice_no,
        'total': total_amount,
        'supplier': supplier.company_name if supplier else 'Direct'
    })

    return jsonify({'message': 'Purchase intake recorded and stock updated.', 'purchase': purchase.to_dict()}), 201
