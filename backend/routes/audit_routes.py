from flask import Blueprint, request, jsonify
from backend.models import AuditLog
from backend.auth import admin_required

audit_bp = Blueprint('audit', __name__, url_prefix='/api/audit')

@audit_bp.route('', methods=['GET'])
@admin_required
def get_audit_logs():
    module = request.args.get('module')
    action = request.args.get('action')

    query = AuditLog.query
    if module and module != 'all':
        query = query.filter_by(module=module)
    if action:
        query = query.filter(AuditLog.action.ilike(f'%{action}%'))

    logs = query.order_by(AuditLog.created_at.desc()).limit(150).all()
    return jsonify({'audit_logs': [l.to_dict() for l in logs]})
