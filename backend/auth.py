from functools import wraps
from datetime import datetime, timedelta, timezone
import jwt
from flask import request, jsonify
from backend.models import Profile, AuditLog, db
from config import Config

def create_access_token(profile: Profile) -> str:
    """Generate JWT signed token containing user identity and role"""
    payload = {
        'sub': str(profile.id),
        'email': profile.email,
        'name': profile.full_name,
        'role': profile.role,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(hours=Config.JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication token missing or invalid header'}), 401
        
        token = auth_header.split(' ')[1].strip()
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Token has expired or is invalid. Please sign in again.'}), 401
        
        user = db.session.get(Profile, payload['sub'])
        if not user or not user.is_active:
            return jsonify({'error': 'Account not found or has been deactivated.'}), 403
        
        request.current_user = user
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        
        token = auth_header.split(' ')[1].strip()
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        user = db.session.get(Profile, payload['sub'])
        if not user or not user.is_active:
            return jsonify({'error': 'Account inactive'}), 403
        
        if user.role != 'admin':
            # Strict SRS requirement: Non-admin users cannot access admin endpoints
            log_audit(user, 'UNAUTHORIZED_ACCESS_ATTEMPT', 'SECURITY', {
                'endpoint': request.path,
                'method': request.method,
                'message': 'Employee attempted to access admin-restricted resource'
            })
            return jsonify({'error': 'Access denied: Admin role required for this action'}), 403
        
        request.current_user = user
        return f(*args, **kwargs)
    return decorated

def log_audit(user, action: str, module: str, details: dict = None):
    """Immutable audit logging utility"""
    try:
        ip = request.remote_addr if request else '127.0.0.1'
        log = AuditLog(
            user_id=user.id if user else None,
            user_name=user.full_name if user else 'System',
            role=user.role if user else 'system',
            action=action,
            module=module,
            details=details or {},
            ip_address=ip
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Failed to record audit log: {e}")
