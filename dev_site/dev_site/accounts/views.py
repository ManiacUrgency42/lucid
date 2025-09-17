from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from itsdangerous import URLSafeTimedSerializer
from .models import CollegeUser
from .forms import LoginForm, RegistrationForm, EmailVerificationForm
import re

# Initialize token generator using app's secret key.
# encodes email address into verification token, which can be later used to verify registered email addresses
serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

# checks if email address ends with .edu, .ac.uk, or a regional .edu.xx using regex
def is_college_email(email):
    return re.match(r"[^@]+@[^@]+\.(edu|ac\.uk|edu\.[a-z]+)$", email)

def landing_page(request):
    """Landing page with login form"""
    if request.user.is_authenticated:
        return redirect('video_chat_home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('video_chat_home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/landing.html', {'form': form})

def register(request):
    """User registration page"""
    if request.user.is_authenticated:
        return redirect('video_chat_home')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Save the user and college user
                user = form.save(commit=True)  # This will create both User and CollegeUser
                
                # Generate verification token and send email
                token = serializer.dumps(user.email, salt="email-verify")
                verification_url = request.build_absolute_uri(reverse('verify_email', args=[token]))
                
                # Send verification email
                send_mail(
                    subject="Verify your College Email - College Chat",
                    message=f"""
                Welcome to College Chat!
                
                Please click the following link to verify your email address:
                {verification_url}
                
                This link will expire in 1 hour.
                
                If you didn't create an account, please ignore this email.
                """,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                )
                
                messages.success(request, 'Registration successful! Please check your email to verify your account.')
                return redirect('registration_complete')
                
            except Exception as e:
                # If something goes wrong, clean up and show error
                if user and user.id:
                    user.delete()
                messages.error(request, f'Registration failed: {str(e)}')
                return render(request, 'accounts/register.html', {'form': form})
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def registration_complete(request):
    """Page shown after successful registration"""
    return render(request, 'accounts/registration_complete.html')

def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('landing_page')

# the view that handles email verification requests
def request_verification(request):
    if request.method == "POST":
        # retrieve submitted email address from the form
        email = request.POST.get("email")

        if not is_college_email(email):
            return HttpResponse("Please use a valid college email (.edu).", status=400)

        # Save or get the user
        # if email already exists in DB, return that record. else, create new CollegeUser record with this email. created=True if new user was created
        user, created = CollegeUser.objects.get_or_create(email=email)

        # Generate token
        token = serializer.dumps(email, salt="email-verify")
        verification_url = request.build_absolute_uri(reverse('verify_email', args=[token]))

        # Send the email
        send_mail(
            subject="Verify your College Email",
            message=f"Click this link to verify: {verification_url}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )

        return HttpResponse("Verification email sent!")
    return render(request, "accounts/request_verification.html")

# once user clicks on verification link included in email
def verify_email(request, token):
    try:
        # decode the token to return the actual email address
        # max_age = 3600 means link is valid for 1 hour
        email = serializer.loads(token, salt="email-verify", max_age=3600)

        # Looks up the CollegeUser object in the database that matches the decoded email.
        # If the email doesn't exist (e.g., deleted), this line will raise an exception and jump to except.
        college_user = CollegeUser.objects.get(email=email)
        
        college_user.is_verified = True
        
        # If there's a linked User, activate it
        if college_user.user:
            college_user.user.is_active = True
            college_user.user.save()
        
        # save updated user record to database, persisting the verification status
        college_user.save()
        
        messages.success(request, f'Email {email} has been verified! You can now log in.')
        return redirect('landing_page')
    except Exception:
        messages.error(request, "Invalid or expired verification link.")
        return redirect('landing_page')

@login_required
def profile(request):
    """User profile page"""
    try:
        college_user = CollegeUser.objects.get(user=request.user)
    except CollegeUser.DoesNotExist:
        college_user = None
    
    return render(request, 'accounts/profile.html', {'college_user': college_user})
