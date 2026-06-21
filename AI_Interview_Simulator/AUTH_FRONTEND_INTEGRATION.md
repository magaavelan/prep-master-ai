# Authentication & Frontend Integration Guide

## Fixed Issues

### 1. Profile API 401/404 Errors - **FIXED**
**Problem:** `/api/profile/` was returning 401 Unauthorized even with valid JWT tokens.

**Root Cause:** 
- The `ProfileView` had `AllowAny` permission but then manually checked authentication and returned 401
- This created a logical conflict where unauthenticated users could access the endpoint but would get an error

**Solution:**
- Changed `ProfileView` to use `IsAuthenticated` permission
- Removed manual authentication check (DRF handles it automatically)
- Now returns proper 401 with WWW-Authenticate header when no valid token

### 2. CORS Middleware Order - **FIXED**
**Problem:** CORS headers might not be properly set, causing frontend requests to fail.

**Solution:**
- Moved `CorsMiddleware` to the top of MIDDLEWARE list (must be before `CommonMiddleware`)
- Added `CORS_ALLOW_CREDENTIALS = True`

### 3. JWT Authentication Flow - **VERIFIED**
The JWT setup in `settings.py` is correct:
- `rest_framework_simplejwt.authentication.JWTAuthentication` is configured
- Token lifetime: 60 minutes for access, 7 days for refresh
- `AUTH_HEADER_TYPES: ('Bearer',)` is properly set

## API Endpoints

### Authentication Endpoints

#### 1. Register User
```
POST /api/register/
Content-Type: application/json

Request Body:
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123"
}

Response (201 Created):
{
    "message": "User registered successfully"
}

Response (400 Bad Request):
{
    "username": ["This field is required."],
    "email": ["Enter a valid email address."],
    ...
}
```

#### 2. Login (Get JWT Tokens)
```
POST /api/login/
Content-Type: application/json

Request Body:
{
    "username": "john_doe",
    "password": "securepassword123"
}

Response (200 OK):
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

Response (401 Unauthorized):
{
    "detail": "No active account found with the given credentials"
}
```

#### 3. Refresh Access Token
```
POST /api/refresh/
Content-Type: application/json

Request Body:
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

Response (200 OK):
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

Response (401 Unauthorized):
{
    "detail": "Token is invalid or expired"
}
```

#### 4. Get User Profile (Protected)
```
GET /api/profile/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
}

Response (401 Unauthorized):
{
    "detail": "Authentication credentials were not provided."
}
```

#### 5. Update User Profile (Protected)
```
PUT /api/profile/
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
    "username": "new_username",
    "email": "newemail@example.com"
}

Response (200 OK):
{
    "id": 1,
    "username": "new_username",
    "email": "newemail@example.com"
}
```

## Frontend Implementation

### JavaScript/React Fetch Examples

#### 1. Login Function
```javascript
async function login(username, password) {
    try {
        const response = await fetch('http://localhost:8000/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();

        if (response.ok) {
            // Store tokens in localStorage
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            return { success: true, data };
        } else {
            return { success: false, error: data.detail || 'Login failed' };
        }
    } catch (error) {
        console.error('Login error:', error);
        return { success: false, error: 'Network error' };
    }
}
```

#### 2. Get Profile Function
```javascript
async function getProfile() {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        return { success: false, error: 'No authentication token' };
    }

    try {
        const response = await fetch('http://localhost:8000/api/profile/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
        });

        const data = await response.json();

        if (response.ok) {
            return { success: true, data };
        } else if (response.status === 401) {
            // Token might be expired, try to refresh
            const refreshResult = await refreshAccessToken();
            if (refreshResult.success) {
                // Retry with new token
                return await getProfile();
            }
            return { success: false, error: 'Authentication failed' };
        } else {
            return { success: false, error: data.detail || 'Failed to get profile' };
        }
    } catch (error) {
        console.error('Profile error:', error);
        return { success: false, error: 'Network error' };
    }
}
```

#### 3. Refresh Token Function
```javascript
async function refreshAccessToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
        return { success: false, error: 'No refresh token' };
    }

    try {
        const response = await fetch('http://localhost:8000/api/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken }),
        });

        const data = await response.json();

        if (response.ok) {
            // Store new access token
            localStorage.setItem('access_token', data.access);
            return { success: true, data };
        } else {
            // Refresh token expired, user needs to login again
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            return { success: false, error: 'Session expired, please login again' };
        }
    } catch (error) {
        console.error('Token refresh error:', error);
        return { success: false, error: 'Network error' };
    }
}
```

#### 4. Register Function
```javascript
async function register(username, email, password) {
    try {
        const response = await fetch('http://localhost:8000/api/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password }),
        });

        const data = await response.json();

        if (response.ok) {
            return { success: true, message: 'Registration successful' };
        } else {
            return { success: false, error: data };
        }
    } catch (error) {
        console.error('Register error:', error);
        return { success: false, error: 'Network error' };
    }
}
```

#### 5. API Call Helper with Auto-Refresh
```javascript
// Helper function for making authenticated API calls
async function authenticatedFetch(url, options = {}) {
    let token = localStorage.getItem('access_token');
    
    if (!token) {
        throw new Error('No authentication token');
    }

    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers,
    };

    let response = await fetch(url, {
        ...options,
        headers,
    });

    // If we get 401, try to refresh token and retry once
    if (response.status === 401) {
        const refreshResult = await refreshAccessToken();
        if (refreshResult.success) {
            token = localStorage.getItem('access_token');
            headers['Authorization'] = `Bearer ${token}`;
            
            response = await fetch(url, {
                ...options,
                headers,
            });
        } else {
            // Redirect to login or handle session expiry
            window.location.href = '/login';
            throw new Error('Session expired');
        }
    }

    return response;
}

// Usage example:
// const response = await authenticatedFetch('http://localhost:8000/api/interviews/');
// const data = await response.json();
```

### HTML/JavaScript Example (Vanilla JS)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Interview Simulator - Login</title>
</head>
<body>
    <div id="app">
        <!-- Login Form -->
        <div id="login-section">
            <h2>Login</h2>
            <form id="login-form">
                <input type="text" id="username" placeholder="Username" required>
                <input type="password" id="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            <div id="login-error" style="color: red;"></div>
        </div>

        <!-- Profile Section (shown after login) -->
        <div id="profile-section" style="display: none;">
            <h2>Welcome, <span id="user-name"></span>!</h2>
            <p>Email: <span id="user-email"></span></p>
            <button id="logout-btn">Logout</button>
        </div>
    </div>

    <script>
        const API_BASE_URL = 'http://localhost:8000/api';

        // Check if user is already logged in on page load
        document.addEventListener('DOMContentLoaded', async () => {
            const token = localStorage.getItem('access_token');
            if (token) {
                await showProfile();
            }
        });

        // Login form handler
        document.getElementById('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch(`${API_BASE_URL}/login/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password }),
                });

                const data = await response.json();

                if (response.ok) {
                    localStorage.setItem('access_token', data.access);
                    localStorage.setItem('refresh_token', data.refresh);
                    showProfileSection();
                    await showProfile();
                } else {
                    document.getElementById('login-error').textContent = 
                        data.detail || 'Login failed';
                }
            } catch (error) {
                document.getElementById('login-error').textContent = 'Network error';
            }
        });

        // Logout handler
        document.getElementById('logout-btn').addEventListener('click', () => {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            location.reload();
        });

        // Show profile section
        function showProfileSection() {
            document.getElementById('login-section').style.display = 'none';
            document.getElementById('profile-section').style.display = 'block';
        }

        // Fetch and display profile
        async function showProfile() {
            const token = localStorage.getItem('access_token');
            
            try {
                const response = await fetch(`${API_BASE_URL}/profile/`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    document.getElementById('user-name').textContent = data.username;
                    document.getElementById('user-email').textContent = data.email;
                    showProfileSection();
                } else if (response.status === 401) {
                    // Token invalid, clear and show login
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                }
            } catch (error) {
                console.error('Error fetching profile:', error);
            }
        }
    </script>
</body>
</html>
```

## Testing the Authentication

### Using cURL

#### 1. Register a new user
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123"}'
```

#### 2. Login and get tokens
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

#### 3. Get profile (replace YOUR_ACCESS_TOKEN with actual token)
```bash
curl -X GET http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 4. Refresh token
```bash
curl -X POST http://localhost:8000/api/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"YOUR_REFRESH_TOKEN"}'
```

## Troubleshooting

### Issue: 401 Unauthorized on protected endpoints
**Check:**
1. Token is included in Authorization header: `Authorization: Bearer <token>`
2. Token is not expired (access tokens last 60 minutes)
3. No extra spaces in the header

### Issue: CORS errors in browser
**Check:**
1. CORS middleware is at the top of MIDDLEWARE list
2. `CORS_ALLOW_ALL_ORIGINS = True` is set (for development)
3. Frontend is making requests to correct URL

### Issue: 404 Not Found
**Check:**
1. URL is correct: `/api/profile/` (not `/profile/` or `/api/profile`)
2. Django server is running on correct port
3. No typos in URL paths

### Issue: Token refresh not working
**Check:**
1. Refresh token is valid and not expired (7 days)
2. `ROTATE_REFRESH_TOKENS = True` means old refresh token is invalidated after use
3. Store the new refresh token returned from refresh endpoint

## Security Notes

1. **Never expose refresh tokens in client-side code** - In production, consider using httpOnly cookies
2. **Use HTTPS in production** - JWT tokens should only be transmitted over secure connections
3. **Set appropriate token lifetimes** - Current settings (60min access, 7 days refresh) are good for development
4. **Implement token blacklisting** - For logout functionality, consider implementing token blacklisting
5. **Validate token on each request** - The current setup does this automatically

## Next Steps

After authentication is working:
1. Implement interview session endpoints
2. Add AI-powered question generation
3. Create feedback and reporting system
4. Add user dashboard with interview history