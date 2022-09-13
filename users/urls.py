from django.urls import path
from . import views

urlpatterns = [
    # Register
    path('register', views.UserRegister.as_view(), name='register'),

    # Authentication
    path('authenticate', views.UserAuthenticate.as_view(), name='authenticate'),
]
