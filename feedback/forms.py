from django import forms
from .models import Feedback, FeedbackAttachment

class FeedbackForm(forms.ModelForm):
    attachment = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,.pdf,.doc,.docx,.txt'
        }),
        help_text="Optional: Upload screenshot or document (Max 5MB)"
    )
    
    class Meta:
        model = Feedback
        fields = ['feedback_type', 'rating', 'title', 'comment', 'is_anonymous']
        widgets = {
            'feedback_type': forms.Select(attrs={'class': 'form-select'}),
            'rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-select'}
            ),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief summary of your feedback'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Please provide detailed feedback...'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_attachment(self):
        file = self.cleaned_data.get('attachment')
        if file:
            if file.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("File size must be under 5MB.")
            
            # Check file type
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt']
            if not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError("File type not supported.")
        
        return file

class FeedbackResponseForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['admin_response']
        widgets = {
            'admin_response': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Response to this feedback...'
            }),
        }

class FeedbackFilterForm(forms.Form):
    feedback_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Feedback.FEEDBACK_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    rating = forms.ChoiceField(
        choices=[('', 'All Ratings')] + [(i, f'{i} Stars') for i in range(1, 6)],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    reviewed = forms.ChoiceField(
        choices=[
            ('', 'All Feedback'),
            ('yes', 'Reviewed'),
            ('no', 'Not Reviewed'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search feedback...'
        })
    )