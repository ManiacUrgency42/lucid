from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='video_chat_home'),
]
