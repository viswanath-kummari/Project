import os
import hashlib
from datetime import datetime, timedelta, timezone, date
from backend.models import db, Profile, Product, Customer, Supplier, Inventory, Sale, SaleItem, Purchase, PurchaseItem, StockMovement, Expense, Payment, Setting, AuditLog
from config import Config

# Optional Supabase client instance
supabase_client = None

def get_supabase_client():
    global supabase_client
    if supabase_client is not None:
        return supabase_client
    
    url = Config.SUPABASE_URL
    key = Config.SUPABASE_SERVICE_ROLE_KEY or Config.SUPABASE_KEY
    if url and key:
        try:
            from supabase import create_client
            supabase_client = create_client(url, key)
            return supabase_client
        except Exception as e:
            print(f"Warning: Failed to connect to Supabase: {e}")
            return None
    return None

def hash_password(password: str) -> str:
    """Hash password with sha256 + salt for secure local authentication"""
    salt = "fresh_cut_artisanal_salt_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def seed_database_if_empty():
    """Seed comprehensive, realistic fresh cut meat shop catalog & transactions"""
    if Profile.query.first() is not None:
        return # Already seeded
    
    print("[SEED] Seeding Fresh Cut Meat Shop database with realistic catalog, inventory & demo records...")
    
    # 1. Default Profiles (Admin and Employee)
    admin_user = Profile(
        email='admin@freshcut.com',
        password_hash=hash_password('AdminPassword123!'),
        full_name='Viswanath',
        role='admin',
        pin='1234',
        phone='+91 98765 00001',
        is_active=True
    )
    
    employee_user = Profile(
        email='cashier@freshcut.com',
        password_hash=hash_password('CashierPassword123!'),
        full_name='Hemanth',
        role='employee',
        pin='5678',
        phone='+91 98765 00002',
        is_active=True
    )
    
    db.session.add(admin_user)
    db.session.add(employee_user)
    db.session.flush()

    # 2. Comprehensive Meat & Seafood Product Catalog
    products_data = [
        # Poultry (KG & Pieces)
        {
            'sku': 'CHK-BRS-01',
            'name': 'Farm Fresh Chicken Breast (Boneless)',
            'category': 'poultry',
            'unit': 'KG',
            'cost_price': 220.00,
            'selling_price': 340.00,
            'min_stock_level': 10.0,
            'initial_stock': 28.500,
            'description': 'Tender, skinless and boneless chicken breast fillets, trimmed of excess fat.',
            'image_url': 'https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80'
        },
        {
            'sku': 'CHK-CUR-02',
            'name': 'Country Chicken Curry Cut (Skinless)',
            'category': 'poultry',
            'unit': 'KG',
            'cost_price': 160.00,
            'selling_price': 260.00,
            'min_stock_level': 15.0,
            'initial_stock': 42.000,
            'description': 'Even bite-sized bone-in chicken cuts perfect for rich slow-cooked curries.',
            'image_url': 'https://images.unsplash.com/photo-1587593810167-a84920ea0781?auto=format&fit=crop&w=400&q=80'
        },
        {
            'sku': 'CHK-DRM-03',
            'name': 'Chicken Drumsticks (Tender Cuts)',
            'category': 'poultry',
            'unit': 'KG',
            'cost_price': 190.00,
            'selling_price': 295.00,
            'min_stock_level': 8.0,
            'initial_stock': 18.250,
            'description': 'Juicy bone-in lower leg cuts, skinless and ready for tandoor or roasting.',
            'image_url': 'https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80'
        },
        {
            'sku': 'CHK-WNG-04',
            'name': 'Crispy Cut Chicken Wings',
            'category': 'poultry',
            'unit': 'KG',
            'cost_price': 150.00,
            'selling_price': 240.00,
            'min_stock_level': 5.0,
            'initial_stock': 4.500, # Low stock alert trigger
            'description': 'Fresh chicken wingettes and drumettes, ideal for grilling and deep frying.',
            'image_url': 'https://images.unsplash.com/photo-1567620832903-9fc6debc209f?auto=format&fit=crop&w=400&q=80'
        },
        {
            'sku': 'CHK-WHL-05',
            'name': 'Whole Spring Chicken (Dressed)',
            'category': 'poultry',
            'unit': 'PCS',
            'cost_price': 180.00,
            'selling_price': 280.00,
            'min_stock_level': 6.0,
            'initial_stock': 14.000,
            'description': 'Plump whole spring chicken cleaned and gutted (approx 850g - 950g each).',
            'image_url': 'https://images.unsplash.com/photo-1516684732162-798a0062be99?auto=format&fit=crop&w=400&q=80'
        },
        # Mutton & Lamb (KG)
        {
            'sku': 'MUT-CUR-01',
            'name': 'Prime Goat Mutton Curry Cut (Bone-in)',
            'category': 'mutton',
            'unit': 'KG',
            'cost_price': 650.00,
            'selling_price': 890.00,
            'min_stock_level': 10.0,
            'initial_stock': 24.750,
            'description': 'Rich pasture-raised goat meat cuts including ribs, shoulder, and shank chunks.',
            'image_url': 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80'
        },
        {
            'sku': 'MUT-CHP-02',
            'name': 'Lamb Rib Chops (French Trimmed)',
            'category': 'mutton',
            'unit': 'KG',
            'cost_price': 780.00,
            'selling_price': 1150.00,
            'min_stock_level': 5.0,
            'initial_stock': 8.200,
            'description': 'Succulent bone-in lamb chops carefully trimmed for searing or gourmet braising.',
            'image_url': 'https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=400&q=80'
        },
        {
            'sku': 'MUT-MNC-03',
            'name': 'Fine Hand-Minced Mutton (Keema)',
            'category': 'mutton',
            'unit': 'KG',
            'cost_price': 680.00,
            'selling_price': 940.00,
            'min_stock_level': 6.0,
            'initial_stock': 12.000,
            'description': 'Double-ground lean goat leg meat for kebabs, samosas, and keema mattar.',
            'image_url': 'https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?auto=format&fit=crop&w=400&q=80'
        },
        {
            'sku': 'MUT-LVR-04',
            'name': 'Fresh Goat Liver (Kaleji Cuts)',
            'category': 'mutton',
            'unit': 'KG',
            'cost_price': 520.00,
            'selling_price': 720.00,
            'min_stock_level': 4.0,
            'initial_stock': 3.100, # Low stock trigger
            'description': 'Nutrient-rich smooth tender goat liver cut into clean pan-sear squares.',
            'image_url': 'https://images.unsplash.com/photo-1588347818036-558601350947?auto=format&fit=crop&w=400&q=80'
        },
        # Seafood & Fish (KG)
        {
            'sku': 'SEA-PRW-01',
            'name': 'Jumbo Tiger Prawns (Cleaned & Deveined)',
            'category': 'seafood',
            'unit': 'KG',
            'cost_price': 580.00,
            'selling_price': 850.00,
            'min_stock_level': 8.0,
            'initial_stock': 15.600,
            'description': 'Sweet, plump coastal prawns tail-on, cleaned and deveined for easy cooking.',
            'image_url': 'https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=400&q=80'
        },
        {
            'sku': 'SEA-SLM-02',
            'name': 'Atlantic Salmon Fillet (Skin-on)',
            'category': 'seafood',
            'unit': 'KG',
            'cost_price': 1100.00,
            'selling_price': 1650.00,
            'min_stock_level': 4.0,
            'initial_stock': 6.200,
            'description': 'Omega-3 rich sashimi-grade pink salmon with crisp skin and buttery flakes.',
            'image_url': 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=400&q=80'
        },
        {
            'sku': 'SEA-SUR-03',
            'name': 'Fresh Kingfish / Surmai Steaks',
            'category': 'seafood',
            'unit': 'KG',
            'cost_price': 720.00,
            'selling_price': 990.00,
            'min_stock_level': 6.0,
            'initial_stock': 1.800, # Low stock alert
            'description': 'Center-cut firm meaty steaks with a single central bone, perfect for rava fry.',
            'image_url': 'https://images.unsplash.com/photo-1534483509719-3feaee7c30da?auto=format&fit=crop&w=400&q=80'
        },
        # Delicatessen & Marinated (KG & PCS)
        {
            'sku': 'DEL-MAR-01',
            'name': 'Tandoori Marinated Chicken Tikka Cuts',
            'category': 'deli',
            'unit': 'KG',
            'cost_price': 250.00,
            'selling_price': 420.00,
            'min_stock_level': 5.0,
            'initial_stock': 14.200,
            'description': 'Boneless chicken cubes steeped in thick hung yogurt, mustard oil, and Kashmiri spices.',
            'image_url': 'https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?auto=format&fit=crop&w=400&q=80'
        },
        {
            'sku': 'DEL-SAS-02',
            'name': 'Artisanal Smoked Chicken Sausages (4-Pack)',
            'category': 'deli',
            'unit': 'PCS',
            'cost_price': 140.00,
            'selling_price': 220.00,
            'min_stock_level': 10.0,
            'initial_stock': 25.000,
            'description': 'Naturally smoked beechwood chicken sausages with fresh cracked black pepper.',
            'image_url': 'https://images.unsplash.com/photo-1541544741938-0af808871cc0?auto=format&fit=crop&w=400&q=80'
        }
    ]

    product_map = {}
    for p_info in products_data:
        init_stock = p_info.pop('initial_stock')
        prod = Product(**p_info)
        db.session.add(prod)
        db.session.flush()
        product_map[prod.sku] = prod

        # Create Inventory Record
        inv = Inventory(
            product_id=prod.id,
            current_stock=init_stock,
            unit=prod.unit,
            last_restocked_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        db.session.add(inv)

        # Initial Stock Movement
        mov = StockMovement(
            product_id=prod.id,
            movement_type='PURCHASE',
            quantity=init_stock,
            unit=prod.unit,
            previous_stock=0.0,
            new_stock=init_stock,
            reference_id='INIT-STOCK-2026',
            reason='Initial catalog opening stock balance',
            created_by=admin_user.id
        )
        db.session.add(mov)

    # 3. Seed Suppliers
    suppliers_data = [
        Supplier(
            company_name='Valley Crest Poultry Farms',
            contact_person='Suresh Reddy',
            phone='+91 94411 22334',
            email='orders@valleycrestfarms.in',
            address='Highway 44, Poultry Belt, Medchal',
            gst_or_tax_id='36AAACV1234F1Z8',
            outstanding_balance=18500.00
        ),
        Supplier(
            company_name='Deccan Highland Mutton & Livestock',
            contact_person='Mohammed Ismail',
            phone='+91 98822 33445',
            email='ismail@deccanlivestock.com',
            address='Mandi Road, Livestock Yard, Shadnagar',
            gst_or_tax_id='36AADCD5678G2Z3',
            outstanding_balance=32000.00
        ),
        Supplier(
            company_name='Coastal Harvest Seafood Co.',
            contact_person='Captain John Fernandez',
            phone='+91 97733 44556',
            email='dispatch@coastalharvest.in',
            address='Harbor Gate Pier 3, Mangalore Port',
            gst_or_tax_id='29AAACH9012H1ZX',
            outstanding_balance=14200.00
        )
    ]
    for s in suppliers_data:
        db.session.add(s)
    db.session.flush()

    # 4. Seed Customers
    customers_data = [
        Customer(
            name='Kavitha Sundaram',
            phone='+91 98401 23456',
            email='kavitha.s@gmail.com',
            address='Villa 12, Palm Meadows, Whitefield',
            total_spent=4250.00,
            loyalty_points=120,
            pending_balance=0.00,
            notes='Prefers boneless cuts and extra clean trimming.'
        ),
        Customer(
            name='Chef Rajesh Pillai (Spice Bistro)',
            phone='+91 99002 34567',
            email='kitchen@spicebistro.com',
            address='Shop 5, Commercial Complex, Indiranagar',
            total_spent=18900.00,
            loyalty_points=550,
            pending_balance=2500.00,
            notes='B2B bulk buyer. Weekly invoice settlement.'
        ),
        Customer(
            name='Arjun Nambiar',
            phone='+91 97412 88990',
            email='arjun.nambiar@live.com',
            address='Flat 402, Skyline Residency, HSR Layout',
            total_spent=2890.00,
            loyalty_points=80,
            pending_balance=0.00,
            notes='Weekend grill enthusiast. Loves salmon fillets and lamb chops.'
        ),
        Customer(
            name='Pooja Deshmukh',
            phone='+91 98220 54321',
            email='pooja.deshmukh@outlook.com',
            address='Row House 8, Green Glen Layout, Bellandur',
            total_spent=1450.00,
            loyalty_points=45,
            pending_balance=0.00,
            notes='Prefers country chicken and fresh prawns.'
        )
    ]
    for c in customers_data:
        db.session.add(c)
    db.session.flush()

    # 5. Seed Past Sales & Invoices (with realistic KG decimals and items)
    today = datetime.now(timezone.utc)
    demo_sales = [
        {
            'invoice_number': 'FC-20261118-0001',
            'customer': customers_data[0],
            'employee': employee_user,
            'payment_method': 'UPI',
            'created_at': today - timedelta(hours=3, minutes=15),
            'items': [
                {'sku': 'CHK-BRS-01', 'qty': 1.450}, # 1.450 KG @ 340 = 493.00
                {'sku': 'SEA-PRW-01', 'qty': 0.750}  # 0.750 KG @ 850 = 637.50
            ],
            'discount': 30.50
        },
        {
            'invoice_number': 'FC-20261118-0002',
            'customer': customers_data[2],
            'employee': employee_user,
            'payment_method': 'CARD',
            'created_at': today - timedelta(hours=2, minutes=30),
            'items': [
                {'sku': 'MUT-CHP-02', 'qty': 1.200}, # 1.200 KG @ 1150 = 1380.00
                {'sku': 'SEA-SLM-02', 'qty': 0.850}  # 0.850 KG @ 1650 = 1402.50
            ],
            'discount': 50.00
        },
        {
            'invoice_number': 'FC-20261118-0003',
            'customer': customers_data[1],
            'employee': admin_user,
            'payment_method': 'CASH',
            'created_at': today - timedelta(hours=1, minutes=45),
            'items': [
                {'sku': 'MUT-CUR-01', 'qty': 4.500}, # 4.500 KG @ 890 = 4005.00
                {'sku': 'CHK-CUR-02', 'qty': 6.000}, # 6.000 KG @ 260 = 1560.00
                {'sku': 'DEL-SAS-02', 'qty': 3.000}  # 3 PCS @ 220 = 660.00
            ],
            'discount': 225.00
        },
        {
            'invoice_number': 'FC-20261118-0004',
            'customer': customers_data[3],
            'employee': employee_user,
            'payment_method': 'UPI',
            'created_at': today - timedelta(minutes=40),
            'items': [
                {'sku': 'CHK-DRM-03', 'qty': 1.150}, # 1.150 KG @ 295 = 339.25
                {'sku': 'DEL-MAR-01', 'qty': 0.650}  # 0.650 KG @ 420 = 273.00
            ],
            'discount': 0.00
        }
    ]

    for s_raw in demo_sales:
        subtotal = 0.0
        total_cogs = 0.0
        sale_items_to_add = []
        
        for it in s_raw['items']:
            prod = product_map[it['sku']]
            line_cost = round(it['qty'] * prod.cost_price, 2)
            line_sub = round(it['qty'] * prod.selling_price, 2)
            subtotal += line_sub
            total_cogs += line_cost
            
            s_item = SaleItem(
                product_id=prod.id,
                product_name=prod.name,
                sku=prod.sku,
                unit=prod.unit,
                quantity=it['qty'],
                unit_cost_price=prod.cost_price,
                unit_selling_price=prod.selling_price,
                subtotal=line_sub,
                created_at=s_raw['created_at']
            )
            sale_items_to_add.append(s_item)
            
        tax_val = round((subtotal - s_raw['discount']) * (Config.DEFAULT_TAX_PERCENT / 100.0), 2)
        total_amount = round((subtotal - s_raw['discount']) + tax_val, 2)
        
        sale = Sale(
            invoice_number=s_raw['invoice_number'],
            customer_id=s_raw['customer'].id,
            employee_id=s_raw['employee'].id,
            employee_name=s_raw['employee'].full_name,
            subtotal=subtotal,
            discount_amount=s_raw['discount'],
            tax_amount=tax_val,
            total_amount=total_amount,
            total_cogs=total_cogs,
            payment_method=s_raw['payment_method'],
            payment_status='PAID',
            cash_tendered=total_amount if s_raw['payment_method'] == 'CASH' else 0.0,
            change_returned=0.0,
            created_at=s_raw['created_at']
        )
        db.session.add(sale)
        db.session.flush()

        for s_item in sale_items_to_add:
            s_item.sale_id = sale.id
            db.session.add(s_item)

    # 6. Seed Operating Expenses
    expenses_data = [
        Expense(
            category='Electricity & Cold Chain',
            amount=4500.00,
            expense_date=date.today(),
            payment_method='UPI',
            description='Commercial 3-Phase Deep Freezer & Chiller power bill advance',
            created_by=admin_user.id
        ),
        Expense(
            category='Packaging Materials',
            amount=1850.00,
            expense_date=date.today(),
            payment_method='CASH',
            description='Biodegradable butcher wrap paper, vacuum pouches, and leak-proof trays',
            created_by=admin_user.id
        ),
        Expense(
            category='Transport & Logistics',
            amount=1200.00,
            expense_date=date.today() - timedelta(days=1),
            payment_method='CASH',
            description='Refrigerated van transit fuel from port harbor',
            created_by=admin_user.id
        ),
        Expense(
            category='Sanitization & Pest Control',
            amount=950.00,
            expense_date=date.today() - timedelta(days=2),
            payment_method='UPI',
            description='Food-grade enzymatic cutting station sterilization disinfectant',
            created_by=admin_user.id
        )
    ]
    for exp in expenses_data:
        db.session.add(exp)

    # 7. Seed Settings
    settings_data = {
        'shop_profile': {
            'name': Config.SHOP_NAME,
            'tagline': Config.SHOP_TAGLINE,
            'phone': Config.SHOP_PHONE,
            'address': Config.SHOP_ADDRESS,
            'gst_no': Config.SHOP_GST_NO,
            'currency': Config.CURRENCY_SYMBOL,
            'tax_percent': Config.DEFAULT_TAX_PERCENT,
            'invoice_prefix': Config.INVOICE_PREFIX
        },
        'supabase_config': {
            'supabase_url': Config.SUPABASE_URL,
            'supabase_key': Config.SUPABASE_KEY,
            'status': 'configured' if Config.SUPABASE_URL else 'local_mode'
        }
    }
    for k, v in settings_data.items():
        db.session.add(Setting(key=k, value=v))

    # 8. Seed Initial Audit Logs
    audit = AuditLog(
        user_id=admin_user.id,
        user_name=admin_user.full_name,
        role='admin',
        action='SYSTEM_INITIALIZED',
        module='SYSTEM',
        details={'event': 'Catalog, initial inventory, profiles and tax parameters successfully bootstrapped.'},
        ip_address='127.0.0.1'
    )
    db.session.add(audit)

    db.session.commit()
    print("[SUCCESS] Fresh Cut Meat Shop database seeded successfully!")
