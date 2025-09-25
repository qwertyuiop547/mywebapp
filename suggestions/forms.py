from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import Suggestion, SuggestionComment, SuggestionCategory

User = get_user_model()

class SuggestionSubmissionForm(forms.ModelForm):
    """Form for submitting new suggestions"""
    
    class Meta:
        model = Suggestion
        fields = [
            'title', 'description', 'category', 'location', 
            'contact_phone', 'is_anonymous'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief title of your suggestion...',
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your suggestion in detail...',
                'rows': 6
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Specific location (optional)...'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact number (optional)...'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active categories and make it optional
        self.fields['category'].queryset = SuggestionCategory.objects.filter(is_active=True)
        self.fields['category'].required = False
        self.fields['category'].empty_label = "General na lang (walang category)"
        
        # Add help text
        self.fields['title'].help_text = "Ano ang gusto mo i-suggest?"
        self.fields['description'].help_text = "Explain mo lang ng maayos ang inyong suggestion"
        self.fields['category'].help_text = "Optional: Piliin kung may specific na category"
        self.fields['location'].help_text = "Optional: Saang lugar ito (kung applicable)"
        self.fields['contact_phone'].help_text = "Optional: Contact number para sa follow-up"
        self.fields['is_anonymous'].help_text = "I-submit nang anonymous"

class SuggestionCommentForm(forms.ModelForm):
    """Form for adding comments to suggestions"""
    
    class Meta:
        model = SuggestionComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Add your comment...',
                'rows': 3
            })
        }

class SuggestionManagementForm(forms.ModelForm):
    """Form for barangay officials to manage suggestions"""
    
    class Meta:
        model = Suggestion
        fields = [
            'status', 'priority', 'admin_notes', 'public_response',
            'estimated_budget', 'implementation_date', 'is_featured'
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'admin_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Internal notes (not visible to public)...',
                'rows': 4
            }),
            'public_response': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Official response to the suggestion...',
                'rows': 4
            }),
            'estimated_budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estimated budget (PHP)'
            }),
            'implementation_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help text
        self.fields['admin_notes'].help_text = "Internal notes for barangay officials only"
        self.fields['public_response'].help_text = "Official response that will be visible to residents"
        self.fields['estimated_budget'].help_text = "Estimated cost in Philippine Peso"
        self.fields['implementation_date'].help_text = "Target date for implementation"
        self.fields['is_featured'].help_text = "Feature this suggestion on the main page"

class SuggestionFilterForm(forms.Form):
    """Form for filtering suggestions"""
    
    STATUS_CHOICES = [('', _('All Statuses'))] + list(Suggestion.STATUS_CHOICES)
    PRIORITY_CHOICES = [('', _('All Priorities'))] + list(Suggestion.PRIORITY_CHOICES)
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=SuggestionCategory.objects.filter(is_active=True),
        required=False,
        empty_label=_("All Categories"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('-submitted_at', _('Newest First')),
            ('submitted_at', _('Oldest First')),
            ('-likes', _('Most Liked')),
            ('-views', _('Most Viewed')),
            ('title', _('Title A-Z')),
        ],
        required=False,
        initial='-submitted_at',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['search'].label = _('Search')
        self.fields['search'].widget.attrs['placeholder'] = _('Search feedback...')
        self.fields['status'].label = _('Status')
        self.fields['priority'].label = _('Priority')
        self.fields['category'].label = _('Category')
        self.fields['category'].empty_label = _('All Categories')
        self.fields['sort_by'].label = _('Sort By')
