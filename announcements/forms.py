from django import forms
from django.utils import timezone
from .models import Announcement

class AnnouncementForm(forms.ModelForm):
    """Form for creating and editing announcements"""
    
    class Meta:
        model = Announcement
        fields = [
            'title', 'image', 'content', 'is_published', 'is_pinned'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maglagay ng titulo...',
                'maxlength': 200
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Optional: Dagdag na details...',
                'rows': 3
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_pinned': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text in Filipino - simplified
        self.fields['title'].help_text = "Maglagay ng titulo ng announcement"
        self.fields['image'].help_text = "Maglagay ng larawan (Required para makita ng mga residents)"
        self.fields['content'].help_text = "Optional: Dagdag na explanation kung kailangan"
        self.fields['is_published'].help_text = "I-publish na ba ito ngayon?"
        self.fields['is_pinned'].help_text = "I-pin sa taas para mas makita"
        
        # Make image required in practice
        self.fields['image'].required = True

class AnnouncementFilterForm(forms.Form):
    """Form for filtering announcements"""
    
    CATEGORY_CHOICES = [('', 'All Categories')] + list(Announcement.CATEGORY_CHOICES)
    PRIORITY_CHOICES = [('', 'All Priorities')] + list(Announcement.PRIORITY_CHOICES)
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Hanapin ang announcement...'
        })
    )
    
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
