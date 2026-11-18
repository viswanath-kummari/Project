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

@auth_bp.route('/register', methods=['POST'])
@auth_bp.route('/signup', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    full_name = data.get('full_name', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'admin').lower()
    pin = data.get('pin', '').strip()
    phone = data.get('phone', '').strip()

    if not email or not full_name or not password:
        return jsonify({'error': 'Full Name, Email, and Password are required.'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long.'}), 400

    if '@' not in email or '.' not in email:
        return jsonify({'error': 'Please provide a valid email address.'}), 400

    if Profile.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with this email address already exists. Please sign in.'}), 400

    # Auto-generate or sanitize 4-digit PIN for touch POS sign-in
    import random
    if not pin or len(pin) != 4 or not pin.isdigit():
        pin = str(random.randint(1000, 9999))
    else:
        existing_pin = Profile.query.filter_by(pin=pin, is_active=True).first()
        if existing_pin:
            pin = str(random.randint(1000, 9999))

    new_user = Profile(
        email=email,
        full_name=full_name,
        role=role if role in ('admin', 'employee') else 'admin',
        pin=pin,
        password_hash=hash_password(password),
        phone=phone,
        is_active=True
    )
    db.session.add(new_user)
    db.session.commit()

    token = create_access_token(new_user)
    log_audit(new_user, 'USER_REGISTERED', 'AUTH', {'email': new_user.email, 'role': new_user.role})

    return jsonify({
        'message': f'Welcome to Fresh Cut, {new_user.full_name}! Account created successfully.',
        'token': token,
        'user': new_user.to_dict()
    }), 201

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
