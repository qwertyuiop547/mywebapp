from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import user_agents

def user_profile_photo_upload_path(instance, filename):
    """Upload path for user profile photos"""
    return f"profile_photos/{instance.id}/{timezone.now().strftime('%Y%m%d_%H%M%S')}_{filename}"

class User(AbstractUser):
    ROLE_CHOICES = [
        ('resident', 'Resident'),
        ('secretary', 'Barangay Secretary'),
        ('chairman', 'Barangay Chairman'),
        ('tanod_head', 'Barangay Tanod Head'),
        ('kagawad_peace', 'Kagawad - Peace & Order'),
        ('kagawad_infra', 'Kagawad - Infrastructure'),
        ('kagawad_health', 'Kagawad - Health'),
        ('kagawad_social', 'Kagawad - Social Services'),
        ('kagawad_sanitation', 'Kagawad - Sanitation'),
        ('kagawad_environment', 'Kagawad - Environment'),
        ('lupon_chair', 'Lupon Tagapamayapa - Chairperson'),
        ('lupon_member', 'Lupon Tagapamayapa - Member'),
        ('bhw', 'Barangay Health Worker'),
        ('sk_chair', 'SK Chairperson'),
        ('vaw_officer', 'VAW Desk Officer'),
        ('badac_focal', 'BADAC Focal Person'),
        ('bdrrmc_focal', 'BDRRMC Focal Person'),
        ('animal_control', 'Animal Control Officer'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='resident')
    position_portfolio = models.CharField(max_length=100, blank=True, null=True, 
                                        help_text="Specific portfolio or assignment details")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Location fields for map pinning
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True, 
                                 help_text="Latitude coordinate for residence location")
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True, 
                                  help_text="Longitude coordinate for residence location")
    
    profile_photo = models.ImageField(upload_to=user_profile_photo_upload_path, blank=True, null=True, 
                                    help_text="Upload your photo (required for registration)")
    is_approved = models.BooleanField(default=False, help_text="Chairman must approve new users")
    date_approved = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_resident(self):
        return self.role == 'resident'
    
    def is_secretary(self):
        return self.role == 'secretary'
    
    def is_chairman(self):
        return self.role == 'chairman'
    
    def can_approve_users(self):
        return self.role in ['chairman', 'secretary']
    
    def can_manage_complaints(self):
        return self.is_secretary() or self.is_chairman()
    
    def is_kagawad(self):
        return self.role.startswith('kagawad_')
    
    def is_lupon_member(self):
        return self.role in ['lupon_chair', 'lupon_member']
    
    def is_barangay_official(self):
        """Check if user is any barangay official (not just resident)"""
        return self.role != 'resident'
    
    def can_be_assigned_complaints(self):
        """Who can receive complaint assignments"""
        assignable_roles = [
            'secretary', 'chairman', 'tanod_head', 'kagawad_peace', 'kagawad_infra',
            'kagawad_health', 'kagawad_social', 'kagawad_sanitation', 'kagawad_environment',
            'lupon_chair', 'lupon_member', 'bhw', 'sk_chair', 'vaw_officer', 
            'badac_focal', 'bdrrmc_focal', 'animal_control'
        ]
        return self.role in assignable_roles
    
    def get_assignment_priority(self):
        """For auto-assignment priority (lower number = higher priority)"""
        priority_map = {
            'chairman': 1,
            'secretary': 2,
            'kagawad_peace': 3, 'kagawad_infra': 3, 'kagawad_health': 3,
            'kagawad_social': 3, 'kagawad_sanitation': 3, 'kagawad_environment': 3,
            'lupon_chair': 4,
            'tanod_head': 5,
            'vaw_officer': 5, 'badac_focal': 5, 'bdrrmc_focal': 5,
            'bhw': 6, 'sk_chair': 6, 'animal_control': 6,
            'lupon_member': 7,
        }
        return priority_map.get(self.role, 99)
    
    def can_view_all_login_history(self):
        """Who can view all users' login history - Secretary and Chairman for security monitoring"""
        return self.role in ['secretary', 'chairman']
    
    def can_view_user_login_history(self, target_user):
        """Who can view specific user's login history"""
        # Can always view own history
        if self == target_user:
            return True
        # Secretary and Chairman can view all
        if self.can_view_all_login_history():
            return True
        return False


def user_verification_upload_path(instance, filename):
    return f"user_verifications/{instance.user_id}/{timezone.now().strftime('%Y%m%d_%H%M%S')}_{filename}"


class UserVerificationDocument(models.Model):
    """Verification documents for residency proof during registration/approval."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_documents')
    file = models.FileField(upload_to=user_verification_upload_path)
    document_type = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., Barangay ID, Utility Bill")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Doc #{self.id} for {self.user.username}"


class BarangayArea(models.Model):
    """Valid streets and areas within Barangay Burgos for address validation"""
    name = models.CharField(max_length=100, unique=True, help_text="Street/Area name")
    zone = models.CharField(max_length=20, blank=True, null=True, help_text="Zone designation (e.g., Zone 1, Zone 2)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Barangay Area"
        verbose_name_plural = "Barangay Areas"
        ordering = ['zone', 'name']
    
    def __str__(self):
        if self.zone:
            return f"{self.name} ({self.zone})"
        return self.name


class ResidencyValidation(models.Model):
    """Track residency validation results for users"""
    VALIDATION_STATUS = [
        ('pending', 'Pending Validation'),
        ('valid_location', 'Valid Location'),
        ('invalid_location', 'Invalid Location'),
        ('valid_address', 'Valid Address'),
        ('invalid_address', 'Invalid Address'),
        ('auto_approved', 'Auto Approved'),
        ('requires_manual', 'Requires Manual Review'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='residency_validation')
    location_status = models.CharField(max_length=20, choices=VALIDATION_STATUS, default='pending')
    address_status = models.CharField(max_length=20, choices=VALIDATION_STATUS, default='pending')
    validation_notes = models.TextField(blank=True, null=True)
    last_validated = models.DateTimeField(auto_now=True)
    auto_validation_score = models.IntegerField(default=0, help_text="Automated validation score (0-100)")
    
    def __str__(self):
        return f"Validation for {self.user.username}: {self.get_overall_status()}"
    
    def get_overall_status(self):
        """Get overall validation status"""
        if self.location_status == 'valid_location' and self.address_status == 'valid_address':
            return 'auto_approved'
        elif 'invalid' in [self.location_status, self.address_status]:
            return 'requires_manual'
        else:
            return 'pending'
    
    def calculate_validation_score(self):
        """Calculate automated validation score"""
        score = 0
        
        # Location validation (50 points)
        if self.location_status == 'valid_location':
            score += 50
        elif self.location_status == 'invalid_location':
            score -= 20
            
        # Address validation (50 points)
        if self.address_status == 'valid_address':
            score += 50
        elif self.address_status == 'invalid_address':
            score -= 20
            
        # Ensure score is between 0-100
        self.auto_validation_score = max(0, min(100, score))
        return self.auto_validation_score


class UserLoginHistory(models.Model):
    """Track user login sessions and devices for security monitoring"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    session_key = models.CharField(max_length=40, blank=True, null=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    # Parsed device information
    device_type = models.CharField(max_length=20, blank=True)  # desktop, mobile, tablet
    browser = models.CharField(max_length=50, blank=True)
    browser_version = models.CharField(max_length=20, blank=True)
    os = models.CharField(max_length=50, blank=True)
    os_version = models.CharField(max_length=20, blank=True)
    
    # Login details
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Security flags
    is_suspicious = models.BooleanField(default=False, help_text="Marked as suspicious login")
    location_estimate = models.CharField(max_length=100, blank=True, help_text="Estimated location from IP")
    
    class Meta:
        ordering = ['-login_time']
        verbose_name = "Login History"
        verbose_name_plural = "Login Histories"
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time.strftime('%Y-%m-%d %H:%M')} from {self.ip_address}"
    
    def parse_user_agent(self):
        """Parse user agent string to extract device information"""
        if self.user_agent:
            ua = user_agents.parse(self.user_agent)
            
            # Device type
            if ua.is_mobile:
                self.device_type = 'mobile'
            elif ua.is_tablet:
                self.device_type = 'tablet'
            else:
                self.device_type = 'desktop'
            
            # Browser info
            self.browser = ua.browser.family
            self.browser_version = ua.browser.version_string
            
            # OS info
            self.os = ua.os.family
            self.os_version = ua.os.version_string
    
    def get_device_display(self):
        """Get human-readable device description"""
        parts = []
        if self.device_type:
            parts.append(self.device_type.title())
        if self.browser:
            browser_info = self.browser
            if self.browser_version:
                browser_info += f" {self.browser_version}"
            parts.append(browser_info)
        if self.os:
            os_info = self.os
            if self.os_version:
                os_info += f" {self.os_version}"
            parts.append(os_info)
        
        return " - ".join(parts) if parts else "Unknown Device"
    
    def get_session_duration(self):
        """Get session duration if logged out"""
        if self.logout_time:
            duration = self.logout_time - self.login_time
            return duration
        return None
    
    def is_current_session(self):
        """Check if this is the current active session"""
        return self.is_active and not self.logout_time

