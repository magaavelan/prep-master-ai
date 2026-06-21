"""
URL routing for the users app.

URL patterns map web addresses (URLs) to view functions/classes.
When a user visits a URL, Django looks through this list to find
a matching pattern and calls the associated view.

Think of URL patterns like a map:
- URL path -> View that handles it
- Example: /api/register/ -> RegisterView

This file defines all API endpoints related to user authentication
and profile management.
"""

from django.urls import path

from .views import RegisterView, ProfileView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path(
        'register/',  # The URL path (comes after /api/)
        RegisterView.as_view(),  # The view that handles this URL
        name='register'  # A name to reference this URL in code
    ),
    
    path(
        'login/',  # The URL path
        TokenObtainPairView.as_view(),  # Built-in DRF SimpleJWT view
        name='login'  # Name for reverse URL lookups
    ),
    
    path(
        'refresh/',  # The URL path
        TokenRefreshView.as_view(),  # Built-in DRF SimpleJWT view
        name='refresh'  # Name for reverse URL lookups
    ),
    
    path(
        'profile/',  # The URL path
        ProfileView.as_view(),  # Our custom ProfileView
        name='profile'  # Name for reverse URL lookups
    ),
]

app_name = 'users'