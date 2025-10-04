from django import forms
from .models import Suggestion


class SuggestionForm(forms.ModelForm):
    """
    Form for submitting a new suggestion
    """
    
    class Meta:
        model = Suggestion
        fields = ['title', 'description', 'location']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Halimbawa: Pagtatayo ng bagong playground'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Ilarawan ang iyong mungkahi...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Purok/Sitio (optional)'
            }),
        }
        labels = {
            'title': 'Pamagat ng Mungkahi',
            'description': 'Detalyadong Paglalarawan',
            'location': 'Lokasyon (Optional)',
        }


class SuggestionReviewForm(forms.ModelForm):
    """
    Form for barangay officials to review suggestions
    """
    
    class Meta:
        model = Suggestion
        fields = ['status', 'admin_response']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'admin_response': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tugon o komento ng barangay...'
            }),
        }
        labels = {
            'status': 'Status',
            'admin_response': 'Tugon ng Barangay',
        }


class SuggestionFilterForm(forms.Form):
    """
    Form for filtering suggestions
    """
    
    STATUS_CHOICES = [('', 'Lahat')] + list(Suggestion.STATUS_CHOICES)
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Maghanap...'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

