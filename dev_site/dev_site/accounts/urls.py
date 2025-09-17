from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path("", views.landing_page, name="landing_page"),
    path("register/", views.register, name="register"),
    path("registration-complete/", views.registration_complete, name="registration_complete"),
    path("logout/", views.user_logout, name="logout"),
    path("profile/", views.profile, name="profile"),
    
    # Email verification URLs (existing)
    path("request/", views.request_verification, name="request_verification"),
    path("verify/<token>/", views.verify_email, name="verify_email"),
]
