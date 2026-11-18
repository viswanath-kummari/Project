import os
from flask import Flask, render_template, jsonify
from config import Config
from backend.models import db
from backend.database import seed_database_if_empty
from backend.routes.auth_routes import auth_bp
from backend.routes.product_routes import product_bp
from backend.routes.pos_routes import pos_bp
from backend.routes.inventory_routes import inventory_bp
from backend.routes.customer_routes import customer_bp
from backend.routes.supplier_routes import supplier_bp
from backend.routes.finance_routes import finance_bp
from backend.routes.report_routes import report_bp
from backend.routes.settings_routes import settings_bp
from backend.routes.audit_routes import audit_bp

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)

    # Initialize Database
    db.init_app(app)

    # Simple CORS header injection for future mobile/cross-origin clients
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        return response

    # Register API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(pos_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(supplier_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(audit_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'version': '1.1.0',
            'app': 'Fresh Cut Meat Shop Management System',
            'mobile_ready': True
        })

    # Error Handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Resource or endpoint not found'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Internal server error occurred'}), 500

    # Auto-create tables & seed demo data
    with app.app_context():
        db.create_all()
        seed_database_if_empty()

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[STARTING] Fresh Cut Meat Shop server starting on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
