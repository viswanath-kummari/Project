from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from backend.models import db, Profile
from backend.auth import create_access_token, token_required, admin_required, log_audit
from backend.database import hash_password, verify_password

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    pin = data.get('pin', '').strip()

    user = None
    if pin:
        user = Profile.query.filter_by(pin=pin, is_active=True).first()
    elif email:
        user = Profile.query.filter_by(email=email).first()
        if user and user.password_hash and not verify_password(password, user.password_hash):
            return jsonify({'error': 'Invalid credentials. Please verify your password.'}), 401
    
    if not user:
        return jsonify({'error': 'Account not found or invalid credentials.'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'This employee account is deactivated. Contact Administrator.'}), 403

    user.last_login = datetime.now(timezone.utc)
    db.session.commit()

    token = create_access_token(user)
    log_audit(user, 'USER_LOGIN', 'AUTH', {'email': user.email, 'role': user.role})

    return jsonify({
        'token': token,
        'user': user.to_dict()
    })

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    return jsonify({'user': request.current_user.to_dict()})

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    log_audit(request.current_user, 'USER_LOGOUT', 'AUTH', {'email': request.current_user.email})
    return jsonify({'message': 'Logged out successfully'})

@auth_bp.route('/employees', methods=['GET'])
@admin_required
def list_employees():
    employees = Profile.query.order_by(Profile.created_at.desc()).all()
    return jsonify({'employees': [e.to_dict() for e in employees]})

@auth_bp.route('/employees', methods=['POST'])
@admin_required
def create_employee():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    full_name = data.get('full_name', '').strip()
    role = data.get('role', 'employee')
    pin = data.get('pin', '1234').strip()
    password = data.get('password', 'FreshCut2026!')
    phone = data.get('phone', '')

    if not email or not full_name:
        return jsonify({'error': 'Email and Full Name are required.'}), 400

    if Profile.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with this email already exists.'}), 400

    new_emp = Profile(
        email=email,
        full_name=full_name,
        role=role if role in ('admin', 'employee') else 'employee',
        pin=pin,
        password_hash=hash_password(password),
        phone=phone,
        is_active=True
    )
    db.session.add(new_emp)
    db.session.commit()

    log_audit(request.current_user, 'EMPLOYEE_CREATED', 'STAFF', {
        'new_employee_id': new_emp.id,
        'email': new_emp.email,
        'role': new_emp.role
    })

    return jsonify({'message': 'Employee created successfully', 'employee': new_emp.to_dict()}), 201

@auth_bp.route('/employees/<emp_id>', methods=['PUT'])
@admin_required
def update_employee(emp_id):
    emp = Profile.query.get_or_404(emp_id)
    data = request.get_json() or {}

    if 'full_name' in data:
        emp.full_name = data['full_name']
    if 'role' in data and data['role'] in ('admin', 'employee'):
        emp.role = data['role']
    if 'pin' in data:
        emp.pin = str(data['pin'])
    if 'phone' in data:
        emp.phone = data['phone']
    if 'is_active' in data:
        emp.is_active = bool(data['is_active'])
    if 'password' in data and data['password']:
        emp.password_hash = hash_password(data['password'])

    db.session.commit()
    log_audit(request.current_user, 'EMPLOYEE_UPDATED', 'STAFF', {'target_id': emp.id, 'email': emp.email})
    return jsonify({'message': 'Employee updated successfully', 'employee': emp.to_dict()})
