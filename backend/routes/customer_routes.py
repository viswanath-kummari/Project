from flask import Blueprint, request, jsonify
from backend.models import db, Customer, Sale
from backend.auth import token_required, admin_required, log_audit

customer_bp = Blueprint('customers', __name__, url_prefix='/api/customers')

@customer_bp.route('', methods=['GET'])
@token_required
def get_customers():
    search = request.args.get('search')
    query = Customer.query
    if search:
        query = query.filter(Customer.name.ilike(f'%{search}%') | Customer.phone.ilike(f'%{search}%'))
    
    customers = query.order_by(Customer.name.asc()).all()
    return jsonify({'customers': [c.to_dict() for c in customers]})

@customer_bp.route('/<customer_id>', methods=['GET'])
@token_required
def get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    cust_data = customer.to_dict()

    # Employee limited access, Admin gets full sales history & pending ledger
    if request.current_user.role == 'admin':
        sales = Sale.query.filter_by(customer_id=customer.id).order_by(Sale.created_at.desc()).limit(20).all()
        cust_data['recent_sales'] = [s.to_dict() for s in sales]
        
    return jsonify({'customer': cust_data})

@customer_bp.route('', methods=['POST'])
@token_required
def create_customer():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip()
    address = data.get('address', '').strip()
    notes = data.get('notes', '').strip()

    if not name or not phone:
        return jsonify({'error': 'Customer name and phone number are required.'}), 400

    existing = Customer.query.filter_by(phone=phone).first()
    if existing:
        return jsonify({'error': f'Customer with phone {phone} already exists.', 'customer': existing.to_dict()}), 400

    new_cust = Customer(
        name=name,
        phone=phone,
        email=email,
        address=address,
        notes=notes
    )
    db.session.add(new_cust)
    db.session.commit()

    log_audit(request.current_user, 'CUSTOMER_CREATED', 'CUSTOMERS', {'name': name, 'phone': phone})
    return jsonify({'message': 'Customer registered successfully', 'customer': new_cust.to_dict()}), 201

@customer_bp.route('/<customer_id>', methods=['PUT'])
@admin_required
def update_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json() or {}

    if 'name' in data:
        customer.name = data['name'].strip()
    if 'phone' in data:
        customer.phone = data['phone'].strip()
    if 'email' in data:
        customer.email = data['email'].strip()
    if 'address' in data:
        customer.address = data['address'].strip()
    if 'notes' in data:
        customer.notes = data['notes'].strip()
    if 'pending_balance' in data:
        customer.pending_balance = float(data['pending_balance'])

    db.session.commit()
    log_audit(request.current_user, 'CUSTOMER_UPDATED', 'CUSTOMERS', {'id': customer.id, 'name': customer.name})
    return jsonify({'message': 'Customer updated successfully', 'customer': customer.to_dict()})
