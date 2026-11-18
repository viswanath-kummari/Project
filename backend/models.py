import uuid
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), unique=True, nullable=True) # Supabase auth user uuid
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True) # local secure hash
    full_name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='employee') # 'admin' or 'employee'
    pin = db.Column(db.String(10), default='1234')
    phone = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)
    updated_at = db.Column(db.DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'pin': self.pin,
            'phone': self.phone,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False) # 'poultry', 'mutton', 'seafood', 'deli'
    unit = db.Column(db.String(20), nullable=False, default='KG') # 'KG' or 'PCS'
    cost_price = db.Column(db.Float, nullable=False, default=0.0)
    selling_price = db.Column(db.Float, nullable=False, default=0.0)
    min_stock_level = db.Column(db.Float, nullable=False, default=5.0)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)
    updated_at = db.Column(db.DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            'id': str(self.id),
            'sku': self.sku,
            'name': self.name,
            'category': self.category,
            'unit': self.unit,
            'cost_price': round(float(self.cost_price), 2),
            'selling_price': round(float(self.selling_price), 2),
            'min_stock_level': round(float(self.min_stock_level), 3),
            'description': self.description or '',
            'image_url': self.image_url or '',
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(255), nullable=True)
    address = db.Column(db.Text, nullable=True)
    total_spent = db.Column(db.Float, nullable=False, default=0.0)
    loyalty_points = db.Column(db.Integer, nullable=False, default=0)
    pending_balance = db.Column(db.Float, nullable=False, default=0.0)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)
    updated_at = db.Column(db.DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'phone': self.phone,
            'email': self.email or '',
            'address': self.address or '',
            'total_spent': round(float(self.total_spent), 2),
            'loyalty_points': self.loyalty_points,
            'pending_balance': round(float(self.pending_balance), 2),
            'notes': self.notes or '',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    company_name = db.Column(db.String(150), nullable=False)
    contact_person = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    address = db.Column(db.Text, nullable=True)
    gst_or_tax_id = db.Column(db.String(50), nullable=True)
    outstanding_balance = db.Column(db.Float, nullable=False, default=0.0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)
    updated_at = db.Column(db.DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            'id': str(self.id),
            'company_name': self.company_name,
            'contact_person': self.contact_person or '',
            'phone': self.phone,
            'email': self.email or '',
            'address': self.address or '',
            'gst_or_tax_id': self.gst_or_tax_id or '',
            'outstanding_balance': round(float(self.outstanding_balance), 2),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), unique=True, nullable=False)
    current_stock = db.Column(db.Float, nullable=False, default=0.0)
    unit = db.Column(db.String(20), nullable=False, default='KG')
    last_restocked_at = db.Column(db.DateTime(timezone=True), nullable=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    product = db.relationship('Product', backref=db.backref('inventory_item', uselist=False))

    def to_dict(self):
        return {
            'id': str(self.id),
            'product_id': str(self.product_id),
            'product_name': self.product.name if self.product else 'Unknown',
            'sku': self.product.sku if self.product else '',
            'category': self.product.category if self.product else '',
            'cost_price': round(float(self.product.cost_price), 2) if self.product else 0.0,
            'selling_price': round(float(self.product.selling_price), 2) if self.product else 0.0,
            'min_stock_level': round(float(self.product.min_stock_level), 3) if self.product else 5.0,
            'current_stock': round(float(self.current_stock), 3),
            'unit': self.unit,
            'status': 'out_of_stock' if self.current_stock <= 0 else ('low_stock' if self.product and self.current_stock <= self.product.min_stock_level else 'in_stock'),
            'last_restocked_at': self.last_restocked_at.isoformat() if self.last_restocked_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=True)
    employee_id = db.Column(db.String(36), db.ForeignKey('profiles.id'), nullable=True)
    employee_name = db.Column(db.String(150), nullable=True)
    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    discount_amount = db.Column(db.Float, nullable=False, default=0.0)
    tax_amount = db.Column(db.Float, nullable=False, default=0.0)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    total_cogs = db.Column(db.Float, nullable=False, default=0.0)
    payment_method = db.Column(db.String(50), nullable=False, default='CASH') # CASH, UPI, CARD, SPLIT
    payment_status = db.Column(db.String(50), nullable=False, default='PAID')
    cash_tendered = db.Column(db.Float, default=0.0)
    change_returned = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)

    customer = db.relationship('Customer', backref=db.backref('sales', lazy=True))
    items = db.relationship('SaleItem', backref='sale', cascade='all, delete-orphan', lazy=True)

    def to_dict(self):
        return {
            'id': str(self.id),
            'invoice_number': self.invoice_number,
            'customer_id': str(self.customer_id) if self.customer_id else None,
            'customer_name': self.customer.name if self.customer else 'Walk-in Customer',
            'customer_phone': self.customer.phone if self.customer else '',
            'employee_id': str(self.employee_id) if self.employee_id else None,
            'employee_name': self.employee_name or 'Cashier',
            'subtotal': round(float(self.subtotal), 2),
            'discount_amount': round(float(self.discount_amount), 2),
            'tax_amount': round(float(self.tax_amount), 2),
            'total_amount': round(float(self.total_amount), 2),
            'total_cogs': round(float(self.total_cogs), 2),
            'gross_margin': round(float(self.total_amount - self.total_cogs), 2),
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'cash_tendered': round(float(self.cash_tendered or 0.0), 2),
            'change_returned': round(float(self.change_returned or 0.0), 2),
            'notes': self.notes or '',
            'item_count': len(self.items),
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SaleItem(db.Model):
    __tablename__ = 'sale_items'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    sale_id = db.Column(db.String(36), db.ForeignKey('sales.id'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=True)
    product_name = db.Column(db.String(150), nullable=False)
    sku = db.Column(db.String(50), nullable=True)
    unit = db.Column(db.String(20), nullable=False, default='KG')
    quantity = db.Column(db.Float, nullable=False)
    unit_cost_price = db.Column(db.Float, nullable=False, default=0.0)
    unit_selling_price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)

    def to_dict(self):
        return {
            'id': str(self.id),
            'sale_id': str(self.sale_id),
            'product_id': str(self.product_id) if self.product_id else None,
            'product_name': self.product_name,
            'sku': self.sku or '',
            'unit': self.unit,
            'quantity': round(float(self.quantity), 3),
            'unit_cost_price': round(float(self.unit_cost_price), 2),
            'unit_selling_price': round(float(self.unit_selling_price), 2),
            'subtotal': round(float(self.subtotal), 2)
        }

class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    purchase_invoice_no = db.Column(db.String(100), nullable=False)
    supplier_id = db.Column(db.String(36), db.ForeignKey('suppliers.id'), nullable=True)
    supplier_name = db.Column(db.String(150), nullable=True)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    paid_amount = db.Column(db.Float, nullable=False, default=0.0)
    payment_status = db.Column(db.String(50), nullable=False, default='PAID')
    purchase_date = db.Column(db.DateTime(timezone=True), default=utc_now)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.String(36), db.ForeignKey('profiles.id'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)

    supplier = db.relationship('Supplier', backref=db.backref('purchases', lazy=True))
    items = db.relationship('PurchaseItem', backref='purchase', cascade='all, delete-orphan', lazy=True)

    def to_dict(self):
        return {
            'id': str(self.id),
            'purchase_invoice_no': self.purchase_invoice_no,
            'supplier_id': str(self.supplier_id) if self.supplier_id else None,
            'supplier_name': self.supplier_name or (self.supplier.company_name if self.supplier else 'Direct Farm'),
            'total_amount': round(float(self.total_amount), 2),
            'paid_amount': round(float(self.paid_amount), 2),
            'payment_status': self.payment_status,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'notes': self.notes or '',
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PurchaseItem(db.Model):
    __tablename__ = 'purchase_items'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    purchase_id = db.Column(db.String(36), db.ForeignKey('purchases.id'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=True)
    product_name = db.Column(db.String(150), nullable=False)
    unit = db.Column(db.String(20), nullable=False, default='KG')
    quantity = db.Column(db.Float, nullable=False)
    unit_cost_price = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': str(self.id),
            'purchase_id': str(self.purchase_id),
            'product_id': str(self.product_id) if self.product_id else None,
            'product_name': self.product_name,
            'unit': self.unit,
            'quantity': round(float(self.quantity), 3),
            'unit_cost_price': round(float(self.unit_cost_price), 2),
            'total_cost': round(float(self.total_cost), 2)
        }

class StockMovement(db.Model):
    __tablename__ = 'stock_movements'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    movement_type = db.Column(db.String(50), nullable=False) # 'PURCHASE', 'SALE', 'WASTAGE', 'RETURN', 'ADJUSTMENT'
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False, default='KG')
    previous_stock = db.Column(db.Float, nullable=False)
    new_stock = db.Column(db.Float, nullable=False)
    reference_id = db.Column(db.String(100), nullable=True)
    reason = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.String(36), db.ForeignKey('profiles.id'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)

    product = db.relationship('Product', backref=db.backref('stock_movements', lazy=True))

    def to_dict(self):
        return {
            'id': str(self.id),
            'product_id': str(self.product_id),
            'product_name': self.product.name if self.product else 'Unknown Product',
            'movement_type': self.movement_type,
            'quantity': round(float(self.quantity), 3),
            'unit': self.unit,
            'previous_stock': round(float(self.previous_stock), 3),
            'new_stock': round(float(self.new_stock), 3),
            'reference_id': self.reference_id or '',
            'reason': self.reason or '',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    expense_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False, default='CASH')
    description = db.Column(db.Text, nullable=True)
    receipt_reference = db.Column(db.String(100), nullable=True)
    created_by = db.Column(db.String(36), db.ForeignKey('profiles.id'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)

    def to_dict(self):
        return {
            'id': str(self.id),
            'category': self.category,
            'amount': round(float(self.amount), 2),
            'expense_date': self.expense_date.isoformat() if self.expense_date else None,
            'payment_method': self.payment_method,
            'description': self.description or '',
            'receipt_reference': self.receipt_reference or '',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    payment_type = db.Column(db.String(50), nullable=False) # 'CUSTOMER_RECEIPT', 'SUPPLIER_PAYMENT'
    reference_id = db.Column(db.String(36), nullable=True)
    reference_name = db.Column(db.String(150), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime(timezone=True), default=utc_now)
    payment_method = db.Column(db.String(50), nullable=False, default='CASH')
    transaction_ref = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.String(36), db.ForeignKey('profiles.id'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)

    def to_dict(self):
        return {
            'id': str(self.id),
            'payment_type': self.payment_type,
            'reference_id': str(self.reference_id) if self.reference_id else None,
            'reference_name': self.reference_name or '',
            'amount': round(float(self.amount), 2),
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method,
            'transaction_ref': self.transaction_ref or '',
            'notes': self.notes or '',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Setting(db.Model):
    __tablename__ = 'settings'
    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.JSON, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), nullable=True)
    user_name = db.Column(db.String(150), nullable=True)
    role = db.Column(db.String(50), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    module = db.Column(db.String(100), nullable=False)
    details = db.Column(db.JSON, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id) if self.user_id else None,
            'user_name': self.user_name or 'System',
            'role': self.role or 'system',
            'action': self.action,
            'module': self.module,
            'details': self.details or {},
            'ip_address': self.ip_address or '',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
