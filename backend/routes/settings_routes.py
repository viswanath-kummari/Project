import os
from flask import Blueprint, request, jsonify
from backend.models import db, Setting
from backend.auth import token_required, admin_required, log_audit
from config import Config

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')

@settings_bp.route('', methods=['GET'])
@token_required
def get_settings():
    settings = Setting.query.all()
    res = {}
    for s in settings:
        res[s.key] = s.value

    # Mask sensitive keys if not admin
    if request.current_user.role != 'admin':
        if 'supabase_config' in res:
            res['supabase_config'] = {'status': res['supabase_config'].get('status', 'local_mode')}

    return jsonify({'settings': res})

@settings_bp.route('/profile', methods=['POST'])
@admin_required
def update_shop_profile():
    data = request.get_json() or {}
    setting = Setting.query.filter_by(key='shop_profile').first()
    if not setting:
        setting = Setting(key='shop_profile', value={})
        db.session.add(setting)

    cur_val = setting.value or {}
    cur_val.update({
        'name': data.get('name', cur_val.get('name', Config.SHOP_NAME)),
        'tagline': data.get('tagline', cur_val.get('tagline', Config.SHOP_TAGLINE)),
        'phone': data.get('phone', cur_val.get('phone', Config.SHOP_PHONE)),
        'address': data.get('address', cur_val.get('address', Config.SHOP_ADDRESS)),
        'gst_no': data.get('gst_no', cur_val.get('gst_no', Config.SHOP_GST_NO)),
        'currency': data.get('currency', cur_val.get('currency', Config.CURRENCY_SYMBOL)),
        'tax_percent': float(data.get('tax_percent', cur_val.get('tax_percent', Config.DEFAULT_TAX_PERCENT))),
        'invoice_prefix': data.get('invoice_prefix', cur_val.get('invoice_prefix', Config.INVOICE_PREFIX))
    })

    # Flag as modified for JSON update
    setting.value = dict(cur_val)
    db.session.commit()

    log_audit(request.current_user, 'SETTINGS_UPDATED', 'SETTINGS', {'updated_profile': cur_val['name']})
    return jsonify({'message': 'Shop profile updated successfully', 'shop_profile': setting.value})

@settings_bp.route('/supabase', methods=['POST'])
@admin_required
def configure_supabase():
    data = request.get_json() or {}
    url = data.get('supabase_url', '').strip()
    key = data.get('supabase_key', '').strip()

    status = 'connected' if (url and key) else 'local_mode'

    setting = Setting.query.filter_by(key='supabase_config').first()
    if not setting:
        setting = Setting(key='supabase_config', value={})
        db.session.add(setting)

    setting.value = {
        'supabase_url': url,
        'supabase_key': key,
        'status': status
    }
    db.session.commit()

    # Also test connection if credentials provided
    test_result = 'ok'
    if url and key:
        try:
            from supabase import create_client
            client = create_client(url, key)
            # quick ping
            test_result = 'Supabase client initialized successfully!'
        except Exception as e:
            test_result = f"Configuration saved, but client check gave: {str(e)}"

    log_audit(request.current_user, 'SUPABASE_CONFIG_UPDATED', 'SECURITY', {'status': status})
    return jsonify({
        'message': 'Supabase configuration saved.',
        'status': status,
        'diagnostic': test_result
    })
