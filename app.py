from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date
from sqlalchemy import or_, and_
import os
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from io import BytesIO
import shutil
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tenant-management-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tenant_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, inactive, moved_out
    
    # Relationships
    leases = db.relationship('Lease', backref='tenant', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='tenant', lazy=True, cascade='all, delete-orphan')
    maintenance_requests = db.relationship('MaintenanceRequest', backref='tenant', lazy=True, cascade='all, delete-orphan')

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), unique=True, nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 1BHK, 2BHK, etc.
    area = db.Column(db.Float)  # in sqft
    rent_amount = db.Column(db.Float, nullable=False)
    deposit_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='available')  # available, occupied, maintenance
    
    # Relationships
    leases = db.relationship('Lease', backref='unit', lazy=True)

class Lease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    monthly_rent = db.Column(db.Float, nullable=False)
    deposit_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, expired, terminated
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    invoices = db.relationship('Invoice', backref='lease', lazy=True, cascade='all, delete-orphan')

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lease_id = db.Column(db.Integer, db.ForeignKey('lease.id'), nullable=False)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    month_year = db.Column(db.String(20), nullable=False)  # MM-YYYY
    rent_amount = db.Column(db.Float, nullable=False)
    utility_amount = db.Column(db.Float, default=0)
    other_charges = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid, overdue
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'), nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # cash, check, bank_transfer, online
    reference_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

class UtilityBill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    utility_type = db.Column(db.String(50), nullable=False)  # electricity, gas, water, internet
    month_year = db.Column(db.String(20), nullable=False)  # MM-YYYY
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid
    bill_number = db.Column(db.String(100))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

class MaintenanceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    category = db.Column(db.String(50), nullable=False)  # plumbing, electrical, hvac, general
    cost = db.Column(db.Float, default=0)
    assigned_to = db.Column(db.String(100))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_date = db.Column(db.DateTime)
    admin_notes = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# Helper Functions
def generate_invoice_number():
    last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
    if last_invoice:
        last_num = int(last_invoice.invoice_number.split('-')[1])
        return f"INV-{last_num + 1:06d}"
    return "INV-000001"

def create_monthly_invoices():
    """Create monthly invoices for all active leases"""
    current_date = datetime.now()
    month_year = current_date.strftime("%m-%Y")
    
    active_leases = Lease.query.filter_by(status='active').all()
    
    for lease in active_leases:
        # Check if invoice already exists for this month
        existing_invoice = Invoice.query.filter_by(
            lease_id=lease.id,
            month_year=month_year
        ).first()
        
        if not existing_invoice:
            # Calculate utility charges for the unit
            utility_total = db.session.query(db.func.sum(UtilityBill.amount)).filter(
                UtilityBill.unit_id == lease.unit_id,
                UtilityBill.month_year == month_year,
                UtilityBill.status == 'pending'
            ).scalar() or 0
            
            invoice = Invoice(
                lease_id=lease.id,
                invoice_number=generate_invoice_number(),
                month_year=month_year,
                rent_amount=lease.monthly_rent,
                utility_amount=utility_total,
                total_amount=lease.monthly_rent + utility_total,
                due_date=current_date.replace(day=10) + timedelta(days=32)  # 10th of next month
            )
            db.session.add(invoice)
    
    db.session.commit()

def update_overdue_invoices():
    """Update invoice status to overdue if past due date"""
    current_date = date.today()
    overdue_invoices = Invoice.query.filter(
        Invoice.due_date < current_date,
        Invoice.status == 'pending'
    ).all()
    
    for invoice in overdue_invoices:
        invoice.status = 'overdue'
    
    db.session.commit()

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Dashboard statistics
    total_tenants = Tenant.query.filter_by(status='active').count()
    total_units = Unit.query.count()
    occupied_units = Unit.query.filter_by(status='occupied').count()
    available_units = total_units - occupied_units
    
    # Recent maintenance requests
    recent_maintenance = MaintenanceRequest.query.filter(
        MaintenanceRequest.status.in_(['open', 'in_progress'])
    ).order_by(MaintenanceRequest.created_date.desc()).limit(5).all()
    
    # Overdue invoices
    overdue_invoices = Invoice.query.filter_by(status='overdue').count()
    
    # Due this month
    current_month = datetime.now().strftime("%m-%Y")
    monthly_revenue = db.session.query(db.func.sum(Invoice.total_amount)).filter(
        Invoice.month_year == current_month,
        Invoice.status == 'paid'
    ).scalar() or 0
    
    pending_payments = Invoice.query.filter(
        Invoice.month_year == current_month,
        Invoice.status.in_(['pending', 'overdue'])
    ).count()
    
    return render_template('dashboard.html',
                         total_tenants=total_tenants,
                         total_units=total_units,
                         occupied_units=occupied_units,
                         available_units=available_units,
                         recent_maintenance=recent_maintenance,
                         overdue_invoices=overdue_invoices,
                         monthly_revenue=monthly_revenue,
                         pending_payments=pending_payments)

@app.route('/tenants')
@login_required
def tenants():
    search = request.args.get('search', '')
    floor = request.args.get('floor', '')
    status = request.args.get('status', '')
    
    query = Tenant.query
    
    if search:
        query = query.filter(or_(
            Tenant.name.contains(search),
            Tenant.email.contains(search),
            Tenant.phone.contains(search)
        ))
    
    if status:
        query = query.filter_by(status=status)
    
    if floor:
        # Join with lease and unit to filter by floor
        query = query.join(Lease).join(Unit).filter(Unit.floor == int(floor))
    
    tenants = query.all()
    floors = db.session.query(Unit.floor).distinct().all()
    floors = [f[0] for f in floors]
    
    return render_template('tenants.html', tenants=tenants, floors=floors,
                         search=search, selected_floor=floor, selected_status=status)

@app.route('/tenant/add', methods=['GET', 'POST'])
@login_required
def add_tenant():
    if request.method == 'POST':
        tenant = Tenant(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            address=request.form['address'],
            emergency_contact=request.form['emergency_contact'],
            emergency_phone=request.form['emergency_phone']
        )
        
        db.session.add(tenant)
        db.session.commit()
        flash('Tenant added successfully!', 'success')
        return redirect(url_for('tenants'))
    
    return render_template('add_tenant.html')

@app.route('/tenant/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_tenant(id):
    tenant = Tenant.query.get_or_404(id)
    
    if request.method == 'POST':
        tenant.name = request.form['name']
        tenant.email = request.form['email']
        tenant.phone = request.form['phone']
        tenant.address = request.form['address']
        tenant.emergency_contact = request.form['emergency_contact']
        tenant.emergency_phone = request.form['emergency_phone']
        tenant.status = request.form['status']
        
        db.session.commit()
        flash('Tenant updated successfully!', 'success')
        return redirect(url_for('tenants'))
    
    return render_template('edit_tenant.html', tenant=tenant)

@app.route('/tenant/delete/<int:id>')
@login_required
def delete_tenant(id):
    tenant = Tenant.query.get_or_404(id)
    db.session.delete(tenant)
    db.session.commit()
    flash('Tenant deleted successfully!', 'success')
    return redirect(url_for('tenants'))

@app.route('/units')
@login_required
def units():
    units = Unit.query.order_by(Unit.floor, Unit.number).all()
    return render_template('units.html', units=units)

@app.route('/unit/add', methods=['GET', 'POST'])
@login_required
def add_unit():
    if request.method == 'POST':
        unit = Unit(
            number=request.form['number'],
            floor=int(request.form['floor']),
            type=request.form['type'],
            area=float(request.form['area']) if request.form['area'] else None,
            rent_amount=float(request.form['rent_amount']),
            deposit_amount=float(request.form['deposit_amount'])
        )
        
        db.session.add(unit)
        db.session.commit()
        flash('Unit added successfully!', 'success')
        return redirect(url_for('units'))
    
    return render_template('add_unit.html')

@app.route('/unit/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_unit(id):
    unit = Unit.query.get_or_404(id)
    
    if request.method == 'POST':
        unit.number = request.form['number']
        unit.floor = int(request.form['floor'])
        unit.type = request.form['type']
        unit.area = float(request.form['area']) if request.form['area'] else None
        unit.rent_amount = float(request.form['rent_amount'])
        unit.deposit_amount = float(request.form['deposit_amount'])
        unit.status = request.form['status']
        
        db.session.commit()
        flash('Unit updated successfully!', 'success')
        return redirect(url_for('units'))
    
    return render_template('edit_unit.html', unit=unit)

@app.route('/leases')
@login_required
def leases():
    leases = Lease.query.join(Tenant).join(Unit).all()
    return render_template('leases.html', leases=leases)

@app.route('/lease/add', methods=['GET', 'POST'])
@login_required
def add_lease():
    if request.method == 'POST':
        # Update unit status to occupied
        unit = Unit.query.get(int(request.form['unit_id']))
        unit.status = 'occupied'
        
        lease = Lease(
            tenant_id=int(request.form['tenant_id']),
            unit_id=int(request.form['unit_id']),
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date(),
            monthly_rent=float(request.form['monthly_rent']),
            deposit_amount=float(request.form['deposit_amount'])
        )
        
        db.session.add(lease)
        db.session.commit()
        flash('Lease created successfully!', 'success')
        return redirect(url_for('leases'))
    
    tenants = Tenant.query.filter_by(status='active').all()
    available_units = Unit.query.filter_by(status='available').all()
    
    return render_template('add_lease.html', tenants=tenants, units=available_units)

@app.route('/invoices')
@login_required
def invoices():
    status_filter = request.args.get('status', '')
    month_filter = request.args.get('month', '')
    
    query = Invoice.query.join(Lease).join(Tenant)
    
    if status_filter:
        query = query.filter(Invoice.status == status_filter)
    
    if month_filter:
        query = query.filter(Invoice.month_year == month_filter)
    
    invoices = query.order_by(Invoice.created_date.desc()).all()
    
    # Get distinct months for filter
    months = db.session.query(Invoice.month_year).distinct().order_by(Invoice.month_year.desc()).all()
    months = [m[0] for m in months]
    
    return render_template('invoices.html', invoices=invoices, months=months,
                         selected_status=status_filter, selected_month=month_filter)

@app.route('/invoice/generate')
@login_required
def generate_invoices():
    create_monthly_invoices()
    flash('Monthly invoices generated successfully!', 'success')
    return redirect(url_for('invoices'))

@app.route('/payments')
@login_required
def payments():
    payments = Payment.query.join(Tenant).order_by(Payment.payment_date.desc()).all()
    return render_template('payments.html', payments=payments)

@app.route('/payment/add', methods=['GET', 'POST'])
@login_required
def add_payment():
    if request.method == 'POST':
        payment = Payment(
            tenant_id=int(request.form['tenant_id']),
            invoice_id=int(request.form['invoice_id']) if request.form['invoice_id'] else None,
            amount=float(request.form['amount']),
            payment_date=datetime.strptime(request.form['payment_date'], '%Y-%m-%d').date(),
            payment_method=request.form['payment_method'],
            reference_number=request.form['reference_number'],
            notes=request.form['notes']
        )
        
        # If payment is for an invoice, update invoice status
        if payment.invoice_id:
            invoice = Invoice.query.get(payment.invoice_id)
            if payment.amount >= invoice.total_amount:
                invoice.status = 'paid'
        
        db.session.add(payment)
        db.session.commit()
        flash('Payment recorded successfully!', 'success')
        return redirect(url_for('payments'))
    
    tenants = Tenant.query.filter_by(status='active').all()
    pending_invoices = Invoice.query.filter(Invoice.status.in_(['pending', 'overdue'])).all()
    
    return render_template('add_payment.html', tenants=tenants, invoices=pending_invoices)

@app.route('/utilities')
@login_required
def utilities():
    bills = UtilityBill.query.join(Unit).order_by(UtilityBill.created_date.desc()).all()
    return render_template('utilities.html', bills=bills)

@app.route('/utility/add', methods=['GET', 'POST'])
@login_required
def add_utility():
    if request.method == 'POST':
        bill = UtilityBill(
            unit_id=int(request.form['unit_id']),
            utility_type=request.form['utility_type'],
            month_year=request.form['month_year'],
            amount=float(request.form['amount']),
            due_date=datetime.strptime(request.form['due_date'], '%Y-%m-%d').date(),
            bill_number=request.form['bill_number']
        )
        
        db.session.add(bill)
        db.session.commit()
        flash('Utility bill added successfully!', 'success')
        return redirect(url_for('utilities'))
    
    units = Unit.query.filter_by(status='occupied').all()
    return render_template('add_utility.html', units=units)

@app.route('/maintenance')
@login_required
def maintenance():
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    
    query = MaintenanceRequest.query.join(Tenant)
    
    if status_filter:
        query = query.filter(MaintenanceRequest.status == status_filter)
    
    if priority_filter:
        query = query.filter(MaintenanceRequest.priority == priority_filter)
    
    requests = query.order_by(MaintenanceRequest.created_date.desc()).all()
    
    return render_template('maintenance.html', requests=requests,
                         selected_status=status_filter, selected_priority=priority_filter)

@app.route('/maintenance/add', methods=['GET', 'POST'])
@login_required
def add_maintenance():
    if request.method == 'POST':
        request_obj = MaintenanceRequest(
            tenant_id=int(request.form['tenant_id']),
            title=request.form['title'],
            description=request.form['description'],
            priority=request.form['priority'],
            category=request.form['category']
        )
        
        db.session.add(request_obj)
        db.session.commit()
        flash('Maintenance request added successfully!', 'success')
        return redirect(url_for('maintenance'))
    
    tenants = Tenant.query.filter_by(status='active').all()
    return render_template('add_maintenance.html', tenants=tenants)

@app.route('/maintenance/update/<int:id>', methods=['POST'])
@login_required
def update_maintenance(id):
    maintenance_request = MaintenanceRequest.query.get_or_404(id)
    
    maintenance_request.status = request.form['status']
    maintenance_request.assigned_to = request.form['assigned_to']
    maintenance_request.cost = float(request.form['cost']) if request.form['cost'] else 0
    maintenance_request.admin_notes = request.form['admin_notes']
    
    if request.form['status'] in ['resolved', 'closed']:
        maintenance_request.resolved_date = datetime.utcnow()
    
    db.session.commit()
    flash('Maintenance request updated successfully!', 'success')
    return redirect(url_for('maintenance'))

@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html')

@app.route('/export/tenants/<format>')
@login_required
def export_tenants(format):
    tenants = Tenant.query.all()
    
    if format == 'pdf':
        return generate_tenants_pdf(tenants)
    elif format == 'excel':
        return generate_tenants_excel(tenants)

@app.route('/export/payments/<format>')
@login_required
def export_payments(format):
    payments = Payment.query.join(Tenant).all()
    
    if format == 'pdf':
        return generate_payments_pdf(payments)
    elif format == 'excel':
        return generate_payments_excel(payments)

def generate_tenants_pdf(tenants):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("Tenants Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Data
    data = [['Name', 'Email', 'Phone', 'Status']]
    for tenant in tenants:
        data.append([tenant.name, tenant.email, tenant.phone, tenant.status.title()])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='tenants_report.pdf', mimetype='application/pdf')

def generate_tenants_excel(tenants):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Tenants Report"
    
    # Headers
    headers = ['Name', 'Email', 'Phone', 'Address', 'Emergency Contact', 'Status', 'Created Date']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
    
    # Data
    for row, tenant in enumerate(tenants, 2):
        ws.cell(row=row, column=1, value=tenant.name)
        ws.cell(row=row, column=2, value=tenant.email)
        ws.cell(row=row, column=3, value=tenant.phone)
        ws.cell(row=row, column=4, value=tenant.address)
        ws.cell(row=row, column=5, value=tenant.emergency_contact)
        ws.cell(row=row, column=6, value=tenant.status.title())
        ws.cell(row=row, column=7, value=tenant.created_date.strftime('%Y-%m-%d'))
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name='tenants_report.xlsx', 
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

def generate_payments_pdf(payments):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("Payments Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Data
    data = [['Tenant', 'Amount', 'Date', 'Method']]
    for payment in payments:
        data.append([payment.tenant.name, f"${payment.amount:.2f}", 
                    payment.payment_date.strftime('%Y-%m-%d'), payment.payment_method.title()])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='payments_report.pdf', mimetype='application/pdf')

def generate_payments_excel(payments):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Payments Report"
    
    # Headers
    headers = ['Tenant', 'Amount', 'Payment Date', 'Method', 'Reference', 'Notes']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
    
    # Data
    for row, payment in enumerate(payments, 2):
        ws.cell(row=row, column=1, value=payment.tenant.name)
        ws.cell(row=row, column=2, value=payment.amount)
        ws.cell(row=row, column=3, value=payment.payment_date.strftime('%Y-%m-%d'))
        ws.cell(row=row, column=4, value=payment.payment_method.title())
        ws.cell(row=row, column=5, value=payment.reference_number)
        ws.cell(row=row, column=6, value=payment.notes)
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name='payments_report.xlsx', 
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/backup')
@login_required
def backup():
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'{backup_dir}/tenant_management_backup_{timestamp}.db'
    
    shutil.copy2('tenant_management.db', backup_file)
    
    flash(f'Database backed up successfully to {backup_file}', 'success')
    return redirect(url_for('dashboard'))

@app.route('/api/notifications')
@login_required
def notifications():
    notifications = []
    
    # Overdue invoices
    overdue_count = Invoice.query.filter_by(status='overdue').count()
    if overdue_count > 0:
        notifications.append({
            'type': 'warning',
            'message': f'{overdue_count} invoice(s) are overdue',
            'url': url_for('invoices', status='overdue')
        })
    
    # Open maintenance requests
    open_maintenance = MaintenanceRequest.query.filter_by(status='open').count()
    if open_maintenance > 0:
        notifications.append({
            'type': 'info',
            'message': f'{open_maintenance} open maintenance request(s)',
            'url': url_for('maintenance', status='open')
        })
    
    # High priority maintenance
    urgent_maintenance = MaintenanceRequest.query.filter_by(priority='urgent', status='open').count()
    if urgent_maintenance > 0:
        notifications.append({
            'type': 'danger',
            'message': f'{urgent_maintenance} urgent maintenance request(s)',
            'url': url_for('maintenance', priority='urgent')
        })
    
    return jsonify(notifications)

# Initialize database and create admin user
def create_tables():
    with app.app_context():
        db.create_all()
        
        # Create admin user if doesn't exist
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(
                username='admin',
                password_hash=generate_password_hash('12345')
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin user created (admin/12345)")
        
        print("✅ Database initialized successfully")

# Background scheduler for automatic tasks
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_overdue_invoices, trigger="interval", hours=1)
scheduler.add_job(func=create_monthly_invoices, trigger="cron", day=1, hour=0)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host='0.0.0.0', port=5000)