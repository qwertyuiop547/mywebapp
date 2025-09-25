# Barangay Complaint & Feedback Portal

A Django web application for managing barangay complaints and feedback with role-based access control.

## Features

### User Authentication & Roles

- User registration and login system
- Three user roles: Resident, Barangay Secretary, Barangay Chairman
- Role-based access control with approval workflow
- Chairman approval required for new user registrations

### Complaint Management

- Residents can submit complaints with:
  - Category selection
  - Detailed descriptions
  - File attachments (images, videos, documents)
  - Location information
- Complaint status tracking (Pending, In-Progress, Resolved)
- Email notifications on status changes
- Comment system for updates and communication

### Dashboard System

- **Residents**: View submitted complaints and their statuses
- **Secretary**: Manage all complaints, update statuses, assign to officials
- **Chairman**: Overview reports, approve user registrations, system management

### Feedback System

- Star rating system (1-5 stars)
- Feedback categories and comments
- Admin response capability
- Anonymous feedback option

### Admin Panel

- Comprehensive Django admin interface
- User and complaint management
- Report generation capabilities
- System configuration

## Technology Stack

- **Backend**: Django 4.2+
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Styling**: Custom CSS with Bootstrap integration
- **File Handling**: Django's media handling with Pillow for images

## Installation & Setup

### Prerequisites
- Python 3.8+ 
- pip (Python package manager)

### Setup Instructions

1. **Clone and navigate to the project**
   ```bash
   cd c:/Users/JUSTIN/Documents/Project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (Chairman)**
   ```bash
   python manage.py createsuperuser
   # Set role to 'chairman' and is_approved to True via admin
   ```

6. **Load initial data (optional)**
   ```bash
   python manage.py shell
   # Run commands to create complaint categories
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main portal: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Project Structure

```
barangay_portal/
├── accounts/           # User authentication and management
├── complaints/         # Complaint management system
├── feedback/          # Feedback and rating system
├── dashboard/         # Role-based dashboards
├── templates/         # HTML templates
├── static/           # CSS, JS, images
├── media/            # User uploaded files
├── barangay_portal/  # Main Django settings
├── manage.py         # Django management script
### User (Custom)

- Extended Django User with roles and approval system
- Roles: resident, secretary, chairman
- Additional fields: phone_number, address, is_approved

### Complaint

- Title, description, category, location
- Status tracking and priority levels
- File attachments and comments
- Email notification system

### Feedback

- Star rating system with categories
- Anonymous feedback option
- Admin response capability
### For Residents

1. Register account (requires chairman approval)
2. Login and access resident dashboard
3. Submit complaints with attachments
4. Track complaint status and receive email updates
5. Provide feedback on portal experience

### For Barangay Secretary

1. Login with secretary role account
2. View and manage all complaints
3. Update complaint statuses and priorities
4. Assign complaints to officials
5. Add internal notes and comments
6. Respond to feedback

### For Barangay Chairman

1. Approve new user registrations
2. Access comprehensive dashboard with statistics
3. Generate and view reports
4. System-wide management capabilities
5. Review all complaints and feedback
6. Respond to feedback

### For Barangay Chairman
1. Approve new user registrations
2. Access comprehensive dashboard with statistics
3. Generate and view reports
4. System-wide management capabilities
5. Review all complaints and feedback

## Configuration

### File Upload Settings

- Maximum file size: 10MB per file
- Allowed formats: Images (jpg, png, gif), Videos (mp4, avi, mov), Documents (pdf, doc, docx)
- Files stored in `media/complaint_attachments/` and `media/feedback_attachments/`
EMAIL_HOST = 'your-smtp-server'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

### File Upload Settings
- Maximum file size: 10MB per file
- Allowed formats: Images (jpg, png, gif), Videos (mp4, avi, mov), Documents (pdf, doc, docx)
- Files stored in `media/complaint_attachments/` and `media/feedback_attachments/`

## Development

### Adding New Complaint Categories
```python
python manage.py shell
from complaints.models import ComplaintCategory
ComplaintCategory.objects.create(name="Road Issues", description="Problems with roads and pathways")
```

### Running Tests
```bash
python manage.py test
```

### Collecting Static Files (Production)
```bash
python manage.py collectstatic
```

## Security Features

- CSRF protection enabled
- User input validation and sanitization
- File type restrictions for uploads
- Role-based access control
- SQL injection protection via Django ORM
- XSS protection via template escaping

## Responsive Design

- Mobile-first responsive design with Bootstrap 5
- Optimized for desktop, tablet, and mobile devices
- Accessible UI with ARIA labels and semantic HTML
- Print-friendly styles for reports

## License

This project is developed for barangay community use and management.