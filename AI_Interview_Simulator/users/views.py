"""
Views for the users app.

Views in Django REST Framework handle incoming HTTP requests,
process them (often using serializers), and return responses.

Think of views as the "traffic controllers" of your API:
- They receive requests (GET, POST, PUT, DELETE, etc.)
- They decide what to do with the data
- They send back appropriate responses (JSON, HTML, errors, etc.)
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .serializers import RegisterSerializer, ProfileSerializer


class RegisterView(APIView):
    """
    API endpoint for user registration.
    
    This view handles POST requests to create new user accounts.
    
    URL: /api/register/
    Method: POST
    Data required: username, email, password
    
    Example POST data:
    {
        "username": "john_doe",
        "email": "john@example.com", 
        "password": "securepassword123"
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Handle POST request to register a new user.
        
        Args:
            request: The HTTP request object containing user data
            
        Returns:
            Response: Success message or validation errors
        """
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            
            return Response(
                {"message": "User registered successfully"}, 
                status=201
            )
        
        return Response(serializer.errors, status=400)


class ProfileView(APIView):
    """
    API endpoint for viewing and updating user profile.
    
    This view handles GET requests to retrieve the current user's
    profile information (id, username, email).
    
    URL: /api/profile/
    Method: GET, PUT, PATCH
    Authentication: Required (JWT token must be provided)
    
    Returns the logged-in user's profile when authenticated.
    Returns 401 Unauthorized if no valid JWT token is provided.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Handle GET request to retrieve user profile.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response: User profile data
        """
        # request.user is guaranteed to be authenticated here
        # because of IsAuthenticated permission
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """
        Handle PUT request to update user profile.
        
        Args:
            request: The HTTP request object containing updated data
            
        Returns:
            Response: Updated user profile data or validation errors
        """
        user = request.user
        serializer = ProfileSerializer(user, data=request.data, partial=False)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        """
        Handle PATCH request to partially update user profile.
        
        Args:
            request: The HTTP request object containing partial data
            
        Returns:
            Response: Updated user profile data or validation errors
        """
        user = request.user
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from django.shortcuts import render

def dashboard_view(request):
    return render(request, 'history_dashboard.html')