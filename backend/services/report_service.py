import io
from datetime import datetime, date, timedelta, timezone
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from backend.models import db, Sale, SaleItem, Purchase, PurchaseItem, Expense, StockMovement, Inventory, Product, Profile
from config import Config

class ReportService:
    @staticmethod
    def get_sales_dataframe(start_date=None, end_date=None):
        query = db.session.query(
            Sale.id,
            Sale.invoice_number,
            Sale.created_at,
            Sale.employee_name,
            Sale.subtotal,
            Sale.discount_amount,
            Sale.tax_amount,
            Sale.total_amount,
            Sale.total_cogs,
            Sale.payment_method,
            Sale.payment_status
        )
        if start_date:
            query = query.filter(Sale.created_at >= start_date)
        if end_date:
            query = query.filter(Sale.created_at <= end_date)
            
        records = query.all()
        if not records:
            return pd.DataFrame()
            
        data = [{
            'Invoice': r.invoice_number,
            'Date': r.created_at.strftime('%Y-%m-%d %H:%M') if r.created_at else '',
            'Cashier': r.employee_name or 'Cashier',
            'Subtotal': float(r.subtotal),
            'Discount': float(r.discount_amount),
            'Tax': float(r.tax_amount),
            'Revenue': float(r.total_amount),
            'COGS': float(r.total_cogs),
            'GrossProfit': float(r.total_amount - r.total_cogs),
            'PaymentMethod': r.payment_method,
            'Status': r.payment_status
        } for r in records]
        return pd.DataFrame(data)

    @staticmethod
    def get_product_sales_dataframe(start_date=None, end_date=None):
        query = db.session.query(
            SaleItem.product_name,
            SaleItem.sku,
            SaleItem.unit,
            SaleItem.quantity,
            SaleItem.unit_cost_price,
            SaleItem.unit_selling_price,
            SaleItem.subtotal,
            Sale.created_at
        ).join(Sale, SaleItem.sale_id == Sale.id)

        if start_date:
            query = query.filter(Sale.created_at >= start_date)
        if end_date:
            query = query.filter(Sale.created_at <= end_date)

        records = query.all()
        if not records:
            return pd.DataFrame()

        data = [{
            'Product': r.product_name,
            'SKU': r.sku,
            'Unit': r.unit,
            'Quantity': float(r.quantity),
            'CostPrice': float(r.unit_cost_price),
            'SellingPrice': float(r.unit_selling_price),
            'Revenue': float(r.subtotal),
            'TotalCost': round(float(r.quantity * r.unit_cost_price), 2),
            'Margin': round(float(r.subtotal - (r.quantity * r.unit_cost_price)), 2)
        } for r in records]
        
        df = pd.DataFrame(data)
        grouped = df.groupby(['Product', 'SKU', 'Unit']).agg({
            'Quantity': 'sum',
            'Revenue': 'sum',
            'TotalCost': 'sum',
            'Margin': 'sum'
        }).reset_index()
        return grouped

    @staticmethod
    def calculate_profit_loss(start_date=None, end_date=None):
        """
        SRS v1.1 Profit calculation:
        - Sales Revenue
        - Cost of Goods Sold (COGS)
        - Gross Profit = Revenue - COGS
        - Wastage Cost
        - Operating Expenses
        - Net Operating Result = Gross Profit - Operating Expenses - Wastage Cost
        """
        sales_q = db.session.query(
            db.func.sum(Sale.total_amount),
            db.func.sum(Sale.total_cogs),
            db.func.count(Sale.id)
        )
        if start_date:
            sales_q = sales_q.filter(Sale.created_at >= start_date)
        if end_date:
            sales_q = sales_q.filter(Sale.created_at <= end_date)
            
        sales_res = sales_q.first()
        total_revenue = float(sales_res[0] or 0.0)
        total_cogs = float(sales_res[1] or 0.0)
        total_bills = int(sales_res[2] or 0)
        gross_profit = total_revenue - total_cogs

        # Expenses
        exp_q = db.session.query(db.func.sum(Expense.amount))
        if start_date:
            exp_q = exp_q.filter(Expense.expense_date >= start_date.date() if hasattr(start_date, 'date') else start_date)
        if end_date:
            exp_q = exp_q.filter(Expense.expense_date <= end_date.date() if hasattr(end_date, 'date') else end_date)
            
        total_expenses = float(exp_q.scalar() or 0.0)

        # Wastage cost (from stock movements where type='WASTAGE')
        wastage_q = db.session.query(
            StockMovement.quantity,
            Product.cost_price
        ).join(Product, StockMovement.product_id == Product.id).filter(StockMovement.movement_type == 'WASTAGE')
        
        if start_date:
            wastage_q = wastage_q.filter(StockMovement.created_at >= start_date)
        if end_date:
            wastage_q = wastage_q.filter(StockMovement.created_at <= end_date)
            
        wastage_records = wastage_q.all()
        wastage_cost = sum(abs(float(r[0])) * float(r[1]) for r in wastage_records)

        net_operating_result = gross_profit - total_expenses - wastage_cost

        return {
            'total_revenue': round(total_revenue, 2),
            'total_cogs': round(total_cogs, 2),
            'gross_profit': round(gross_profit, 2),
            'gross_margin_percent': round((gross_profit / total_revenue * 100) if total_revenue > 0 else 0, 2),
            'operating_expenses': round(total_expenses, 2),
            'wastage_cost': round(wastage_cost, 2),
            'net_operating_result': round(net_operating_result, 2),
            'net_profit_percent': round((net_operating_result / total_revenue * 100) if total_revenue > 0 else 0, 2),
            'total_bills': total_bills
        }

    @staticmethod
    def export_excel_report(report_type: str, start_date=None, end_date=None) -> io.BytesIO:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if report_type == 'sales':
                df = ReportService.get_sales_dataframe(start_date, end_date)
                if df.empty:
                    df = pd.DataFrame([{'Notice': 'No sales records for selected period'}])
                df.to_excel(writer, sheet_name='Sales Summary', index=False)
            elif report_type == 'products':
                df = ReportService.get_product_sales_dataframe(start_date, end_date)
                if df.empty:
                    df = pd.DataFrame([{'Notice': 'No product records found'}])
                df.to_excel(writer, sheet_name='Product Performance', index=False)
            elif report_type == 'pnl':
                pnl = ReportService.calculate_profit_loss(start_date, end_date)
                pnl_data = [
                    {'Metric': 'Total Sales Revenue (Net)', 'Amount (INR)': pnl['total_revenue']},
                    {'Metric': 'Cost of Goods Sold (COGS)', 'Amount (INR)': pnl['total_cogs']},
                    {'Metric': 'Gross Profit', 'Amount (INR)': pnl['gross_profit']},
                    {'Metric': 'Gross Margin %', 'Amount (INR)': f"{pnl['gross_margin_percent']}%"},
                    {'Metric': 'Operating Expenses (Rent, Cold Chain, Staff)', 'Amount (INR)': pnl['operating_expenses']},
                    {'Metric': 'Wastage & Trimming Loss Cost', 'Amount (INR)': pnl['wastage_cost']},
                    {'Metric': 'Net Operating Result (EBITDA)', 'Amount (INR)': pnl['net_operating_result']},
                    {'Metric': 'Net Operating Margin %', 'Amount (INR)': f"{pnl['net_profit_percent']}%"},
                    {'Metric': 'Total Invoices Count', 'Amount (INR)': pnl['total_bills']}
                ]
                pd.DataFrame(pnl_data).to_excel(writer, sheet_name='Profit & Loss', index=False)
            else:
                # Inventory report
                inv_items = Inventory.query.all()
                data = [{
                    'Product': item.product.name if item.product else 'Unknown',
                    'SKU': item.product.sku if item.product else '',
                    'Category': item.product.category if item.product else '',
                    'Stock Balance': item.current_stock,
                    'Unit': item.unit,
                    'Cost Price': item.product.cost_price if item.product else 0,
                    'Selling Price': item.product.selling_price if item.product else 0,
                    'Stock Value': round(item.current_stock * (item.product.cost_price if item.product else 0), 2),
                    'Min Alert Level': item.product.min_stock_level if item.product else 5.0
                } for item in inv_items]
                pd.DataFrame(data).to_excel(writer, sheet_name='Inventory Ledger', index=False)

        output.seek(0)
        return output

    @staticmethod
    def export_pdf_report(report_type: str, start_date=None, end_date=None) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        elements = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#881337'),
            spaceAfter=6
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#4b5563'),
            spaceAfter=15
        )

        elements.append(Paragraph(f"FRESH CUT MEAT SHOP - {report_type.upper()} REPORT", title_style))
        elements.append(Paragraph(f"Generated on {datetime.now().strftime('%d %b %Y %H:%M')} | Currency: INR", subtitle_style))

        if report_type == 'pnl':
            pnl = ReportService.calculate_profit_loss(start_date, end_date)
            table_data = [
                ['Metric Description', 'Financial Result (₹)'],
                ['Total Sales Revenue', f"₹{pnl['total_revenue']:,.2f}"],
                ['Less: Cost of Goods Sold (COGS)', f"₹{pnl['total_cogs']:,.2f}"],
                ['GROSS PROFIT', f"₹{pnl['gross_profit']:,.2f} ({pnl['gross_margin_percent']}%)"],
                ['Less: Operating Expenses (Utilities, Packaging, Wages)', f"₹{pnl['operating_expenses']:,.2f}"],
                ['Less: Wastage & Trimming Spoilage', f"₹{pnl['wastage_cost']:,.2f}"],
                ['NET OPERATING RESULT', f"₹{pnl['net_operating_result']:,.2f} ({pnl['net_profit_percent']}%)"],
                ['Total Bills Processed', str(pnl['total_bills'])]
            ]
            t = Table(table_data, colWidths=[340, 180])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#881337')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 10),
                ('BOTTOMPADDING', (0,0), (-1,0), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
                ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#f0fdf4')),
                ('TEXTCOLOR', (0,3), (-1,3), colors.HexColor('#166534')),
                ('FONTNAME', (0,3), (-1,3), 'Helvetica-Bold'),
                ('BACKGROUND', (0,6), (-1,6), colors.HexColor('#eff6ff')),
                ('TEXTCOLOR', (0,6), (-1,6), colors.HexColor('#1e40af')),
                ('FONTNAME', (0,6), (-1,6), 'Helvetica-Bold'),
            ]))
            elements.append(t)
        else:
            # Sales summary table
            df = ReportService.get_sales_dataframe(start_date, end_date)
            if df.empty:
                elements.append(Paragraph("No transaction records found for selected period.", styles['Normal']))
            else:
                table_data = [['Invoice', 'Date', 'Cashier', 'Revenue (₹)', 'Payment']]
                for _, row in df.head(20).iterrows():
                    table_data.append([
                        str(row['Invoice']),
                        str(row['Date']),
                        str(row['Cashier']),
                        f"₹{row['Revenue']:,.2f}",
                        str(row['PaymentMethod'])
                    ])
                t = Table(table_data, colWidths=[110, 120, 110, 100, 80])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#065f46')),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,0), 9),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
                    ('FONTSIZE', (0,1), (-1,-1), 8),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9fafb')])
                ]))
                elements.append(t)

        doc.build(elements)
        buffer.seek(0)
        return buffer
