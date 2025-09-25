from django import forms
from django.core.exceptions import ValidationError
from .models import Complaint, ComplaintAttachment, ComplaintComment, ComplaintCategory

class ComplaintForm(forms.ModelForm):
    attachments = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,video/*,.pdf,.doc,.docx'
        }),
        help_text="Upload an image, video, or document (Max 10MB per file)"
    )
    
    is_anonymous = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'anonymousCheck'
        }),
        label="Submit anonymously",
        help_text="Your identity will not be revealed to anyone"
    )
    
    anonymous_contact = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com (optional)',
            'id': 'anonymousContact'
        }),
        label="Contact email (optional)",
        help_text="Provide an email for status updates (optional for anonymous complaints)"
    )
    
    class Meta:
        model = Complaint
        fields = ['category', 'title', 'description', 'location', 'priority', 'is_anonymous', 'anonymous_contact']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief title of your complaint'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 5,
                'placeholder': 'Please provide detailed description of your complaint'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Specific location (street, landmark, etc.)'
            }),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ComplaintCategory.objects.filter(is_active=True)
        self.fields['category'].empty_label = "Select a category"
    
    def clean_attachments(self):
        files = self.files.getlist('attachments')
        if files:
            for file in files:
                if file.size > 10 * 1024 * 1024:  # 10MB limit
                    raise ValidationError(f"File {file.name} is too large. Maximum size is 10MB.")
                
                # Validate file type
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.avi', '.mov', '.pdf', '.doc', '.docx']
                if not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
                    raise ValidationError(f"File {file.name} has an unsupported format.")
        
        return files

class ComplaintUpdateForm(forms.ModelForm):
    resolution_proof = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,.pdf,.doc,.docx'
        }),
        help_text="Upload proof of resolution (required when marking as resolved)"
    )
    
    class Meta:
        model = Complaint
        fields = ['status', 'priority', 'assigned_to', 'resolution_proof', 'resolution_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'resolution_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe how the complaint was resolved...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        from accounts.models import User
        # Show all barangay officials who can be assigned complaints
        self.fields['assigned_to'].queryset = User.objects.filter(
            is_approved=True
        ).filter(
            role__in=[
                'secretary', 'chairman', 'tanod_head', 'kagawad_peace', 'kagawad_infra',
                'kagawad_health', 'kagawad_social', 'kagawad_sanitation', 'kagawad_environment',
                'lupon_chair', 'lupon_member', 'bhw', 'sk_chair', 'vaw_officer', 
                'badac_focal', 'bdrrmc_focal', 'animal_control'
            ]
        ).order_by('role', 'first_name', 'last_name')
        self.fields['assigned_to'].empty_label = "Unassigned"
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        resolution_proof = cleaned_data.get('resolution_proof')
        resolution_notes = cleaned_data.get('resolution_notes')
        
        # If status is being changed to resolved, require proof and notes
        if status == 'resolved':
            # Check if this is a new resolution (not already resolved)
            if self.instance and self.instance.pk:
                original = Complaint.objects.get(pk=self.instance.pk)
                if original.status != 'resolved':
                    # This is a new resolution, require proof
                    if not resolution_proof and not self.instance.resolution_proof:
                        raise ValidationError({
                            'resolution_proof': 'Resolution proof is required when marking complaint as resolved.'
                        })
                    if not resolution_notes:
                        raise ValidationError({
                            'resolution_notes': 'Resolution notes are required when marking complaint as resolved.'
                        })
        
        return cleaned_data

class ComplaintCommentForm(forms.ModelForm):
    class Meta:
        model = ComplaintComment
        fields = ['comment', 'attachment', 'is_internal']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add a comment...'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,application/pdf,.doc,.docx'
            }),
            'is_internal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only staff can make internal comments
        if user and not user.can_manage_complaints():
            self.fields.pop('is_internal')

class ComplaintSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search complaints, location, description...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=ComplaintCategory.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Complaint.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    priority = forms.ChoiceField(
        choices=[('', 'All Priority')] + Complaint.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="From Date"
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="To Date"
    )
    assigned_to = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Assignees",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('', 'Default (Newest first)'),
            ('created_at', 'Date Created (Oldest first)'),
            ('-created_at', 'Date Created (Newest first)'),
            ('title', 'Title (A-Z)'),
            ('-title', 'Title (Z-A)'),
            ('priority', 'Priority (Low to High)'),
            ('-priority', 'Priority (High to Low)'),
            ('status', 'Status'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show assignee filter for staff
        if user and user.can_manage_complaints():
            from accounts.models import User
            self.fields['assigned_to'].queryset = User.objects.filter(
                is_approved=True
            ).filter(
                role__in=[
                    'secretary', 'chairman', 'tanod_head', 'kagawad_peace', 'kagawad_infra',
                    'kagawad_health', 'kagawad_social', 'kagawad_sanitation', 'kagawad_environment',
                    'lupon_chair', 'lupon_member', 'bhw', 'sk_chair', 'vaw_officer', 
                    'badac_focal', 'bdrrmc_focal', 'animal_control'
                ]
            ).order_by('role', 'first_name', 'last_name')
        else:
            # Remove assignee field for residents
            self.fields.pop('assigned_to')