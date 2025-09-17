from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import CollegeUser
import re

class LoginForm(AuthenticationForm):
    """Form for user login"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Allow login with either username or email
        if '@' in username:
            try:
                college_user = CollegeUser.objects.get(email=username)
                return college_user.user.username if college_user.user else username
            except CollegeUser.DoesNotExist:
                raise forms.ValidationError("No account found with this email address.")
        return username

class RegistrationForm(UserCreationForm):
    """Form for user registration with college email validation"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@university.edu'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        error_messages={'required': 'You must accept the terms and conditions.'}
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Check if it's a valid college email
        if not self.is_college_email(email):
            raise forms.ValidationError(
                "Please use a valid college/university email address (.edu, .ac.uk, etc.)"
            )
        
        # Check if email already exists
        if CollegeUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account with this email address already exists."
            )
        
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This username is already taken. Please choose a different one."
            )
        
        return username
    
    def is_college_email(self, email):
        """Check if email is from a college/university domain"""
        return re.match(r"[^@]+@[^@]+\.(edu|ac\.uk|edu\.[a-z]+)$", email)
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = False  # User must verify email first
        
        if commit:
            user.save()
            
            # Create CollegeUser instance
            college_user = CollegeUser.objects.create(
                user=user,
                email=self.cleaned_data['email'],
                username=self.cleaned_data['username'],
                is_verified=False  # Will be verified via email
            )
        
        return user

class EmailVerificationForm(forms.Form):
    """Form for requesting email verification"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@university.edu'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Check if it's a valid college email
        if not re.match(r"[^@]+@[^@]+\.(edu|ac\.uk|edu\.[a-z]+)$", email):
            raise forms.ValidationError(
                "Please use a valid college/university email address."
            )
        
        return email 