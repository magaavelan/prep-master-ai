# JWT Token Debug Guide: "Given token not valid for any token type"

## Quick Diagnosis

The error **"Given token not valid for any token type"** typically occurs when:

1. **Using refresh token as access token** - Most common cause
2. **Token is expired** - Access tokens expire after 60 minutes
3. **Token is corrupted** - Extra characters, whitespace, or truncation
4. **Wrong Authorization header format** - Missing "Bearer " prefix or extra spaces
5. **Token from different SECRET_KEY** - Server key changed

---

## Step-by-Step Debugging

### Step 1: Verify You're Using the Correct Token

Your login response returns TWO tokens:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

- **`access`** = Used for API requests (expires in 60 minutes)
- **`refresh`** = Used to get new access tokens (expires in 7 days)

**Common Mistake:** Using `refresh` token in Authorization header instead of `access` token.

**Fix:** Always use the `access` token for API requests:
```javascript
// CORRECT
const token = localStorage.getItem('access_token');  // This is the ACCESS token

// WRONG - Don't do this!
const token = localStorage.getItem('refresh_token');  // This is the REFRESH token
```

### Step 2: Check Token Storage

Add this debugging code to your frontend to verify token storage:

```javascript
// Debug: Check what's stored
console.log('Access Token:', localStorage.getItem('access_token'));
console.log('Refresh Token:', localStorage.getItem('refresh_token'));

// Verify token structure (JWT has 3 parts separated by dots)
const token = localStorage.getItem('access_token');
if (token) {
    const parts = token.split('.');
    console.log('Token parts:', parts.length); // Should be 3
    if (parts.length !== 3) {
        console.error('Invalid token structure!');
    }
}
```

### Step 3: Verify Authorization Header Format

The Authorization header MUST be exactly:
```
Authorization: Bearer <token>
```

**Common mistakes:**
- Missing space after "Bearer"
- Extra spaces before or after token
- Using "bearer" (lowercase) instead of "Bearer"
- Using "Bearer:" with colon

**Correct format:**
```javascript
headers: {
    'Authorization': 'Bearer ' + token  // Space after "Bearer", no extra spaces
}
```

**Debug the header:**
```javascript
const token = localStorage.getItem('access_token');
const authHeader = 'Bearer ' + token;
console.log('Authorization Header:', authHeader);
console.log('Header length:', authHeader.length);

// Check for common issues
if (authHeader.includes('  ')) {
    console.error('Double space detected!');
}
if (!authHeader.startsWith('Bearer ')) {
    console.error('Missing "Bearer " prefix!');
}
```

### Step 4: Check Token Expiration

Your access tokens expire after 60 minutes. Check if token is expired:

```javascript
function isTokenExpired(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const payload = JSON.parse(atob(base64));
        const currentTime = Date.now() / 1000;
        return payload.exp < currentTime;
    } catch (error) {
        return true; // If we can't decode, assume expired
    }
}

const token = localStorage.getItem('access_token');
if (token && isTokenExpired(token)) {
    console.warn('Token is expired! Need to refresh.');
    // Call refresh endpoint
}
```

### Step 5: Implement Token Refresh Logic

Add automatic token refresh to your frontend:

```javascript
async function refreshAccessToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
        console.error('No refresh token available');
        return false;
    }
    
    try {
        const response = await fetch('/api/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('access_token', data.access);
            console.log('Token refreshed successfully');
            return true;
        } else {
            console.error('Token refresh failed:', data);
            // Clear tokens and redirect to login
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login/';
            return false;
        }
    } catch (error) {
        console.error('Token refresh error:', error);
        return false;
    }
}

// Wrapper function for authenticated requests
async function authenticatedFetch(url, options = {}) {
    let token = localStorage.getItem('access_token');
    
    if (!token) {
        window.location.href = '/login/';
        throw new Error('No access token');
    }
    
    // Check if token is expired
    if (isTokenExpired(token)) {
        console.log('Token expired, refreshing...');
        const refreshed = await refreshAccessToken();
        if (!refreshed) {
            throw new Error('Failed to refresh token');
        }
        token = localStorage.getItem('access_token');
    }
    
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token,
        ...options.headers
    };
    
    let response = await fetch(url, { ...options, headers });
    
    // If we get 401, try refreshing once
    if (response.status === 401) {
        console.log('Got 401, trying token refresh...');
        const refreshed = await refreshAccessToken();
        if (refreshed) {
            token = localStorage.getItem('access_token');
            headers['Authorization'] = 'Bearer ' + token;
            response = await fetch(url, { ...options, headers });
        }
    }
    
    return response;
}
```

---

## Backend Verification

### Check Django Settings

Your `settings.py` should have:

```python
from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

**Important:** The `SIGNING_KEY` must be consistent. If you change `SECRET_KEY`, all existing tokens become invalid.

### Test Token Manually

Use this Python script to decode and verify your token:

```python
import jwt
from datetime import datetime

# Your Django SECRET_KEY (from settings.py)
SECRET_KEY = 'django-insecure-klf%tn&y6p#y@3rn8#076in2590%udaq*jplmslh(+5bw_#!&3'

# Your token (copy from browser localStorage)
token = "YOUR_ACCESS_TOKEN_HERE"

try:
    # Decode the token
    decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    print("Token is valid!")
    print("Decoded payload:", decoded)
    
    # Check expiration
    exp_timestamp = decoded.get('exp')
    if exp_timestamp:
        exp_time = datetime.fromtimestamp(exp_timestamp)
        print(f"Expires at: {exp_time}")
        
        if datetime.now() > exp_time:
            print("WARNING: Token is expired!")
        else:
            print("Token is not expired")
except jwt.ExpiredSignatureError:
    print("ERROR: Token has expired!")
except jwt.InvalidTokenError as e:
    print(f"ERROR: Invalid token: {e}")
```

---

## Quick Fix Checklist

Run through this checklist when you get "Given token not valid for any token type":

- [ ] **Check which token you're using**
  - Am I using `access_token` (not `refresh_token`)?
  - `console.log(localStorage.getItem('access_token'))`

- [ ] **Check Authorization header format**
  - Is it exactly `Bearer <token>`?
  - No extra spaces? `console.log('Bearer ' + token)`

- [ ] **Check token structure**
  - Does it have 3 parts? `token.split('.').length === 3`
  - No truncation or corruption?

- [ ] **Check token expiration**
  - Is the token expired? Use the decode function above
  - If expired, call `/api/refresh/` endpoint

- [ ] **Check localStorage**
  - Is the token actually stored? `localStorage.getItem('access_token') !== null`
  - Was it cleared accidentally?

- [ ] **Check server configuration**
  - Is Django server running?
  - Did `SECRET_KEY` change? (This invalidates all tokens)
  - Are you hitting the correct server URL?

---

## Complete Working Example

Here's a complete, working frontend implementation:

```javascript
// Token management utility
const AuthManager = {
    // Get access token
    getAccessToken() {
        return localStorage.getItem('access_token');
    },
    
    // Get refresh token
    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    },
    
    // Check if token is expired
    isTokenExpired(token) {
        if (!token) return true;
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const payload = JSON.parse(atob(base64));
            const currentTime = Date.now() / 1000;
            return payload.exp < currentTime;
        } catch (error) {
            return true;
        }
    },
    
    // Refresh access token
    async refreshAccessToken() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) {
            console.error('No refresh token');
            return false;
        }
        
        try {
            const response = await fetch('/api/refresh/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh: refreshToken })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                localStorage.setItem('access_token', data.access);
                console.log('Token refreshed');
                return true;
            } else {
                console.error('Refresh failed:', data);
                this.logout();
                return false;
            }
        } catch (error) {
            console.error('Refresh error:', error);
            return false;
        }
    },
    
    // Make authenticated request
    async fetch(url, options = {}) {
        let token = this.getAccessToken();
        
        if (!token) {
            console.error('No access token');
            this.logout();
            throw new Error('Not authenticated');
        }
        
        // Refresh if expired
        if (this.isTokenExpired(token)) {
            console.log('Token expired, refreshing...');
            const refreshed = await this.refreshAccessToken();
            if (!refreshed) {
                throw new Error('Failed to refresh token');
            }
            token = this.getAccessToken();
        }
        
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
            ...options.headers
        };
        
        console.log('Making request to:', url);
        console.log('Auth header:', 'Bearer ' + token.substring(0, 20) + '...');
        
        let response = await fetch(url, { ...options, headers });
        
        // Handle 401 - try refresh once
        if (response.status === 401) {
            console.log('Got 401, trying refresh...');
            const refreshed = await this.refreshAccessToken();
            if (refreshed) {
                token = this.getAccessToken();
                headers['Authorization'] = 'Bearer ' + token;
                response = await fetch(url, { ...options, headers });
            }
        }
        
        return response;
    },
    
    // Logout
    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('username');
        window.location.href = '/login/';
    },
    
    // Debug info
    debug() {
        const accessToken = this.getAccessToken();
        const refreshToken = this.getRefreshToken();
        
        console.log('=== Auth Debug Info ===');
        console.log('Has access token:', !!accessToken);
        console.log('Has refresh token:', !!refreshToken);
        console.log('Access token length:', accessToken ? accessToken.length : 0);
        console.log('Refresh token length:', refreshToken ? refreshToken.length : 0);
        
        if (accessToken) {
            console.log('Access token parts:', accessToken.split('.').length);
            console.log('Access token expired:', this.isTokenExpired(accessToken));
            
            try {
                const base64Url = accessToken.split('.')[1];
                const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
                const payload = JSON.parse(atob(base64));
                console.log('Access token payload:', payload);
            } catch (e) {
                console.error('Could not decode token:', e);
            }
        }
        
        console.log('======================');
    }
};

// Usage example
async function callProtectedAPI() {
    try {
        const response = await AuthManager.fetch('/api/profile/');
        const data = await response.json();
        
        if (response.ok) {
            console.log('Profile data:', data);
        } else {
            console.error('API error:', data);
        }
    } catch (error) {
        console.error('Request failed:', error);
    }
}

// Run debug
AuthManager.debug();
```

---

## Common Scenarios and Solutions

### Scenario 1: Token works initially, then fails after some time
**Cause:** Token expired (60 minutes)
**Solution:** Implement token refresh logic

### Scenario 2: Token never works, always get "not valid"
**Cause:** Using refresh token instead of access token
**Solution:** Check which token you're storing and using

### Scenario 3: Token works in some browsers but not others
**Cause:** Token stored differently or corrupted in some browsers
**Solution:** Clear localStorage and re-login

### Scenario 4: Token worked yesterday but not today
**Cause:** Token expired or SECRET_KEY changed
**Solution:** Check if SECRET_KEY was modified, re-login

### Scenario 5: Getting 401 but token seems valid
**Cause:** Authorization header format wrong
**Solution:** Check for extra spaces, correct "Bearer " prefix

---

## Testing Commands

### Test with cURL
```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}' | python -c "import sys, json; print(json.load(sys.stdin)['access'])")

# Use token
curl -X GET http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer $TOKEN"
```

### Test with Python
```python
import requests

# Login
response = requests.post('http://localhost:8000/api/login/', 
    json={'username': 'testuser', 'password': 'testpass123'})
token = response.json()['access']

# Use token
response = requests.get('http://localhost:8000/api/profile/',
    headers={'Authorization': f'Bearer {token}'})
print(response.status_code, response.json())
```

---

## Final Checklist

After implementing fixes, verify:

- [ ] Login stores both `access_token` and `refresh_token`
- [ ] API calls use `access_token` (not `refresh_token`)
- [ ] Authorization header is exactly `Bearer <token>` (no extra spaces)
- [ ] Token refresh is implemented and working
- [ ] Expired tokens are automatically refreshed
- [ ] Debug logging shows correct token and header
- [ ] All API calls work without "not valid" errors

If you still have issues after following this guide, run `AuthManager.debug()` in your browser console and share the output for further assistance.