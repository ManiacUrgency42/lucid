from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

# Create your models here.

class CollegeUser(models.Model):
    # Link to Django's built-in User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # College email verification
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    
    # Additional user fields
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    # College-specific fields
    college_name = models.CharField(max_length=200, null=True, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        # Auto-generate username if not provided
        if not self.username and self.email:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)
    
    @property
    def is_authenticated(self):
        return self.is_verified and self.is_active
    
    class Meta:
        verbose_name = "College User"
        verbose_name_plural = "College Users"