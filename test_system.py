import unittest
from app import app
from backend.models import db, Profile, Product, Inventory, Sale

class FreshCutSystemTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_01_admin_login(self):
        res = self.client.post('/api/auth/login', json={'email': 'admin@freshcut.com', 'password': 'AdminPassword123!'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('token', data)
        self.assertEqual(data['user']['role'], 'admin')

    def test_02_employee_pin_login(self):
        res = self.client.post('/api/auth/login', json={'pin': '5678'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['user']['role'], 'employee')

    def test_03_rbac_enforcement(self):
        # 1. Log in as employee
        emp_res = self.client.post('/api/auth/login', json={'pin': '5678'})
        emp_token = emp_res.get_json()['token']
        headers = {'Authorization': f'Bearer {emp_token}'}

        # 2. Try to access Admin-only employees endpoint
        res = self.client.get('/api/auth/employees', headers=headers)
        self.assertEqual(res.status_code, 403)

        # 3. Try to access Admin-only expenses endpoint
        res2 = self.client.get('/api/finance/expenses', headers=headers)
        self.assertEqual(res2.status_code, 403)

    def test_04_pos_calculation_and_checkout(self):
        # Log in as cashier
        login_res = self.client.post('/api/auth/login', json={'pin': '5678'})
        token = login_res.get_json()['token']
        headers = {'Authorization': f'Bearer {token}'}

        # Get first active KG product
        prod_res = self.client.get('/api/products', headers=headers)
        prods = prod_res.get_json()['products']
        self.assertTrue(len(prods) > 0)
        prod = next(p for p in prods if p['unit'] == 'KG')

        # Calculate cart with decimal KG (e.g. 1.250 kg)
        calc_res = self.client.post('/api/pos/calculate', headers=headers, json={
            'items': [{'product_id': prod['id'], 'quantity': 1.250}],
            'discount_amount': 10.0,
            'tax_percent': 5.0
        })
        self.assertEqual(calc_res.status_code, 200)
        calc_data = calc_res.get_json()
        expected_subtotal = round(1.250 * prod['selling_price'], 2)
        self.assertEqual(calc_data['subtotal'], expected_subtotal)

        # Checkout
        checkout_res = self.client.post('/api/pos/checkout', headers=headers, json={
            'items': [{'product_id': prod['id'], 'quantity': 1.000}],
            'payment_method': 'UPI',
            'discount_amount': 0.0,
            'notes': 'Test sale'
        })
        self.assertEqual(checkout_res.status_code, 201)
        chk_data = checkout_res.get_json()
        self.assertTrue(chk_data['sale']['invoice_number'].startswith('FC-'))

    def test_05_dashboard_and_reports(self):
        login_res = self.client.post('/api/auth/login', json={'email': 'admin@freshcut.com', 'password': 'AdminPassword123!'})
        token = login_res.get_json()['token']
        headers = {'Authorization': f'Bearer {token}'}

        res = self.client.get('/api/reports/dashboard', headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('kpis', data)
        self.assertIn('charts', data)
        self.assertIn('recent_transactions', data)

        # Excel Export test
        excel_res = self.client.get('/api/reports/export?type=sales&format=excel', headers=headers)
        self.assertEqual(excel_res.status_code, 200)

        # PDF Export test
        pdf_res = self.client.get('/api/reports/export?type=pnl&format=pdf', headers=headers)
        self.assertEqual(pdf_res.status_code, 200)

    def test_06_stock_increment(self):
        login_res = self.client.post('/api/auth/login', json={'email': 'admin@freshcut.com', 'password': 'AdminPassword123!'})
        token = login_res.get_json()['token']
        headers = {'Authorization': f'Bearer {token}'}

        # 1. Fetch current stock
        inv_res = self.client.get('/api/inventory', headers=headers)
        self.assertEqual(inv_res.status_code, 200)
        items = inv_res.get_json()['inventory']
        self.assertTrue(len(items) > 0)
        target = items[0]
        initial_stock = target['current_stock']

        # 2. Increment stock by +15.500
        increment_amount = 15.5 if target['unit'] == 'KG' else 15.0
        inc_res = self.client.post('/api/inventory/increment', headers=headers, json={
            'product_id': target['product_id'],
            'quantity': increment_amount,
            'reason': 'Fresh farm delivery intake test'
        })
        self.assertEqual(inc_res.status_code, 200)
        inc_data = inc_res.get_json()
        expected_new_stock = round(initial_stock + increment_amount, 3)
        self.assertEqual(inc_data['inventory']['current_stock'], expected_new_stock)

        # 3. Verify stock movements recorded the intake
        mov_res = self.client.get(f"/api/inventory/movements?product_id={target['product_id']}&type=PURCHASE", headers=headers)
        self.assertEqual(mov_res.status_code, 200)
        movements = mov_res.get_json()['movements']
        self.assertTrue(len(movements) > 0)
        latest_mov = movements[0]
        self.assertEqual(latest_mov['movement_type'], 'PURCHASE')
        self.assertEqual(latest_mov['quantity'], increment_amount)

    def test_07_user_registration_and_signup(self):
        import time
        unique_email = f"manager_{int(time.time())}@freshcut.com"

        # 1. Reject short password
        short_res = self.client.post('/api/auth/register', json={
            'full_name': 'New Manager',
            'email': unique_email,
            'password': '123'
        })
        self.assertEqual(short_res.status_code, 400)

        # 2. Valid Registration
        reg_res = self.client.post('/api/auth/register', json={
            'full_name': 'Viswanath Store Owner',
            'email': unique_email,
            'password': 'SecureStorePass2026!',
            'role': 'admin',
            'pin': '7788',
            'phone': '+91 98765 43210'
        })
        self.assertEqual(reg_res.status_code, 201)
        data = reg_res.get_json()
        self.assertIn('token', data)
        self.assertEqual(data['user']['email'], unique_email)
        self.assertEqual(data['user']['role'], 'admin')

        # 3. Reject duplicate registration
        dup_res = self.client.post('/api/auth/register', json={
            'full_name': 'Duplicate User',
            'email': unique_email,
            'password': 'SecureStorePass2026!'
        })
        self.assertEqual(dup_res.status_code, 400)

        # 4. Sign in with newly registered credentials
        login_res = self.client.post('/api/auth/login', json={
            'email': unique_email,
            'password': 'SecureStorePass2026!'
        })
        self.assertEqual(login_res.status_code, 200)
        login_data = login_res.get_json()
        self.assertEqual(login_data['user']['email'], unique_email)

if __name__ == '__main__':
    unittest.main()
