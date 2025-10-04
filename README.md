# 🏛️ Barangay Burgos Complaint & Feedback Portal

A comprehensive Django web application for managing barangay complaints and feedback with role-based access control, modern glass morphism UI, and multi-language support.

## ✨ Key Features

### 🔐 User Authentication & Management

- **Advanced Registration System**
  - User registration with profile photo (required)
  - Verification document upload for residency proof
  - Username, email, phone number, and address collection
  - Chairman/Secretary approval required before account activation
  - Email notifications on approval/rejection

- **Role-Based Access Control**
  - **Resident**: Submit complaints and feedback, track status
  - **Barangay Secretary**: Manage complaints, approve users, respond to feedback
  - **Barangay Chairman**: Full system access, user management, system-wide oversight
  - **Additional Roles**: Kagawad positions, Lupon members, BADAC, BDRRMC, and more

- **User Management Dashboard** (Chairman Only)
  - View all registered users with complete details
  - Activate/Deactivate user accounts via AJAX
  - Soft delete with account anonymization fallback
  - Real-time updates without page reload
  - Filter and search functionality

### 📋 Complaint Management System

- **Resident Features**
  - Submit complaints with rich details:
    - Category selection (Infrastructure, Health, Peace & Order, etc.)
    - Title and detailed description
    - Location information with GPS coordinates
    - Priority levels (Low, Medium, High, Critical)
    - Multiple file attachments (images, videos, documents)
    - Anonymous submission option
  - Track complaint status in real-time
  - Receive email notifications on status changes
  - View complaint history and timeline
  - Add comments and updates

- **Secretary/Chairman Features**
  - View and manage all complaints
  - Update complaint statuses (Pending → In Progress → Resolved)
  - Assign complaints to specific officials
  - Add internal notes and comments
  - Mark complaints as resolved with proof
  - Secretary approval system for complaint processing
  - Generate reports and statistics

- **Status Tracking**
  - Pending: Newly submitted
  - Pending Secretary Approval: Awaiting review
  - In Progress: Being addressed
  - Resolved: Completed with proof
  - Closed: Archived

### 💬 Feedback & Rating System

- **Feedback Submission**
  - Star rating system (1-5 stars)
  - Feedback type categories:
    - General Feedback
    - Complaint
    - Suggestion
    - Appreciation
    - Other
  - Detailed feedback with title and description
  - File attachment support
  - Anonymous feedback option
  - Beautiful glass morphism UI

- **Admin Response**
  - Secretary/Chairman can respond to feedback
  - Public and private response options
  - Feedback status management
  - Analytics and insights

### 🎨 Modern UI/UX Design

- **Glass Morphism Design**
  - Beautiful frosted glass effect throughout
  - Backdrop blur with transparency
  - Modern, professional appearance
  - Consistent design language across all pages

- **Responsive Design**
  - Mobile-first approach
  - Optimized for phones, tablets, and desktops
  - Touch-friendly buttons (44px minimum)
  - Adaptive layouts for all screen sizes
  - Cross-device viewing (register on mobile, view on PC)

- **User Experience Enhancements**
  - Quick action buttons with smart redirects
  - Login required for complaint submission
  - Automatic redirect after login to intended page
  - AJAX-based operations (no page reload)
  - Real-time form validation
  - Loading states and animations

### 🌐 Multi-Language Support

- **Languages Available**
  - English (en)
  - Filipino (fil)
  - Easy language switching
  - All UI elements translated

### 📊 Dashboard System

- **Resident Dashboard**
  - Personal complaint tracker
  - Submission history
  - Feedback overview
  - Quick actions: File complaint, Submit feedback

- **Secretary Dashboard**
  - All complaints overview with filters
  - Pending approvals list
  - Statistics and metrics
  - User management (approval/rejection)
  - Quick actions for complaint management

- **Chairman Dashboard**
  - System-wide statistics and analytics
  - User registration approvals
  - Complete oversight of all operations
  - Report generation
  - User management (activate/deactivate/delete)

### 🔒 Security Features

- **Authentication & Authorization**
  - CSRF protection on all forms
  - Login required for sensitive operations
  - Role-based permissions
  - Session management
  - Secure password hashing

- **Data Protection**
  - User input validation and sanitization
  - SQL injection protection via Django ORM
  - XSS protection via template escaping
  - File type restrictions for uploads
  - File size limits (10MB for photos, 50MB for documents)

- **User Privacy**
  - Anonymous submission options
  - Soft delete with data anonymization
  - Secure document storage
  - GDPR-friendly user data handling

### 📧 Notification System

- **Email Notifications**
  - User registration approval/rejection
  - Complaint status updates
  - Assignment notifications for officials
  - Feedback responses

### 📱 Additional Features

- **Profile Management**
  - Update personal information
  - Change profile photo
  - Update contact details
  - View and edit address with map integration

- **Document Management**
  - Upload and store verification documents
  - View submitted documents
  - Secure file storage

- **Search & Filter**
  - Advanced complaint search
  - Filter by status, category, priority
  - Date range filtering
  - User search in management pages

---

## 🛠️ Technology Stack

- **Backend**: Django 4.2+
- **Frontend**: 
  - Bootstrap 5
  - HTML5, CSS3 (Glass Morphism)
  - JavaScript (Vanilla + AJAX)
  - Font Awesome icons
- **Database**: 
  - SQLite (development)
  - PostgreSQL (production on Railway)
- **File Storage**: Django's media handling with Pillow
- **Deployment**: Railway (cloud hosting)
- **Version Control**: Git & GitHub

---

## 📦 Installation & Setup

### Prerequisites

- Python 3.11+
- pip (Python package manager)
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/qwertyuiop547/mywebapp.git
   cd mywebapp
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Mac/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Edit .env with your settings:
   # - SECRET_KEY
   # - DEBUG=True (for development)
   # - ALLOWED_HOSTS=localhost,127.0.0.1
   # - Database settings
   # - Email settings (optional for development)
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser (Chairman account)**
   ```bash
   python manage.py createsuperuser
   # Follow prompts to create username, email, password
   ```

7. **Set superuser role to Chairman**
   ```bash
   python manage.py shell
   ```
   ```python
   from accounts.models import User
   user = User.objects.get(username='your_username')
   user.role = 'chairman'
   user.is_approved = True
   user.date_approved = timezone.now()
   user.save()
   exit()
   ```

8. **Load initial complaint categories** (optional)
   ```bash
   python manage.py shell
   ```
   ```python
   from complaints.models import ComplaintCategory
   
   categories = [
       ("Infrastructure", "Roads, bridges, drainage, public facilities"),
       ("Health & Sanitation", "Health concerns, sanitation, waste management"),
       ("Peace & Order", "Security concerns, noise complaints, public disturbances"),
       ("Social Services", "Community programs, welfare assistance"),
       ("Environment", "Pollution, illegal logging, environmental issues"),
       ("Animal Control", "Stray animals, animal-related concerns"),
       ("Others", "Other concerns not listed above")
   ]
   
   for name, desc in categories:
       ComplaintCategory.objects.get_or_create(
           name=name,
           defaults={'description': desc, 'is_active': True}
       )
   
   exit()
   ```

9. **Run development server**
   ```bash
   python manage.py runserver
   ```

10. **Access the application**
    - **Main Portal**: http://127.0.0.1:8000/
    - **Admin Panel**: http://127.0.0.1:8000/admin/
    - **English**: http://127.0.0.1:8000/en/
    - **Filipino**: http://127.0.0.1:8000/fil/

---

## 🚀 Production Deployment (Railway)

The application is deployed on Railway at:
**https://mywebapp-production-cd0d.up.railway.app**

### Deployment Configuration

1. **Environment Variables** (set in Railway):
   ```
   DEBUG=False
   SECRET_KEY=<your-production-secret-key>
   ALLOWED_HOSTS=mywebapp-production-cd0d.up.railway.app
   CSRF_TRUSTED_ORIGINS=https://mywebapp-production-cd0d.up.railway.app
   DATABASE_URL=<railway-postgres-url>
   ```

2. **Database**: PostgreSQL (automatically provisioned by Railway)

3. **Static Files**: Served via WhiteNoise

4. **Media Files**: Stored in Railway's persistent volume

---

## 📁 Project Structure

```
barangay_portal/
├── accounts/              # User authentication & management
│   ├── models.py         # User, UserVerificationDocument
│   ├── views.py          # Login, register, user approval, profile
│   ├── forms.py          # Registration, login, profile forms
│   └── templates/        # Login, register, approval pages
├── complaints/           # Complaint management system
│   ├── models.py         # Complaint, Category, Attachment, Comment
│   ├── views.py          # Create, list, detail, update complaints
│   ├── forms.py          # Complaint submission forms
│   └── templates/        # Complaint pages
├── feedback/             # Feedback & rating system
│   ├── models.py         # Feedback model
│   ├── views.py          # Submit, list, manage feedback
│   ├── forms.py          # Feedback forms
│   └── templates/        # Feedback pages
├── dashboard/            # Role-based dashboards
│   ├── views.py          # Resident, secretary, chairman dashboards
│   └── templates/        # Dashboard pages
├── templates/            # Shared HTML templates
│   ├── base.html         # Base template with navbar
│   ├── home.html         # Landing page
│   └── ...
├── static/               # CSS, JavaScript, images
│   ├── css/
│   ├── js/
│   └── images/
├── media/                # User uploaded files
│   ├── profile_photos/
│   ├── user_verifications/
│   ├── complaint_attachments/
│   └── feedback_attachments/
├── barangay_portal/      # Django project settings
│   ├── settings.py       # Main configuration
│   ├── urls.py           # URL routing
│   └── wsgi.py           # WSGI application
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not in git)
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

---

## 📚 User Workflows

### For Residents

1. **Register Account**
   - Fill out registration form with personal details
   - Upload profile photo (required)
   - Upload verification document (required - Barangay ID, utility bill, etc.)
   - Wait for Chairman/Secretary approval
   - Receive email notification when approved

2. **File a Complaint**
   - Login to your account
   - Click "File a Complaint" button
   - Select complaint category
   - Enter title, description, and location
   - Attach supporting files (optional)
   - Choose to submit anonymously (optional)
   - Submit and receive tracking number

3. **Track Complaints**
   - View all submitted complaints in dashboard
   - Check real-time status updates
   - Add comments or additional information
   - Receive email notifications on status changes

4. **Submit Feedback**
   - Rate your experience (1-5 stars)
   - Choose feedback type
   - Provide detailed feedback
   - Attach files if needed
   - Submit anonymously (optional)

### For Barangay Secretary

1. **Manage Complaints**
   - View all submitted complaints
   - Approve pending complaints
   - Update complaint status
   - Assign complaints to officials
   - Add internal notes
   - Mark as resolved with proof

2. **User Approval**
   - Review pending registrations
   - View user details and documents
   - Approve or reject registration requests
   - Manage active users

3. **Respond to Feedback**
   - Read submitted feedback
   - Respond to users
   - Mark feedback as addressed

### For Barangay Chairman

1. **System Oversight**
   - Access comprehensive dashboard with analytics
   - View all complaints and feedback
   - Monitor system activity

2. **User Management**
   - Approve/reject new registrations
   - Activate/deactivate user accounts
   - Delete accounts (with soft delete fallback)
   - View complete user profiles

3. **Generate Reports**
   - Complaint statistics
   - User registration trends
   - Feedback analysis

---

## ⚙️ Configuration

### File Upload Limits

- **Profile Photos**: 10MB max, image files only (JPG, PNG, GIF, BMP, WebP)
- **Verification Documents**: 50MB max, any file type
- **Complaint Attachments**: 10MB per file
- **Feedback Attachments**: 5MB per file

### Email Configuration

Edit `.env` file:
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

---

## 🧪 Development Commands

### Database Management
```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (CAUTION: deletes all data)
python manage.py flush

# Create database backup
python manage.py dumpdata > backup.json

# Load database backup
python manage.py loaddata backup.json
```

### Static Files
```bash
# Collect static files for production
python manage.py collectstatic --no-input
```

### Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test complaints
```

### Shell Commands
```bash
# Open Django shell
python manage.py shell

# Example: View all pending users
from accounts.models import User
User.objects.filter(is_approved=False)
```

---

## 🔧 Troubleshooting

### Common Issues

**Issue**: Categories not visible on complaint form
- **Solution**: Check CSS styling for select dropdowns, ensure white background with opacity

**Issue**: CSRF verification failed on Railway
- **Solution**: Add Railway URL to `CSRF_TRUSTED_ORIGINS` in settings.py

**Issue**: User deletion fails with database error
- **Solution**: System uses soft delete fallback - deactivates and anonymizes instead

**Issue**: Migration conflicts
- **Solution**: Run `python manage.py migrate --fake` to sync migration history

---

## 🤝 Contributing

This project is developed for Barangay Burgos, Basey, Samar. For contributions or issues:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## 📄 License

This project is developed for barangay community use and management.

---

## 👨‍💻 Developer

**Justin Echegorin**
- Email: echegorinjustin14@gmail.com
- GitHub: [@qwertyuiop547](https://github.com/qwertyuiop547)

---

## 🎯 Future Roadmap

- [ ] SMS notifications for complaint updates
- [ ] Mobile app (Android/iOS)
- [ ] Advanced analytics dashboard
- [ ] PDF report generation
- [ ] Integration with GIS mapping
- [ ] Dark mode toggle
- [ ] Real-time chat support
- [ ] Complaint resolution timeline view
- [ ] Multi-barangay support
- [ ] API for third-party integrations

---

## 📞 Support

For technical support or questions about the system:
- Email: echegorinjustin14@gmail.com
- GitHub Issues: https://github.com/qwertyuiop547/mywebapp/issues

---

**Made with ❤️ for Barangay Burgos, Basey, Samar**
