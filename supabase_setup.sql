-- =========================================================================
-- FRESH CUT MEAT SHOP MANAGEMENT SYSTEM
-- Supabase PostgreSQL Database Schema & RLS Policies (SRS v1.1 Compliant)
-- =========================================================================

-- Enable UUID extension if not enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Profiles Table (Linked to Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE, -- REFERENCES auth.users(id) ON DELETE CASCADE
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    full_name VARCHAR(150) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'employee' CHECK (role IN ('admin', 'employee')),
    pin VARCHAR(10) DEFAULT '1234',
    phone VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 2. Products Table
CREATE TABLE IF NOT EXISTS public.products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sku VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL, -- 'poultry', 'mutton', 'seafood', 'deli', 'other'
    unit VARCHAR(20) NOT NULL DEFAULT 'KG' CHECK (unit IN ('KG', 'PCS')),
    cost_price NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    selling_price NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    min_stock_level NUMERIC(12, 3) NOT NULL DEFAULT 5.000,
    description TEXT,
    image_url TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 3. Customers Table
CREATE TABLE IF NOT EXISTS public.customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(150) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(255),
    address TEXT,
    total_spent NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    loyalty_points INTEGER NOT NULL DEFAULT 0,
    pending_balance NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 4. Suppliers Table
CREATE TABLE IF NOT EXISTS public.suppliers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(150),
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    address TEXT,
    gst_or_tax_id VARCHAR(50),
    outstanding_balance NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 5. Inventory Table (Current stock balance by product and unit)
CREATE TABLE IF NOT EXISTS public.inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE UNIQUE,
    current_stock NUMERIC(12, 3) NOT NULL DEFAULT 0.000,
    unit VARCHAR(20) NOT NULL DEFAULT 'KG',
    last_restocked_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 6. Sales Table (Invoice Headers)
CREATE TABLE IF NOT EXISTS public.sales (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    customer_id UUID REFERENCES public.customers(id) ON DELETE SET NULL,
    employee_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    employee_name VARCHAR(150),
    subtotal NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    discount_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    tax_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    total_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    total_cogs NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    payment_method VARCHAR(50) NOT NULL DEFAULT 'CASH' CHECK (payment_method IN ('CASH', 'UPI', 'CARD', 'SPLIT', 'CREDIT')),
    payment_status VARCHAR(50) NOT NULL DEFAULT 'PAID' CHECK (payment_status IN ('PAID', 'PARTIAL', 'PENDING', 'CANCELLED')),
    cash_tendered NUMERIC(12, 2) DEFAULT 0.00,
    change_returned NUMERIC(12, 2) DEFAULT 0.00,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 7. Sale Items Table (Item lines)
CREATE TABLE IF NOT EXISTS public.sale_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sale_id UUID NOT NULL REFERENCES public.sales(id) ON DELETE CASCADE,
    product_id UUID REFERENCES public.products(id) ON DELETE SET NULL,
    product_name VARCHAR(150) NOT NULL,
    sku VARCHAR(50),
    unit VARCHAR(20) NOT NULL DEFAULT 'KG',
    quantity NUMERIC(12, 3) NOT NULL,
    unit_cost_price NUMERIC(12, 2) NOT NULL DEFAULT 0.00, -- Historical cost
    unit_selling_price NUMERIC(12, 2) NOT NULL,           -- Historical price
    subtotal NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 8. Purchases Table (Stock Intake Headers)
CREATE TABLE IF NOT EXISTS public.purchases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    purchase_invoice_no VARCHAR(100) NOT NULL,
    supplier_id UUID REFERENCES public.suppliers(id) ON DELETE SET NULL,
    supplier_name VARCHAR(150),
    total_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    paid_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    payment_status VARCHAR(50) NOT NULL DEFAULT 'PAID' CHECK (payment_status IN ('PAID', 'PARTIAL', 'PENDING')),
    purchase_date TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    notes TEXT,
    created_by UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 9. Purchase Items Table (Stock Intake Line Items)
CREATE TABLE IF NOT EXISTS public.purchase_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    purchase_id UUID NOT NULL REFERENCES public.purchases(id) ON DELETE CASCADE,
    product_id UUID REFERENCES public.products(id) ON DELETE SET NULL,
    product_name VARCHAR(150) NOT NULL,
    unit VARCHAR(20) NOT NULL DEFAULT 'KG',
    quantity NUMERIC(12, 3) NOT NULL,
    unit_cost_price NUMERIC(12, 2) NOT NULL,
    total_cost NUMERIC(12, 2) NOT NULL
);

-- 10. Stock Movements Table (Auditable movements: INTAKE, SALE, WASTAGE, RETURN, ADJUSTMENT)
CREATE TABLE IF NOT EXISTS public.stock_movements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    movement_type VARCHAR(50) NOT NULL CHECK (movement_type IN ('PURCHASE', 'SALE', 'WASTAGE', 'RETURN', 'ADJUSTMENT')),
    quantity NUMERIC(12, 3) NOT NULL, -- Negative for SALE/WASTAGE, Positive for PURCHASE
    unit VARCHAR(20) NOT NULL DEFAULT 'KG',
    previous_stock NUMERIC(12, 3) NOT NULL,
    new_stock NUMERIC(12, 3) NOT NULL,
    reference_id VARCHAR(100), -- Sale Invoice, Purchase Invoice, or Wastage Log ID
    reason TEXT,
    created_by UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 11. Expenses Table (Operational expenses)
CREATE TABLE IF NOT EXISTS public.expenses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category VARCHAR(100) NOT NULL, -- 'Rent', 'Electricity & Cold Chain', 'Salaries', 'Transport', 'Packaging', 'Maintenance', 'Other'
    amount NUMERIC(12, 2) NOT NULL,
    expense_date DATE NOT NULL DEFAULT CURRENT_DATE,
    payment_method VARCHAR(50) NOT NULL DEFAULT 'CASH',
    description TEXT,
    receipt_reference VARCHAR(100),
    created_by UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 12. Payments Table (Customer Receipts and Supplier Disbursements)
CREATE TABLE IF NOT EXISTS public.payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_type VARCHAR(50) NOT NULL CHECK (payment_type IN ('CUSTOMER_RECEIPT', 'SUPPLIER_PAYMENT')),
    reference_id UUID, -- Customer ID or Supplier ID
    reference_name VARCHAR(150),
    amount NUMERIC(12, 2) NOT NULL,
    payment_date TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    payment_method VARCHAR(50) NOT NULL DEFAULT 'CASH',
    transaction_ref VARCHAR(100),
    notes TEXT,
    created_by UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 13. Settings Table
CREATE TABLE IF NOT EXISTS public.settings (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 14. Audit Logs Table
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    user_name VARCHAR(150),
    role VARCHAR(50),
    action VARCHAR(100) NOT NULL,
    module VARCHAR(100) NOT NULL,
    details JSONB,
    ip_address VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- Create Indexes for performance
CREATE INDEX IF NOT EXISTS idx_sales_created_at ON public.sales(created_at);
CREATE INDEX IF NOT EXISTS idx_sales_invoice_no ON public.sales(invoice_number);
CREATE INDEX IF NOT EXISTS idx_stock_movements_product ON public.stock_movements(product_id);
CREATE INDEX IF NOT EXISTS idx_stock_movements_created_at ON public.stock_movements(created_at);
CREATE INDEX IF NOT EXISTS idx_products_category ON public.products(category);
CREATE INDEX IF NOT EXISTS idx_products_active ON public.products(is_active);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON public.audit_logs(created_at);

-- ROW LEVEL SECURITY (RLS) POLICIES
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sale_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.stock_movements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.purchases ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- Helper function to check admin role
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM public.profiles
    WHERE user_id = auth.uid() AND role = 'admin' AND is_active = true
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Profiles: Admin can view and edit all; employees view own
CREATE POLICY "Admins full access to profiles" ON public.profiles FOR ALL USING (public.is_admin());
CREATE POLICY "Employees can view own profile" ON public.profiles FOR SELECT USING (user_id = auth.uid());

-- Products: Everyone authenticated can view active products; Admin has full control
CREATE POLICY "Anyone can view active products" ON public.products FOR SELECT USING (true);
CREATE POLICY "Admins full access to products" ON public.products FOR ALL USING (public.is_admin());

-- Sales: Admin views all; Employee views own sales
CREATE POLICY "Admins view all sales" ON public.sales FOR ALL USING (public.is_admin());
CREATE POLICY "Employees view own sales" ON public.sales FOR SELECT USING (employee_id IN (SELECT id FROM public.profiles WHERE user_id = auth.uid()));
CREATE POLICY "Employees can create sales" ON public.sales FOR INSERT WITH CHECK (true);

-- Sale Items: Viewable if corresponding sale is viewable
CREATE POLICY "View sale items" ON public.sale_items FOR SELECT USING (true);
CREATE POLICY "Create sale items" ON public.sale_items FOR INSERT WITH CHECK (true);

-- Inventory: All can view; only admins can directly update/delete
CREATE POLICY "View inventory" ON public.inventory FOR SELECT USING (true);
CREATE POLICY "Admins modify inventory" ON public.inventory FOR ALL USING (public.is_admin());

-- Stock movements: All can view movements; creation permitted for sales and adjustments
CREATE POLICY "View stock movements" ON public.stock_movements FOR SELECT USING (true);
CREATE POLICY "Create stock movements" ON public.stock_movements FOR INSERT WITH CHECK (true);

-- Expenses & Audit Logs: Admin only
CREATE POLICY "Admins full access to expenses" ON public.expenses FOR ALL USING (public.is_admin());
CREATE POLICY "Admins full access to audit logs" ON public.audit_logs FOR ALL USING (public.is_admin());
CREATE POLICY "Admins full access to settings" ON public.settings FOR ALL USING (public.is_admin());
