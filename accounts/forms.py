from django import forms
import os
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import User, UserVerificationDocument


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=False)  # Make email optional
    first_name = forms.CharField(max_length=150, required=False)  # Optional, increased max_length
    last_name = forms.CharField(max_length=150, required=False)   # Optional, increased max_length
    phone_number = forms.CharField(max_length=50, required=False)  # Increased max_length
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    profile_photo = forms.ImageField(
        required=True,  # Make required for registration
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'  # Accept only image files
        }),
        help_text='Upload your photo (required). Only image files accepted, up to 10MB.'
    )
    
    verification_documents = forms.FileField(
        required=True,  # Make required for residency verification
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '*/*'  # Accept any file type
        }),
        help_text='Upload a verification document (required). Any file type accepted, up to 50MB.'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'address', 'profile_photo', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Add specific IDs for password fields for toggle functionality
        self.fields['password1'].widget.attrs.update({'id': 'register-password1'})
        self.fields['password2'].widget.attrs.update({'id': 'register-password2'})

    def clean_verification_documents(self):
        file = self.cleaned_data.get('verification_documents')
        
        # Require file upload for residency verification
        if not file:
            raise forms.ValidationError('Please upload a verification document to prove your residency.')
        
        # Validate file size
        max_size = 50 * 1024 * 1024  # 50 MB
        if file.size > max_size:
            raise forms.ValidationError('File is too large. Maximum size is 50MB.')
        
        return file

    def clean_profile_photo(self):
        photo = self.cleaned_data.get('profile_photo')
        
        # Require photo upload for registration
        if not photo:
            raise forms.ValidationError('Please upload your photo. This is required for registration.')
        
        # Validate file size (10MB max)
        max_size = 10 * 1024 * 1024  # 10 MB
        if photo.size > max_size:
            raise forms.ValidationError('Photo file is too large. Maximum size is 10MB.')
        
        # Validate file type
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        file_extension = os.path.splitext(photo.name)[1].lower()
        if file_extension not in valid_extensions:
            raise forms.ValidationError('Please upload a valid image file (JPG, PNG, GIF, BMP, or WebP).')
        
        return photo

    # Override username validation to remove uniqueness check
    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        if not username:
            raise forms.ValidationError('Username is required.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        # Just return the email without uniqueness check
        return email
    
    def _post_clean(self):
        # Override to prevent username uniqueness validation from UserCreationForm
        super(UserCreationForm, self)._post_clean()
        # Don't call UserCreationForm's _post_clean which does uniqueness check

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information"""
    
    profile_photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'profile-photo-input'
        }),
        help_text='Update your profile photo. Only image files accepted, up to 10MB.'
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'latitude', 'longitude', 'profile_photo')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Complete Address'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Latitude (e.g., 11.2588)',
                'step': '0.00000001'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Longitude (e.g., 125.0078)',
                'step': '0.00000001'
            }),
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise forms.ValidationError('Username cannot be blank.')

        existing = User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk)
        if existing.exists():
            raise forms.ValidationError('This username is already taken. Please choose another one.')

        return username

    def clean_profile_photo(self):
        photo = self.cleaned_data.get('profile_photo')
        
        if photo:
            # Validate file size (10MB max)
            max_size = 10 * 1024 * 1024  # 10 MB
            if photo.size > max_size:
                raise forms.ValidationError('Photo file is too large. Maximum size is 10MB.')
            
            # Validate file type
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            file_extension = os.path.splitext(photo.name)[1].lower()
            if file_extension not in valid_extensions:
                raise forms.ValidationError('Please upload a valid image file (JPG, PNG, GIF, BMP, or WebP).')
            
        return photo

class UserLoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'login-password'
        })
    )
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Invalid username or password")
            if not user.is_approved and not user.is_superuser:
                raise forms.ValidationError("Your account is pending approval by the Barangay Chairman")
        
        return self.cleaned_data