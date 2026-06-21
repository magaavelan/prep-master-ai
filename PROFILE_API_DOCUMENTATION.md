# AI Interview Simulator - Protected Profile API Documentation

## Complete Implementation Guide

This document provides a comprehensive guide to the Profile API implementation using Django REST Framework and JWT Authentication.

---

## 1. Complete Folder Structure

```
AI_Interview_Simulator/
│
├── manage.py                    # Django management script
├── db.sqlite3                   # SQLite database file
│
├── config/                      # Main Django project configuration
│   ├── __init__.py
│   ├── settings.py              # Main settings file (JWT configured here)
│   ├── urls.py                  # Main URL routing (includes users.urls)
│   ├── asgi.py                  # ASGI configuration
│   └── wsgi.py                  # WSGI configuration
│
├── users/                       # Users app (authentication & profile)
│   ├── __init__.py
│   ├── admin.py                 # Django admin configuration
│   ├── apps.py                  # App configuration
│   ├── models.py                # Database models (uses Django's built-in User)
│   ├── serializers.py           # Data serializers (RegisterSerializer, ProfileSerializer)
│   ├── views.py                 # API views (RegisterView, ProfileView)
│   ├── urls.py                  # URL routing for users app
│   ├── tests.py                 # Unit tests
│   └── migrations/              # Database migrations
│       └── __init__.py
│
├── interviews/                  # Interviews app (for future interview features)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   └── migrations/
│       └── __init__.py
│
└── reports/                     # Reports app (for future reporting features)
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── tests.py
    └── migrations/
        └── __init__.py
```

---

## 2. API Endpoints Overview

| Endpoint | Method | Authentication | Description |
|----------|--------|----------------|-------------|
| `/api/register/` | POST | No | Register a new user |
| `/api/login/` | POST | No | Login and get JWT tokens |
| `/api/refresh/` | POST | No | Refresh access token |
| `/api/profile/` | GET | Yes (JWT) | Get user profile |

---

## 3. Step-by-Step Code Explanation

### 3.1 settings.py - JWT Configuration

```python
# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

**Line-by-line explanation:**

- `REST_FRAMEWORK`: Dictionary containing DRF settings
- `DEFAULT_AUTHENTICATION_CLASSES`: Tells DRF to use JWT for authentication
- `JWTAuthentication`: The class that handles JWT token validation
- `DEFAULT_PERMISSION_CLASSES`: Sets default permissions (AllowAny = no restriction)
- `timedelta`: Python class for representing time durations
- `ACCESS_TOKEN_LIFETIME`: How long the access token is valid (5 minutes)
- `REFRESH_TOKEN_LIFETIME`: How long the refresh token is valid (7 days)
- `ROTATE_REFRESH_TOKENS`: Issue new refresh token each time one is used
- `BLACKLIST_AFTER_ROTATION`: Prevent old refresh tokens from being reused
- `ALGORITHM`: Encryption algorithm (HS256 = HMAC with SHA-256)
- `SIGNING_KEY`: Secret key used to sign tokens (uses Django's SECRET_KEY)
- `AUTH_HEADER_TYPES`: The prefix used in Authorization header ("Bearer <token>")

### 3.2 serializers.py - ProfileSerializer

```python
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id', 'username', 'email']
```

**Line-by-line explanation:**

- `ProfileSerializer`: Class that converts User objects to JSON
- `serializers.ModelSerializer`: DRF's shortcut for creating serializers from models
- `class Meta`: Inner class that defines serializer metadata
- `model = User`: Tells serializer to use Django's User model
- `fields`: List of fields to include in the output
- `read_only_fields`: Fields that cannot be modified through this serializer

### 3.3 views.py - ProfileView

```python
class ProfileView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        if request.user.is_authenticated:
            serializer = ProfileSerializer(request.user)
            return Response(serializer.data)
        else:
            return Response(
                {"error": "Authentication required to view profile"},
                status=401
            )
```

**Line-by-line explanation:**

- `class ProfileView(APIView)`: Creates a class-based view inheriting from APIView
- `permission_classes = [AllowAny]`: Allows anyone to access (change to IsAuthenticated for protection)
- `def get(self, request)`: Method that handles GET requests
- `request.user`: The user making the request (set by JWT authentication)
- `is_authenticated`: Boolean - True if user has valid JWT token
- `ProfileSerializer(request.user)`: Converts user object to JSON
- `serializer.data`: The JSON-ready dictionary
- `Response()`: DRF's response class that returns JSON
- `status=401`: HTTP status code for "Unauthorized"

### 3.4 urls.py - URL Routing

```python
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
```

**Line-by-line explanation:**

- `urlpatterns`: List of URL patterns for this app
- `path()`: Function that defines a URL route
- `'register/'`: The URL path (becomes /api/register/)
- `RegisterView.as_view()`: Converts class-based view to a callable view function
- `name='register'`: Name for reverse URL lookups

---

## 4. Testing the API with Postman

### Step 1: Register a New User

**Request:**
- **Method:** POST
- **URL:** `http://localhost:8000/api/register/`
- **Headers:**
  - `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123"
}
```

**Expected Response (201 Created):**
```json
{
    "message": "User registered successfully"
}
```

---

### Step 2: Login to Get JWT Tokens

**Request:**
- **Method:** POST
- **URL:** `http://localhost:8000/api/login/`
- **Headers:**
  - `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
    "username": "testuser",
    "password": "securepassword123"
}
```

**Expected Response (200 OK):**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIzNDU2Nzg5LCJpYXQiOjE3MjM0NTY0ODksImp0aSI6ImFiY2RlZjEyMzQ1NiIsInVzZXJfaWQiOjF9.abcdefghijklmnopqrstuvwxyz123456789",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyNDA2MTI4OSwiaWF0IjoxNzIzNDU2NDg5LCJqdGkiOiJ4eXphYmNkMTIzNDU2IiwidXNlcl9pZCI6MX0.xyzabcdefghijklmnopqrstuvwxyz123456789"
}
```

**Important:** 
- `access` token: Short-lived (5 minutes), used for API requests
- `refresh` token: Long-lived (7 days), used to get new access tokens

---

### Step 3: Access Profile with JWT Token

**Request:**
- **Method:** GET
- **URL:** `http://localhost:8000/api/profile/`
- **Headers:**
  - `Authorization: Bearer <your_access_token_here>`
  - `Content-Type: application/json`

**Example Header:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Expected Response (200 OK):**
```json
{
    "id": 1,
    "username": "testuser",
    "email": "test@example.com"
}
```

---

### Step 4: Refresh Expired Token

When your access token expires (after 5 minutes), use the refresh token to get a new one:

**Request:**
- **Method:** POST
- **URL:** `http://localhost:8000/api/refresh/`
- **Headers:**
  - `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
    "refresh": "<your_refresh_token_here>"
}
```

**Expected Response (200 OK):**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.new_access_token..."
}
```

---

## 5. Expected Request Headers and Response JSON

### Profile API Request Headers

| Header | Value | Required |
|--------|-------|----------|
| `Authorization` | `Bearer <access_token>` | Yes (for authenticated access) |
| `Content-Type` | `application/json` | Recommended |

### Profile API Response JSON

**Success (200 OK):**
```json
{
    "id": 1,
    "username": "testuser",
    "email": "test@example.com"
}
```

**Unauthorized (401 Unauthorized):**
```json
{
    "error": "Authentication required to view profile"
}
```

---

## 6. Common Debugging Steps

### Issue 1: 401 Unauthorized

**Symptom:** You get a 401 error when trying to access `/api/profile/`

**Possible Causes & Solutions:**

1. **No token provided:**
   - Make sure you include the Authorization header
   - Format: `Authorization: Bearer <token>` (note the space after "Bearer")

2. **Token is expired:**
   - Access tokens expire after 5 minutes (by default)
   - Use the refresh endpoint to get a new access token
   - Or login again to get new tokens

3. **Invalid token format:**
   - Ensure the token is copied completely (no missing characters)
   - Don't include extra spaces or quotes around the token

4. **Wrong header name:**
   - Must be exactly `Authorization` (case-sensitive)
   - Not `authorization` or `AUTHORIZATION`

**Debug Command:**
```bash
# Test with curl to see the exact response
curl -X GET http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -v
```

---

### Issue 2: 404 Not Found

**Symptom:** You get a 404 error when accessing any endpoint

**Possible Causes & Solutions:**

1. **Wrong URL:**
   - Verify the URL is correct: `http://localhost:8000/api/profile/`
   - Don't forget the trailing slash (Django requires it)
   - The `/api/` prefix comes from config/urls.py

2. **Server not running:**
   - Make sure Django server is running: `python manage.py runserver`
   - Check that it's running on port 8000

3. **URL not in urlpatterns:**
   - Check users/urls.py to ensure the path is defined
   - Check config/urls.py to ensure users.urls is included

**Debug Command:**
```bash
# List all available URLs
python manage.py showurls
# Or check URL patterns manually
python manage.py shell
>>> from django.urls import get_resolver
>>> resolver = get_resolver()
>>> for url in resolver.url_patterns:
...     print(url.pattern)
```

---

### Issue 3: Invalid Token

**Symptom:** You get an error about invalid token

**Possible Causes & Solutions:**

1. **Token was tampered with:**
   - JWT tokens have a signature that validates integrity
   - If any character is changed, the token becomes invalid
   - Copy the token exactly as returned from login

2. **Token from wrong server:**
   - Tokens are signed with your server's SECRET_KEY
   - A token from one server won't work on another

3. **Token was corrupted:**
   - Make sure the entire token is included
   - JWT tokens are long strings with dots (.) separating parts
   - Format: `xxxxx.yyyyy.zzzzz`

**How to verify a token:**
```python
# In Django shell
python manage.py shell
>>> from rest_framework_simplejwt.tokens import AccessToken
>>> token = AccessToken("YOUR_TOKEN_HERE")
>>> print(token.payload)  # Shows token contents if valid
```

---

### Issue 4: Expired Token

**Symptom:** You get a 401 error with "Token is expired" message

**Possible Causes & Solutions:**

1. **Access token expired (normal):**
   - Access tokens are short-lived (5 minutes by default)
   - This is intentional for security
   - Use the refresh token to get a new access token

2. **Refresh token expired:**
   - Refresh tokens last 7 days by default
   - If expired, user must login again

3. **Server time is wrong:**
   - JWT validation depends on server time
   - Make sure your server's clock is correct

**Solution - Refresh the token:**
```bash
# Use refresh endpoint
curl -X POST http://localhost:8000/api/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

---

## 7. Testing with Python Requests (Alternative to Postman)

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Step 1: Register
register_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123"
}
response = requests.post(f"{BASE_URL}/register/", json=register_data)
print("Register:", response.json())

# Step 2: Login
login_data = {
    "username": "testuser",
    "password": "securepassword123"
}
response = requests.post(f"{BASE_URL}/login/", json=login_data)
tokens = response.json()
access_token = tokens["access"]
print("Login successful, got access token")

# Step 3: Get Profile
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/profile/", headers=headers)
print("Profile:", response.json())

# Step 4: Refresh Token (when access expires)
refresh_data = {"refresh": tokens["refresh"]}
response = requests.post(f"{BASE_URL}/refresh/", json=refresh_data)
new_tokens = response.json()
print("Token refreshed, new access token received")
```

---

## 8. Production Best Practices

### Security Recommendations

1. **Use HTTPS in production:**
   - Never send JWT tokens over HTTP (they can be intercepted)
   - Configure SSL/TLS certificates

2. **Set appropriate token lifetimes:**
   - Shorter access token lifetime = more secure
   - Consider 15-30 minutes for access tokens
   - Consider 1-7 days for refresh tokens

3. **Store tokens securely on client:**
   - Don't store in localStorage (vulnerable to XSS)
   - Use httpOnly cookies or secure storage

4. **Implement token blacklisting:**
   - Add `'BLACKLIST_AFTER_ROTATION': True` (already configured)
   - Use SimpleJWT's blacklist app

5. **Use environment variables for secrets:**
   ```python
   # In settings.py
   import os
   SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
   ```

### Performance Tips

1. **Enable caching** for frequently accessed data
2. **Use database indexing** on frequently queried fields
3. **Implement rate limiting** to prevent abuse
4. **Monitor API usage** with logging and analytics

---

## 9. Quick Reference - API Endpoints

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI Interview Simulator API                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  POST   /api/register/      Register new user                   │
│         Body: {"username", "email", "password"}                 │
│                                                                  │
│  POST   /api/login/         Login (get JWT tokens)              │
│         Body: {"username", "password"}                          │
│         Response: {"access", "refresh"}                         │
│                                                                  │
│  POST   /api/refresh/       Refresh access token                │
│         Body: {"refresh"}                                       │
│         Response: {"access"}                                    │
│                                                                  │
│  GET    /api/profile/       Get user profile                    │
│         Header: Authorization: Bearer <token>                   │
│         Response: {"id", "username", "email"}                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Running the Server

```bash
# Navigate to project directory
cd AI_Interview_Simulator

# Apply database migrations
python manage.py migrate

# Create a superuser (optional, for admin access)
python manage.py createsuperuser

# Run the development server
python manage.py runserver

# Server will be available at: http://localhost:8000
```

---

## Summary

This implementation provides:

✅ **JWT Authentication** - Secure token-based authentication  
✅ **Protected Profile API** - Returns user id, username, email  
✅ **Token Refresh** - Get new access tokens without re-login  
✅ **Comprehensive Error Handling** - Clear error messages  
✅ **Beginner-Friendly Documentation** - Line-by-line explanations  
✅ **Production-Ready Code** - Follows DRF best practices  
✅ **Debugging Guide** - Solutions for common issues  

You now have a complete, working Profile API with JWT authentication!