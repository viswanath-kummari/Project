# Fresh Cut Meat Shop Management System

A commercial-grade retail management platform and high-speed POS billing system engineered for modern meat shops, butcheries, poultry suppliers, and seafood retailers.

Designed according to **Software Requirements Specification (SRS v1.1)** with a modern, high-conversion visual identity, smooth interactive 60fps animations, virtual weight scale integration, and future mobile app readiness.

---

## 🥩 Key Features

- **Artisanal Butcher UI/UX**: Deep butcher carmine red (`#881337`), emerald sage (`#065f46`), and dark charcoal slate (`#0f172a`) design system with card lift effects, micro-interactions, and skeleton screens.
- **High-Speed Touch POS Billing**:
  - Full support for **KG products** with decimal weights (e.g. `1.350` kg) and **Piece products** (whole numbers).
  - Quick Scale dial buttons (`0.25 kg`, `0.50 kg`, `1.00 kg`, etc.).
  - Instant calculations for Subtotal, Discounts, Configurable Taxes (GST 5%), and Net Amount.
  - Multi-tender payment methods: **Cash** (with cash tendered & change return calculator), **UPI / QR Code** (with interactive simulated QR scanner), **Card**, and **Store Credit**.
  - **Thermal Printable Receipts**: 80mm thermal receipt generator ready for instant browser printing (`Ctrl+P` styled).
- **Transactional Stock Decrement & Movement Ledger**:
  - Atomic inventory decrement upon completed sales.
  - Negative stock prevention.
  - Dedicated **Spoilage & Wastage Logger** with mandatory audit classification (Trimming Loss, De-boning scrap, Cold chain fluctuation, Shelf expiry).
- **Role-Based Access Control (RBAC)**:
  - **Admin / Owner**: Complete oversight of P&L reports, operating overheads, staff accounts, wholesale intake, and system settings.
  - **Employee / Cashier**: Fast POS billing counter, active product and price catalog, limited stock viewing, and their own sales history. Strict backend route enforcement (returns 403 Forbidden on unauthorized requests).
- **Pandas Reporting & Financial Analytics**:
  - Profit & Loss (P&L) breakdown: Total Sales Revenue &minus; Cost of Goods Sold (COGS) = **Gross Profit**, less Operating Expenses and Spoilage = **Net Operating Result (EBITDA)**.
  - 1-Click exports to **Excel (.xlsx)**, **Printable PDF**, and **CSV**.
- **Supabase Cloud PostgreSQL + Dual-Engine Resilience**:
  - Pre-configured Supabase PostgreSQL integration with Row Level Security (RLS) policies and triggers (`supabase_setup.sql`).
  - Seamless zero-config local persistent engine enabled by default so the application runs immediately without requiring external database setup.
- **Future Mobile Application Pathway**:
  - REST API backend architecture with standard JSON payloads, ready for future Android and iOS applications or PWA wrapping.

---

## 🚀 Quick Start Guide

### 1. Requirements
- Python 3.10+
- Modern Web Browser (Chrome, Edge, Firefox, Safari)

### 2. Run the Application
Open a terminal in the project directory and execute:
```bash
python app.py
```
Open **`http://127.0.0.1:5000/`** in your browser.

---

## 🔐 Demo Credentials & 1-Click Role Switcher

The top navigation bar features a **"Switch Demo Role"** dropdown button for 1-click evaluation:

| Role | Name | Email | Quick PIN | Password | Permissions |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Admin / Owner** | Vikram Rathore | `admin@freshcut.com` | `1234` | `AdminPassword123!` | Complete master control (Products, POS, Staff, Expenses, P&L, Audit, Supabase settings) |
| **Employee / Cashier** | Aarav Sharma | `cashier@freshcut.com` | `5678` | `CashierPassword123!` | POS billing, catalog & pricing view, shift sales history |

---

## 📁 Project Architecture & Directory Structure

```
Application/
├── app.py                      # Flask Application entry point & CORS configuration
├── config.py                   # App config, business defaults, JWT, Supabase settings
├── requirements.txt            # Python dependencies (Flask, pandas, openpyxl, reportlab, supabase)
├── supabase_setup.sql          # Supabase PostgreSQL schema, RLS policies, indexes
├── test_system.py              # Automated test suite (Auth, RBAC, POS, Stock, Reports)
│
├── backend/
│   ├── database.py             # Dual-mode DB adapter (Supabase PostgreSQL + SQLAlchemy fallback)
│   ├── auth.py                 # JWT token generation, role verification decorators
│   ├── models.py               # Data models (Profiles, Products, Inventory, Sales, Expenses, etc.)
│   ├── routes/
│   │   ├── auth_routes.py      # /api/auth (Login, user profile, staff accounts)
│   │   ├── product_routes.py   # /api/products (Catalog CRUD, KG vs PCS, price control)
│   │   ├── pos_routes.py       # /api/pos (Cart checkout, scale calc, invoice numbering)
│   │   ├── inventory_routes.py # /api/inventory (Current balances, wastage, adjustments)
│   │   ├── customer_routes.py  # /api/customers (Customer profiles & loyalty)
│   │   ├── supplier_routes.py  # /api/suppliers (Suppliers & wholesale purchase intake)
│   │   ├── finance_routes.py   # /api/finance (Expenses, operating costs, payments)
│   │   ├── report_routes.py    # /api/reports (Dashboard KPIs, P&L, Excel/PDF exports)
│   │   ├── settings_routes.py  # /api/settings (Shop parameters, Supabase keys)
│   │   └── audit_routes.py     # /api/audit (Action logs & security audit trail)
│   └── services/
│       └── report_service.py   # Pandas reporting aggregations & Excel/PDF generator
│
├── static/
│   ├── css/
│   │   ├── style.css           # Artisanal meat color scheme, layout, typography
│   │   ├── animations.css      # Smooth card lifts, 3D tilt, counter animations, toasts
│   │   └── pos.css             # POS layout, touch buttons, thermal print stylesheet
│   └── js/
│       ├── api.js              # Fetch wrapper with Bearer token & session handling
│       ├── app.js              # Single-page router, role toggler, animated counters
│       ├── dashboard.js        # Dynamic Chart.js visualizations & KPI counters
│       ├── pos.js              # High-speed POS billing engine & thermal receipt preview
│       ├── inventory.js        # Stock manager, wastage logger, movement history
│       ├── products.js         # Product catalog management modal
│       ├── customers.js        # Customer management & suppliers intake
│       ├── finance.js          # Operating expenses logger
│       ├── reports.js          # Pandas P&L report viewer & download triggers
│       ├── employees.js        # Staff account & PIN administration
│       └── settings.js         # Shop details & Supabase connectivity
│
└── templates/
    └── index.html              # Responsive single-page application template
```

---

## 🗄️ Supabase PostgreSQL Setup (Optional Cloud Mode)

To connect this application to a hosted Supabase project:
1. Create a project at [supabase.com](https://supabase.com).
2. Go to the **SQL Editor** in the Supabase Dashboard.
3. Paste and run the contents of [`supabase_setup.sql`](file:///c:/Users/viswa/Desktop/Application/supabase_setup.sql).
4. In the app, navigate to **Store Settings**, input your **Supabase URL** and **API Key**, and click **Save & Verify Connection**.
