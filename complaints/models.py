from django.db import models
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

class CategoryAssignmentRule(models.Model):
    """Maps complaint categories to default assignees and escalation rules"""
    ASSIGNEE_CHOICES = [
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
        ('secretary', 'Barangay Secretary'),
        ('chairman', 'Barangay Chairman'),
    ]
    
    category = models.ForeignKey('ComplaintCategory', on_delete=models.CASCADE, related_name='assignment_rules')
    default_assignee_role = models.CharField(max_length=20, choices=ASSIGNEE_CHOICES)
    backup_assignee_role = models.CharField(max_length=20, choices=ASSIGNEE_CHOICES, blank=True, null=True)
    is_sensitive = models.BooleanField(default=False, help_text="Requires confidential handling")
    requires_referral = models.BooleanField(default=False, help_text="Usually needs external referral")
    escalation_notes = models.TextField(blank=True, help_text="Instructions for escalation")
    
    def __str__(self):
        return f"{self.category.name} → {self.get_default_assignee_role_display()}"

class ComplaintCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Complaint Categories"
    
    def __str__(self):
        return self.name

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('high', 'High'),  
        ('emergency', 'Emergency'),
    ]
    
    complainant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints', null=True, blank=True)
    is_anonymous = models.BooleanField(default=False, help_text="Anonymous complaint - no complainant identity revealed")
    anonymous_contact = models.CharField(max_length=255, blank=True, null=True, help_text="Optional contact info for anonymous complaints")
    category = models.ForeignKey(ComplaintCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255, blank=True, help_text="Specific location of the complaint")
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Secretary approval system
    is_approved = models.BooleanField(null=True, blank=True, default=None, help_text="Approved by secretary for chairman review (None=pending, True=approved, False=rejected)")
    approved_at = models.DateTimeField(null=True, blank=True, help_text="When complaint was approved by secretary")
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_complaints',
        help_text="Secretary who approved this complaint"
    )
    rejection_reason = models.TextField(
        blank=True,
        help_text="Reason for rejection if complaint is not approved"
    )
    
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='assigned_complaints')
    assignment_notes = models.TextField(blank=True, help_text="Assignment or referral notes")
    
    # SLA tracking
    assignment_due = models.DateTimeField(null=True, blank=True, help_text="When assignment should be completed")
    response_due = models.DateTimeField(null=True, blank=True, help_text="When response is due")
    accepted_at = models.DateTimeField(null=True, blank=True, help_text="When complaint was accepted/assigned")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Resolution proof fields
    resolution_proof = models.FileField(
        upload_to='resolution_proofs/%Y/%m/',
        null=True, blank=True,
        help_text="Photo or document proof of complaint resolution (required for resolved status)"
    )
    resolution_notes = models.TextField(
        blank=True,
        help_text="Detailed notes about how the complaint was resolved"
    )
    resolved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='resolved_complaints',
        help_text="Chairman or official who resolved the complaint"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['complainant']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        from django.utils import timezone
        from datetime import timedelta
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info(f"Complaint.save() called for complaint {self.pk or 'new'}: {self.title}")
        
        is_new = not self.pk
        
        # Check if status changed
        if self.pk:
            logger.info(f"Checking status change for existing complaint {self.pk}")
            try:
                original = Complaint.objects.get(pk=self.pk)
                if original.status != self.status:
                    logger.info(f"Status changed from {original.status} to {self.status} for complaint {self.pk}")
                    self.send_status_update_email()
                    # Set timestamps for status changes
                    if self.status == 'in_progress' and not self.accepted_at:
                        self.accepted_at = timezone.now()
                    elif self.status == 'resolved' and not self.resolved_at:
                        self.resolved_at = timezone.now()
                        # Set resolved_by if not already set
                        if not self.resolved_by:
                            # Get the current user from thread local storage if available
                            from django.contrib.auth import get_user_model
                            User = get_user_model()
                            # This will be set by the view when updating
                            pass
                else:
                    logger.info(f"No status change for complaint {self.pk}")
            except Exception as e:
                logger.error(f"Error checking status change for complaint {self.pk}: {e}")
        
        # Auto-assign on creation
        if is_new and not self.assigned_to:
            logger.info(f"Auto-assigning new complaint")
            self.auto_assign()
        
        # Set SLA dates based on priority
        if is_new or not self.response_due:
            self.set_sla_dates()
        
        logger.info(f"About to call super().save() for complaint {self.pk or 'new'}")
        super().save(*args, **kwargs)
        logger.info(f"Successfully saved complaint {self.pk}: {self.title}")
    
    def auto_assign(self):
        """Automatically assign complaint based on category rules"""
        try:
            rule = self.category.assignment_rules.first()
            if rule:
                # Find available user with the default assignee role
                assignee = User.objects.filter(
                    role=rule.default_assignee_role,
                    is_approved=True,
                    is_active=True
                ).order_by('?').first()  # Random selection if multiple
                
                if not assignee and rule.backup_assignee_role:
                    # Try backup role
                    assignee = User.objects.filter(
                        role=rule.backup_assignee_role,
                        is_approved=True,
                        is_active=True
                    ).order_by('?').first()
                
                if not assignee:
                    # Fallback to Secretary
                    assignee = User.objects.filter(
                        role='secretary',
                        is_approved=True,
                        is_active=True
                    ).first()
                
                self.assigned_to = assignee
                if rule.requires_referral:
                    self.assignment_notes = "May require external referral. " + rule.escalation_notes
        except Exception as e:
            # Fallback assignment to Secretary
            secretary = User.objects.filter(role='secretary', is_approved=True, is_active=True).first()
            self.assigned_to = secretary
            self.assignment_notes = f"Auto-assignment failed: {e}"
    
    def set_sla_dates(self):
        """Set SLA dates based on priority"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        
        if self.priority == 'emergency':
            self.assignment_due = now + timedelta(hours=1)
            self.response_due = now + timedelta(hours=4)
        elif self.priority == 'high':
            self.assignment_due = now + timedelta(hours=4)
            self.response_due = now + timedelta(days=2)
        else:  # normal
            self.assignment_due = now + timedelta(days=1)
            self.response_due = now + timedelta(days=5)
    
    def is_overdue(self):
        """Check if complaint is past its SLA"""
        from django.utils import timezone
        return self.response_due and timezone.now() > self.response_due
    
    def days_since_created(self):
        """Get days since complaint was created"""
        from django.utils import timezone
        return (timezone.now() - self.created_at).days
    
    def send_status_update_email(self):
        """Send email notification when complaint status changes"""
        subject = f"Complaint Status Update - {self.title}"
        message = f"""
        # Handle anonymous complaints
        if self.is_anonymous:
            if not self.anonymous_contact or '@' not in self.anonymous_contact:
                return
            recipient_name = 'Anonymous User'
            recipient_email = self.anonymous_contact
        else:
            recipient_name = self.complainant.get_full_name() or self.complainant.username if self.complainant else 'Unknown User'
            recipient_email = self.complainant.email if self.complainant else None
            if not recipient_email:
                return
        
        Dear {recipient_name},
        
        Your complaint "{self.title}" status has been updated to: {self.get_status_display()}
        
        Complaint Details:
        - Category: {self.category.name}
        - Status: {self.get_status_display()}
        - Priority: {self.get_priority_display()}
        
        You can view your complaint details by logging into the Barangay Portal.
        
        Thank you,
        Barangay Office
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient_email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send email: {e}")

class ComplaintAttachment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='complaint_attachments/%Y/%m/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=[
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document')
    ])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.complaint.title} - {self.file_name}"
    
    def save(self, *args, **kwargs):
        if not self.file_name:
            self.file_name = self.file.name
        
        # Determine file type based on extension
        if self.file.name:
            ext = self.file.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                self.file_type = 'image'
            elif ext in ['mp4', 'avi', 'mov', 'wmv', 'flv']:
                self.file_type = 'video'
            else:
                self.file_type = 'document'
        
        super().save(*args, **kwargs)

class ComplaintComment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    attachment = models.FileField(
        upload_to='comment_attachments/%Y/%m/',
        null=True, blank=True,
        help_text="Optional file attachment (proof, documents, etc.)"
    )
    is_internal = models.BooleanField(default=False, help_text="Internal notes not visible to complainant")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.complaint.title}"