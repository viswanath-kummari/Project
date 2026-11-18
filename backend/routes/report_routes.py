import io
from datetime import datetime, date, timedelta, timezone
from flask import Blueprint, request, jsonify, send_file
from backend.models import db, Sale, SaleItem, Expense, Inventory, Product, StockMovement
from backend.auth import token_required, admin_required
from backend.services.report_service import ReportService

report_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@report_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard_summary():
    """Real-time live KPI telemetry and Chart.js datasets"""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    is_admin = (request.current_user.role == 'admin')

    # Today's Sales
    today_sales_q = Sale.query.filter(Sale.created_at >= today_start)
    if not is_admin:
        today_sales_q = today_sales_q.filter_by(employee_id=request.current_user.id)
    today_sales = today_sales_q.all()

    today_revenue = sum(s.total_amount for s in today_sales)
    today_bills = len(today_sales)

    # All-time / Month totals for Admin
    if is_admin:
        all_sales = Sale.query.all()
        total_revenue = sum(s.total_amount for s in all_sales)
        total_cogs = sum(s.total_cogs for s in all_sales)
        gross_profit = total_revenue - total_cogs
        total_bills_all = len(all_sales)

        expenses = Expense.query.all()
        total_expenses = sum(e.amount for e in expenses)

        # Wastage cost
        wastage_records = db.session.query(
            StockMovement.quantity,
            Product.cost_price
        ).join(Product, StockMovement.product_id == Product.id).filter(StockMovement.movement_type == 'WASTAGE').all()
        wastage_cost = sum(abs(r[0]) * r[1] for r in wastage_records)

        net_operating_result = gross_profit - total_expenses - wastage_cost
    else:
        total_revenue = today_revenue
        gross_profit = 0.0
        total_expenses = 0.0
        net_operating_result = 0.0
        total_bills_all = today_bills

    # Stock stats
    inv_items = Inventory.query.all()
    total_stock_kg = sum(i.current_stock for i in inv_items if i.unit == 'KG')
    total_stock_pcs = sum(i.current_stock for i in inv_items if i.unit == 'PCS')
    low_stock_alerts = sum(1 for i in inv_items if i.product and i.current_stock <= i.product.min_stock_level)

    # Recent Transactions
    rec_sales_q = Sale.query
    if not is_admin:
        rec_sales_q = rec_sales_q.filter_by(employee_id=request.current_user.id)
    recent_sales = rec_sales_q.order_by(Sale.created_at.desc()).limit(8).all()

    # Chart 1: Last 7 Days Revenue Trend
    last_7_days_labels = []
    last_7_days_revenue = []
    last_7_days_expenses = []

    for i in range(6, -1, -1):
        day_date = date.today() - timedelta(days=i)
        day_start = datetime.combine(day_date, datetime.min.time(), tzinfo=timezone.utc)
        day_end = datetime.combine(day_date, datetime.max.time(), tzinfo=timezone.utc)
        
        day_label = day_date.strftime('%a (%d %b)')
        last_7_days_labels.append(day_label)

        # Revenue
        day_rev_q = db.session.query(db.func.sum(Sale.total_amount)).filter(Sale.created_at >= day_start, Sale.created_at <= day_end)
        if not is_admin:
            day_rev_q = day_rev_q.filter(Sale.employee_id == request.current_user.id)
        rev_val = day_rev_q.scalar() or 0.0
        last_7_days_revenue.append(round(float(rev_val), 2))

        # Expense (Admin only)
        if is_admin:
            exp_val = db.session.query(db.func.sum(Expense.amount)).filter(Expense.expense_date == day_date).scalar() or 0.0
            last_7_days_expenses.append(round(float(exp_val), 2))
        else:
            last_7_days_expenses.append(0.0)

    # Chart 2: Category Volume Breakdown
    cat_query = db.session.query(
        Product.category,
        db.func.sum(SaleItem.subtotal)
    ).join(SaleItem, Product.id == SaleItem.product_id).group_by(Product.category).all()
    
    cat_labels = [c[0].capitalize() for c in cat_query]
    cat_values = [round(float(c[1]), 2) for c in cat_query]

    return jsonify({
        'kpis': {
            'today_sales': round(float(today_revenue), 2),
            'today_bills': today_bills,
            'total_revenue': round(float(total_revenue), 2),
            'total_bills': total_bills_all,
            'total_expenses': round(float(total_expenses), 2) if is_admin else None,
            'gross_profit': round(float(gross_profit), 2) if is_admin else None,
            'net_operating_result': round(float(net_operating_result), 2) if is_admin else None,
            'total_stock_kg': round(float(total_stock_kg), 2),
            'total_stock_pcs': int(total_stock_pcs),
            'low_stock_alerts': low_stock_alerts
        },
        'charts': {
            'trend': {
                'labels': last_7_days_labels,
                'revenue': last_7_days_revenue,
                'expenses': last_7_days_expenses
            },
            'categories': {
                'labels': cat_labels,
                'values': cat_values
            }
        },
        'recent_transactions': [s.to_dict() for s in recent_sales]
    })

@report_bp.route('/pnl', methods=['GET'])
@admin_required
def get_pnl():
    start = request.args.get('start_date')
    end = request.args.get('end_date')

    start_dt = datetime.strptime(start, '%Y-%m-%d').replace(tzinfo=timezone.utc) if start else None
    end_dt = datetime.strptime(end, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=timezone.utc) if end else None

    pnl = ReportService.calculate_profit_loss(start_dt, end_dt)
    return jsonify({'pnl': pnl})

@report_bp.route('/export', methods=['GET'])
@admin_required
def export_report():
    report_type = request.args.get('type', 'sales') # 'sales', 'products', 'pnl', 'inventory'
    fmt = request.args.get('format', 'excel') # 'excel', 'pdf', 'csv'
    start = request.args.get('start_date')
    end = request.args.get('end_date')

    start_dt = datetime.strptime(start, '%Y-%m-%d').replace(tzinfo=timezone.utc) if start else None
    end_dt = datetime.strptime(end, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=timezone.utc) if end else None

    filename = f"fresh_cut_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M')}"

    if fmt == 'pdf':
        buffer = ReportService.export_pdf_report(report_type, start_dt, end_dt)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"{filename}.pdf",
            mimetype='application/pdf'
        )
    elif fmt == 'csv':
        df = ReportService.get_sales_dataframe(start_dt, end_dt) if report_type == 'sales' else ReportService.get_product_sales_dataframe(start_dt, end_dt)
        csv_data = df.to_csv(index=False)
        return send_file(
            io.BytesIO(csv_data.encode('utf-8')),
            as_attachment=True,
            download_name=f"{filename}.csv",
            mimetype='text/csv'
        )
    else:
        # Excel .xlsx
        excel_buf = ReportService.export_excel_report(report_type, start_dt, end_dt)
        return send_file(
            excel_buf,
            as_attachment=True,
            download_name=f"{filename}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
