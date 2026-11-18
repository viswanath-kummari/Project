from datetime import datetime, date
from flask import Blueprint, request, jsonify
from backend.models import db, Expense, Payment, Supplier, Customer
from backend.auth import admin_required, log_audit

finance_bp = Blueprint('finance', __name__, url_prefix='/api/finance')

@finance_bp.route('/expenses', methods=['GET'])
@admin_required
def get_expenses():
    category = request.args.get('category')
    query = Expense.query
    if category and category != 'all':
        query = query.filter_by(category=category)
    
    expenses = query.order_by(Expense.expense_date.desc()).limit(150).all()
    
    # Calculate category summary
    category_totals = {}
    total_amount = 0.0
    for exp in expenses:
        category_totals[exp.category] = round(category_totals.get(exp.category, 0.0) + exp.amount, 2)
        total_amount += exp.amount

    return jsonify({
        'expenses': [e.to_dict() for e in expenses],
        'total_amount': round(total_amount, 2),
        'category_totals': category_totals
    })

@finance_bp.route('/expenses', methods=['POST'])
@admin_required
def create_expense():
    data = request.get_json() or {}
    category = data.get('category', 'Other')
    amount = float(data.get('amount', 0.0))
    expense_date_str = data.get('expense_date')
    payment_method = data.get('payment_method', 'CASH').upper()
    description = data.get('description', '')
    receipt_reference = data.get('receipt_reference', '')

    if amount <= 0:
        return jsonify({'error': 'Expense amount must be greater than zero.'}), 400

    exp_date = date.today()
    if expense_date_str:
        try:
            exp_date = datetime.strptime(expense_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    exp = Expense(
        category=category,
        amount=amount,
        expense_date=exp_date,
        payment_method=payment_method,
        description=description,
        receipt_reference=receipt_reference,
        created_by=request.current_user.id
    )
    db.session.add(exp)
    db.session.commit()

    log_audit(request.current_user, 'EXPENSE_RECORDED', 'FINANCE', {'category': category, 'amount': amount})
    return jsonify({'message': 'Expense recorded successfully', 'expense': exp.to_dict()}), 201

@finance_bp.route('/expenses/<exp_id>', methods=['DELETE'])
@admin_required
def delete_expense(exp_id):
    exp = Expense.query.get_or_404(exp_id)
    db.session.delete(exp)
    db.session.commit()
    log_audit(request.current_user, 'EXPENSE_DELETED', 'FINANCE', {'id': exp_id, 'amount': exp.amount})
    return jsonify({'message': 'Expense record deleted.'})

@finance_bp.route('/payments', methods=['GET'])
@admin_required
def get_payments():
    p_type = request.args.get('type')
    query = Payment.query
    if p_type:
        query = query.filter_by(payment_type=p_type)
        
    payments = query.order_by(Payment.payment_date.desc()).limit(100).all()
    return jsonify({'payments': [p.to_dict() for p in payments]})

@finance_bp.route('/payments', methods=['POST'])
@admin_required
def create_payment():
    data = request.get_json() or {}
    payment_type = data.get('payment_type') # 'CUSTOMER_RECEIPT' or 'SUPPLIER_PAYMENT'
    reference_id = data.get('reference_id')
    amount = float(data.get('amount', 0.0))
    payment_method = data.get('payment_method', 'CASH').upper()
    notes = data.get('notes', '')
    transaction_ref = data.get('transaction_ref', '')

    if amount <= 0 or not payment_type:
        return jsonify({'error': 'Payment type and positive amount are required.'}), 400

    ref_name = ''
    if payment_type == 'SUPPLIER_PAYMENT' and reference_id:
        supplier = Supplier.query.get(reference_id)
        if supplier:
            ref_name = supplier.company_name
            supplier.outstanding_balance = max(0.0, round(supplier.outstanding_balance - amount, 2))
    elif payment_type == 'CUSTOMER_RECEIPT' and reference_id:
        cust = Customer.query.get(reference_id)
        if cust:
            ref_name = cust.name
            cust.pending_balance = max(0.0, round(cust.pending_balance - amount, 2))

    pay = Payment(
        payment_type=payment_type,
        reference_id=reference_id,
        reference_name=ref_name,
        amount=amount,
        payment_method=payment_method,
        transaction_ref=transaction_ref,
        notes=notes,
        created_by=request.current_user.id
    )
    db.session.add(pay)
    db.session.commit()

    log_audit(request.current_user, 'PAYMENT_RECORDED', 'FINANCE', {
        'type': payment_type,
        'amount': amount,
        'party': ref_name
    })

    return jsonify({'message': 'Payment recorded and ledger reconciled.', 'payment': pay.to_dict()}), 201
