# Tenant Management System

A comprehensive web-based Tenant Management System designed for residential building management with modern UI/UX, secure database practices, and clean modular code architecture.

## 🏢 Features

### Core Functionality
- **Admin Authentication** (Username: `admin`, Password: `12345`)
- **Tenant Management** - Add, Edit, Delete, and View tenant profiles
- **Unit Management** - Manage units/flats with occupancy tracking
- **Lease Management** - Create and manage lease agreements with automatic unit assignment
- **Rent Collection** - Due date tracking and payment management
- **Invoice Generation** - Automated monthly invoice creation
- **Payment Tracking** - Multiple payment methods and receipt generation
- **Utility Bills Management** - Track electricity, gas, water, internet bills
- **Maintenance System** - Request creation, assignment, and status tracking
- **Search & Filter** - Advanced filtering by floor, unit, status, etc.
- **Export Capabilities** - PDF and Excel reports for tenants and payments
- **Backup & Restore** - Database backup functionality

### Advanced Features
- **Responsive Dashboard** with real-time statistics
- **Real-time Notifications** for due rent and maintenance updates
- **Automatic Invoice Generation** (scheduled monthly)
- **Overdue Payment Tracking** with automatic status updates
- **Priority-based Maintenance Requests** with visual indicators
- **Interactive Charts** and analytics
- **Modern UI/UX Design** with Bootstrap 5 and custom CSS
- **Auto-save Forms** with client-side data persistence
- **Table Sorting** and real-time search functionality

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ installed
- Web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Clone or download** this repository to your local machine

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the system**:
   - Open your web browser
   - Go to: `http://localhost:5000`
   - Login with:
     - **Username**: `admin`
     - **Password**: `12345`

## 📱 System Overview

### Dashboard
- Real-time statistics (tenants, units, revenue, maintenance)
- Quick action buttons for common tasks
- Occupancy overview with visual charts
- Alert system for overdue payments and maintenance
- Recent activity tracking

### Tenant Management
- Complete tenant profiles with emergency contacts
- Status tracking (Active, Inactive, Moved Out)
- Search and filter by multiple criteria
- Export capabilities (PDF/Excel)
- Payment history and lease information

### Unit Management
- Visual unit cards with status indicators
- Floor and type categorization
- Rent and deposit amount tracking
- Current tenant assignment
- Availability status management

### Lease Management
- Tenant-unit assignment with lease terms
- Start and end date tracking
- Monthly rent and deposit management
- Lease status monitoring (Active, Expired, Terminated)
- Automatic unit status updates

### Financial Management
- **Invoices**: Monthly generation with utility inclusion
- **Payments**: Multiple payment methods supported
- **Due Date Tracking**: Automatic overdue status updates
- **Payment History**: Complete audit trail
- **Receipt Generation**: Professional payment receipts

### Maintenance System
- **Request Management**: Create, assign, and track requests
- **Priority Levels**: Low, Medium, High, Urgent with visual indicators
- **Categories**: Plumbing, Electrical, HVAC, General, etc.
- **Status Tracking**: Open, In Progress, Resolved, Closed
- **Cost Tracking**: Record maintenance expenses
- **Assignment System**: Assign requests to maintenance staff

### Utility Management
- **Bill Tracking**: Electricity, Gas, Water, Internet, etc.
- **Monthly Billing**: Automatic inclusion in rent invoices
- **Due Date Management**: Track utility payment deadlines
- **Status Updates**: Mark bills as paid/pending

### Reports & Analytics
- **Export Options**: PDF and Excel formats
- **Visual Analytics**: Charts and graphs for insights
- **Financial Reports**: Revenue tracking and collection rates
- **Occupancy Reports**: Unit utilization statistics
- **Maintenance Analytics**: Request categorization and trends

## 🔧 Technical Architecture

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with session management
- **Scheduling**: APScheduler for automated tasks
- **PDF Generation**: ReportLab
- **Excel Export**: OpenPyXL

### Frontend
- **Framework**: Bootstrap 5 for responsive design
- **JavaScript**: jQuery for dynamic interactions
- **Charts**: Chart.js for data visualization
- **Icons**: Font Awesome 6
- **Styling**: Custom CSS with modern gradients and animations

### Database Schema
- **Admin**: User authentication
- **Tenant**: Tenant information and contacts
- **Unit**: Property units with specifications
- **Lease**: Tenant-unit agreements
- **Invoice**: Monthly billing records
- **Payment**: Payment tracking and history
- **UtilityBill**: Utility expense management
- **MaintenanceRequest**: Maintenance workflow

### Security Features
- **Password Hashing**: Werkzeug security for admin passwords
- **Session Management**: Secure login sessions
- **Input Validation**: Form validation and sanitization
- **CSRF Protection**: Flask-WTF for form security
- **SQL Injection Prevention**: SQLAlchemy ORM

## 📊 Key Functionalities

### Automated Processes
- **Monthly Invoice Generation**: Automatic creation on the 1st of each month
- **Overdue Tracking**: Hourly checks for overdue invoices
- **Status Updates**: Automatic lease and payment status management
- **Notification System**: Real-time alerts for important events

### Data Management
- **Auto-save**: Client-side form data persistence
- **Backup System**: Database backup with timestamp
- **Export Functions**: Professional PDF and Excel reports
- **Search & Filter**: Advanced filtering across all modules

### User Experience
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Visual Feedback**: Loading states, success/error messages
- **Interactive Elements**: Sortable tables, dynamic forms
- **Modern UI**: Clean design with intuitive navigation

## 🛠️ Configuration

### Default Settings
- **Admin Credentials**: admin/12345
- **Database**: SQLite (tenant_management.db)
- **Port**: 5000
- **Debug Mode**: Enabled for development

### Customization Options
- **Database**: Can be changed to PostgreSQL/MySQL by updating the connection string
- **Styling**: Modify `static/css/style.css` for custom themes
- **Features**: Enable/disable modules by commenting out routes in `app.py`

## 📁 File Structure

```
tenant-management-system/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── login.html        # Login page
│   ├── dashboard.html    # Main dashboard
│   ├── tenants.html      # Tenant listing
│   ├── add_tenant.html   # Add tenant form
│   ├── edit_tenant.html  # Edit tenant form
│   ├── units.html        # Unit management
│   ├── add_unit.html     # Add unit form
│   ├── leases.html       # Lease management
│   ├── add_lease.html    # Create lease form
│   ├── invoices.html     # Invoice listing
│   ├── payments.html     # Payment tracking
│   ├── add_payment.html  # Payment recording
│   ├── maintenance.html  # Maintenance requests
│   ├── add_maintenance.html # Add maintenance form
│   ├── utilities.html    # Utility bills
│   ├── add_utility.html  # Add utility form
│   └── reports.html      # Reports and analytics
├── static/               # Static assets
│   ├── css/
│   │   └── style.css     # Custom styling
│   ├── js/
│   │   └── app.js        # JavaScript functionality
│   └── images/           # Image assets
└── backups/              # Database backups (created automatically)
```

## 🔄 Workflow Examples

### Adding a New Tenant
1. Navigate to **Tenants** → **Add New Tenant**
2. Fill in tenant information (name, email, phone, emergency contact)
3. Save the tenant profile
4. Create a lease agreement in **Leases** → **Create New Lease**
5. Assign the tenant to an available unit
6. System automatically generates monthly invoices

### Processing Monthly Rent
1. System automatically generates invoices on the 1st of each month
2. View pending invoices in **Finance** → **Invoices**
3. Record payments in **Finance** → **Record Payment**
4. System automatically updates invoice status
5. Generate receipts for tenant records

### Handling Maintenance Requests
1. Create request in **Maintenance** → **Add Request**
2. Set priority level and category
3. Assign to maintenance staff
4. Update status as work progresses
5. Record costs and completion notes
6. Close request when resolved

## 🚨 Troubleshooting

### Common Issues

**Application won't start**
- Ensure Python 3.8+ is installed
- Install all requirements: `pip install -r requirements.txt`
- Check if port 5000 is available

**Can't login**
- Use default credentials: admin/12345
- Clear browser cache if needed
- Check if database file was created

**Missing features**
- Ensure all dependencies are installed
- Check browser console for JavaScript errors
- Verify all template files are present

**Database errors**
- Delete `tenant_management.db` to reset database
- Restart the application to recreate tables
- Check file permissions in the project directory

### Support
For technical support or feature requests, check the application logs in the terminal where you started the Flask server.

## 🔮 Future Enhancements

- **Multi-building Support**: Manage multiple properties
- **Tenant Portal**: Self-service portal for tenants
- **Mobile App**: Native mobile applications
- **SMS/Email Notifications**: Automated communication
- **Document Management**: Store and manage lease documents
- **Advanced Analytics**: Predictive analytics and reporting
- **Multi-language Support**: Internationalization
- **API Integration**: Third-party service integrations

## 📄 License

This project is created for educational and demonstration purposes. Feel free to modify and use according to your needs.

---

**Built with ❤️ using Flask, Bootstrap, and modern web technologies**
