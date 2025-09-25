from django import forms
from django.core.exceptions import ValidationError
from .models import GalleryPhoto, GalleryCategory, GalleryComment


class PhotoUploadForm(forms.ModelForm):
    """Form for uploading photos to the gallery"""
    
    class Meta:
        model = GalleryPhoto
        fields = [
            'title', 'description', 'image', 'date_taken', 'photographer'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a descriptive title for your photo'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe what this photo shows...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'date_taken': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'photographer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Photographer name (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Required fields
        self.fields['title'].required = True
        self.fields['image'].required = True
        
        # Optional fields
        self.fields['description'].required = False
        self.fields['date_taken'].required = False
        self.fields['photographer'].required = False
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (10MB limit)
            if image.size > 10 * 1024 * 1024:
                raise ValidationError('Image file size cannot exceed 10MB.')
            
            # Check file type
            if not image.content_type.startswith('image/'):
                raise ValidationError('Please upload a valid image file.')
        
        return image
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title) < 5:
            raise ValidationError('Title must be at least 5 characters long.')
        return title


class PhotoFilterForm(forms.Form):
    """Form for filtering photos in the gallery"""
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search photos...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=GalleryCategory.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    featured_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class CommentForm(forms.ModelForm):
    """Form for adding comments to photos"""
    
    class Meta:
        model = GalleryComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment...'
            })
        }
    
    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if comment and len(comment.strip()) < 3:
            raise ValidationError('Comment must be at least 3 characters long.')
        return comment.strip()


class PhotoManagementForm(forms.ModelForm):
    """Form for managing photos by officials"""
    
    class Meta:
        model = GalleryPhoto
        fields = [
            'title', 'description', 'category', 'status', 'is_featured', 
            'is_public', 'location', 'event_name', 'photographer'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'event_name': forms.TextInput(attrs={'class': 'form-control'}),
            'photographer': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = GalleryCategory.objects.filter(is_active=True)
