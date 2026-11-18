import random
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from backend.models import db, Sale, SaleItem, Product, Inventory, StockMovement, Customer, Setting
from backend.auth import token_required, admin_required, log_audit
from config import Config

pos_bp = Blueprint('pos', __name__, url_prefix='/api/pos')

def generate_invoice_number():
    """Format: FC-YYYYMMDD-XXXX with auto-increment check"""
    today_str = datetime.now().strftime('%Y%m%d')
    prefix = Config.INVOICE_PREFIX
    # Count sales today
    count_today = Sale.query.filter(Sale.invoice_number.like(f"{prefix}{today_str}-%")).count() + 1
    return f"{prefix}{today_str}-{count_today:04d}"

@pos_bp.route('/calculate', methods=['POST'])
@token_required
def calculate_cart():
    """Preview totals, taxes, and validate item quantities before checkout"""
    data = request.get_json() or {}
    items = data.get('items', [])
    discount_amount = float(data.get('discount_amount', 0.0))
    tax_percent = float(data.get('tax_percent', Config.DEFAULT_TAX_PERCENT))

    subtotal = 0.0
    evaluated_items = []

    for it in items:
        p_id = it.get('product_id')
        qty = float(it.get('quantity', 1.0))
        prod = db.session.get(Product, p_id)
        if not prod:
            return jsonify({'error': f"Product ID {p_id} not found"}), 404
        
        # Enforce integer for piece-based items
        if prod.unit == 'PCS':
            qty = round(qty)
            if qty < 1:
                qty = 1.0
        else:
            qty = round(qty, 3) # 3 decimals for KG (e.g. 1.250 KG)
            if qty <= 0:
                return jsonify({'error': f"Invalid quantity for {prod.name}"}), 400

        line_sub = round(qty * prod.selling_price, 2)
        subtotal += line_sub

        evaluated_items.append({
            'product_id': prod.id,
            'name': prod.name,
            'sku': prod.sku,
            'unit': prod.unit,
            'unit_price': prod.selling_price,
            'quantity': qty,
            'subtotal': line_sub
        })

    taxable_amount = max(0.0, subtotal - discount_amount)
    tax_amount = round(taxable_amount * (tax_percent / 100.0), 2)
    grand_total = round(taxable_amount + tax_amount, 2)

    return jsonify({
        'items': evaluated_items,
        'subtotal': round(subtotal, 2),
        'discount_amount': round(discount_amount, 2),
        'tax_percent': tax_percent,
        'tax_amount': tax_amount,
        'grand_total': grand_total
    })

@pos_bp.route('/checkout', methods=['POST'])
@token_required
def checkout():
    """Complete a POS sale atomically, reducing stock and issuing invoice"""
    data = request.get_json() or {}
    items = data.get('items', [])
    customer_id = data.get('customer_id')
    payment_method = data.get('payment_method', 'CASH').upper()
    discount_amount = float(data.get('discount_amount', 0.0))
    cash_tendered = float(data.get('cash_tendered', 0.0))
    notes = data.get('notes', '')

    if not items:
        return jsonify({'error': 'Cart is empty. Add at least one product.'}), 400

    if payment_method not in ('CASH', 'UPI', 'CARD', 'SPLIT', 'CREDIT'):
        return jsonify({'error': 'Unsupported payment method.'}), 400

    try:
        subtotal = 0.0
        total_cogs = 0.0
        prepared_sale_items = []
        stock_updates = []

        # 1. Validate items and verify available stock
        for it in items:
            prod = db.session.get(Product, it['product_id'])
            if not prod or not prod.is_active:
                return jsonify({'error': f"Product {it.get('product_id')} is not available."}), 400

            qty = float(it['quantity'])
            if prod.unit == 'PCS':
                qty = round(qty)
            else:
                qty = round(qty, 3)

            if qty <= 0:
                return jsonify({'error': f"Quantity for {prod.name} must be greater than zero."}), 400

            inv = Inventory.query.filter_by(product_id=prod.id).first()
            if not inv:
                inv = Inventory(product_id=prod.id, current_stock=0.0, unit=prod.unit)
                db.session.add(inv)
                db.session.flush()

            # Prevent negative stock (SRS Business Rules 9)
            if inv.current_stock < qty:
                return jsonify({
                    'error': f"Insufficient stock for '{prod.name}'. Available: {inv.current_stock:.3f} {prod.unit}, Requested: {qty:.3f} {prod.unit}"
                }), 400

            line_sub = round(qty * prod.selling_price, 2)
            line_cogs = round(qty * prod.cost_price, 2)
            subtotal += line_sub
            total_cogs += line_cogs

            prepared_sale_items.append({
                'product': prod,
                'inventory': inv,
                'qty': qty,
                'unit_selling_price': prod.selling_price,
                'unit_cost_price': prod.cost_price,
                'subtotal': line_sub
            })

        # 2. Financial calculation
        tax_percent = Config.DEFAULT_TAX_PERCENT
        taxable_amount = max(0.0, subtotal - discount_amount)
        tax_amount = round(taxable_amount * (tax_percent / 100.0), 2)
        grand_total = round(taxable_amount + tax_amount, 2)

        change_returned = 0.0
        if payment_method == 'CASH':
            if cash_tendered < grand_total:
                cash_tendered = grand_total
            change_returned = round(cash_tendered - grand_total, 2)

        # 3. Create Sale Header
        invoice_no = generate_invoice_number()
        sale = Sale(
            invoice_number=invoice_no,
            customer_id=customer_id if customer_id else None,
            employee_id=request.current_user.id,
            employee_name=request.current_user.full_name,
            subtotal=subtotal,
            discount_amount=discount_amount,
            tax_amount=tax_amount,
            total_amount=grand_total,
            total_cogs=total_cogs,
            payment_method=payment_method,
            payment_status='PAID' if payment_method != 'CREDIT' else 'PENDING',
            cash_tendered=cash_tendered,
            change_returned=change_returned,
            notes=notes
        )
        db.session.add(sale)
        db.session.flush()

        # 4. Create Sale Items and Atomically Decrement Inventory
        for prep in prepared_sale_items:
            prod = prep['product']
            inv = prep['inventory']
            qty = prep['qty']

            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=prod.id,
                product_name=prod.name,
                sku=prod.sku,
                unit=prod.unit,
                quantity=qty,
                unit_cost_price=prep['unit_cost_price'],
                unit_selling_price=prep['unit_selling_price'],
                subtotal=prep['subtotal']
            )
            db.session.add(sale_item)

            # Record stock decrement
            prev_stock = inv.current_stock
            new_stock = round(prev_stock - qty, 3)
            inv.current_stock = new_stock

            movement = StockMovement(
                product_id=prod.id,
                movement_type='SALE',
                quantity=-qty,
                unit=prod.unit,
                previous_stock=prev_stock,
                new_stock=new_stock,
                reference_id=invoice_no,
                reason=f"POS Sale Invoice #{invoice_no}",
                created_by=request.current_user.id
            )
            db.session.add(movement)

        # 5. Customer Loyalty Points update if customer present
        if customer_id:
            cust = db.session.get(Customer, customer_id)
            if cust:
                cust.total_spent = round(cust.total_spent + grand_total, 2)
                # 1 point per 100 spent
                cust.loyalty_points += int(grand_total // 100)
                if payment_method == 'CREDIT':
                    cust.pending_balance = round(cust.pending_balance + grand_total, 2)

        db.session.commit()

        log_audit(request.current_user, 'POS_SALE_COMPLETED', 'POS', {
            'invoice_number': invoice_no,
            'total_amount': grand_total,
            'payment_method': payment_method,
            'item_count': len(items)
        })

        return jsonify({
            'message': 'Sale completed successfully!',
            'sale': sale.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Failed to complete sale: {str(e)}"}), 500

@pos_bp.route('/history', methods=['GET'])
@token_required
def billing_history():
    """Retrieve billing history. Admins get all; Employees get own sales only."""
    query = Sale.query
    if request.current_user.role != 'admin':
        # SRS requirement: Employee views own sales history only
        query = query.filter_by(employee_id=request.current_user.id)
    
    invoice_filter = request.args.get('invoice')
    if invoice_filter:
        query = query.filter(Sale.invoice_number.ilike(f'%{invoice_filter}%'))

    sales = query.order_by(Sale.created_at.desc()).limit(100).all()
    return jsonify({'sales': [s.to_dict() for s in sales]})

@pos_bp.route('/invoice/<invoice_number>', methods=['GET'])
@token_required
def get_invoice(invoice_number):
    sale = Sale.query.filter_by(invoice_number=invoice_number).first_or_404()
    if request.current_user.role != 'admin' and sale.employee_id != request.current_user.id:
        return jsonify({'error': 'Unauthorized to view this invoice'}), 403
    return jsonify({'sale': sale.to_dict()})

@pos_bp.route('/refund', methods=['POST'])
@admin_required
def process_refund():
    """SRS FR-22: Cancellations, refunds and corrections create auditable reversals; do not silently delete history."""
    data = request.get_json() or {}
    invoice_no = data.get('invoice_number')
    reason = data.get('reason', 'Customer return')

    sale = Sale.query.filter_by(invoice_number=invoice_no).first_or_404()
    if sale.payment_status == 'CANCELLED':
        return jsonify({'error': 'Invoice is already cancelled/refunded.'}), 400

    # Restock items and record movement
    for item in sale.items:
        if item.product_id:
            inv = Inventory.query.filter_by(product_id=item.product_id).first()
            if inv:
                prev_stock = inv.current_stock
                new_stock = round(prev_stock + item.quantity, 3)
                inv.current_stock = new_stock

                movement = StockMovement(
                    product_id=item.product_id,
                    movement_type='RETURN',
                    quantity=item.quantity,
                    unit=item.unit,
                    previous_stock=prev_stock,
                    new_stock=new_stock,
                    reference_id=f"REFUND-{invoice_no}",
                    reason=f"Refund/Return for {invoice_no}: {reason}",
                    created_by=request.current_user.id
                )
                db.session.add(movement)

    sale.payment_status = 'CANCELLED'
    db.session.commit()

    log_audit(request.current_user, 'SALE_REFUNDED', 'POS', {'invoice': invoice_no, 'reason': reason})
    return jsonify({'message': f'Invoice {invoice_no} has been refunded and stock restored.', 'sale': sale.to_dict()})
