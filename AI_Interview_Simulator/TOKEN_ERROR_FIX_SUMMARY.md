# JWT Token Error Fix: "Given token not valid for any token type"

## Problem Analysis

The error **"Given token not valid for any token type"** from Django SimpleJWT occurs when the JWT token cannot be validated. This is a comprehensive guide to diagnose and fix this issue.

---

## Root Causes Identified

### 1. **Using Refresh Token Instead of Access Token** (Most Common)
Your login endpoint returns two tokens:
- `access` - For API requests (expires in 60 minutes)
- `refresh` - For getting new access tokens (expires in 7 days)

**The Error:** Using `refresh` token in `Authorization: Bearer <token>` header.

**The Fix:** Always use the `access` token for API requests.

```javascript
// CORRECT - Use access token
const token = localStorage.getItem('access_token');
headers: { 'Authorization': 'Bearer ' + token }

// WRONG - Don't use refresh token for API calls
const token = localStorage.getItem('refresh_token'); // ❌
```

### 2. **Token Expired**
Access tokens expire after 60 minutes (configured in `settings.py`).

**The Fix:** Implement automatic token refresh using the refresh token.

### 3. **Incorrect Authorization Header Format**
The header must be exactly: `Authorization: Bearer <token>`

Common mistakes:
- Missing space: `Bearer<token>` ❌
- Extra spaces: `Bearer  <token>` ❌
- Wrong case: `bearer <token>` ❌

### 4. **Token Corrupted or Truncated**
Token might have extra characters, whitespace, or be incomplete.

### 5. **SECRET_KEY Changed**
If Django's `SECRET_KEY` was modified, all existing tokens become invalid.

---

## Solutions Implemented

### 1. Created AuthManager JavaScript Library

**File:** `static/js/auth.js`

A comprehensive authentication manager that handles:
- Token storage and retrieval
- Token expiration checking
- Automatic token refresh
- Authenticated API requests
- Debug utilities

**Usage:**
```html
<script src="/static/js/auth.js"></script>
<script>
    // Check if authenticated
    if (AuthManager.isAuthenticated()) {
        // Make authenticated request
        const response = await AuthManager.fetch('/api/profile/');
    }
    
    // Debug token issues
    AuthManager.debug();
</script>
```

### 2. Updated Templates

**Login Page (`login.html`):**
- Now uses `AuthManager.setTokens()` to store tokens properly
- Consistent token storage across the application

**Interview Setup Page (`interviewsetuppage.html`):**
- Uses `AuthManager.fetch()` for automatic token handling
- Automatic token refresh if expired
- Proper error handling

### 3. Fixed Backend Configuration

**Settings.py:**
- Removed duplicate `load_dotenv()` calls
- Verified JWT configuration is correct
- CORS middleware properly ordered

---

## How to Debug Token Issues

### Step 1: Open Browser Developer Tools
Press `F12` or right-click → Inspect → Console

### Step 2: Run AuthManager Debug
```javascript
// Enable debug mode
AuthManager.setDebug(true);

// Print debug information
AuthManager.debug();
```

This will show:
- Whether you have an access token
- Whether you have a refresh token
- Token structure (should have 3 parts)
- Token expiration status
- Token payload (including expiry time)

### Step 3: Check Common Issues

```javascript
// 1. Check which token you're using
console.log('Access Token:', localStorage.getItem('access_token'));
console.log('Refresh Token:', localStorage.getItem('refresh_token'));

// 2. Verify token structure (should be 3 parts)
const token = localStorage.getItem('access_token');
if (token) {
    const parts = token.split('.');
    console.log('Token parts:', parts.length); // Should be 3
}

// 3. Check Authorization header format
const authHeader = 'Bearer ' + token;
console.log('Auth header:', authHeader);
console.log('Starts with "Bearer ":', authHeader.startsWith('Bearer '));

// 4. Check if token is expired
console.log('Token expired:', AuthManager.isTokenExpired(token));
```

---

## Testing the Fix

### Test 1: Login and Access Profile
```javascript
// 1. Login
const loginResponse = await fetch('/api/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'testuser', password: 'testpass123' })
});
const { access, refresh } = await loginResponse.json();

// 2. Store tokens using AuthManager
AuthManager.setTokens(access, refresh, 'testuser');

// 3. Access protected endpoint
const profileResponse = await AuthManager.fetch('/api/profile/');
const profile = await profileResponse.json();
console.log('Profile:', profile);
```

### Test 2: Token Refresh
```javascript
// Wait for token to expire (or use an expired token)
// Then try to access protected endpoint
const response = await AuthManager.fetch('/api/profile/');
// AuthManager should automatically refresh the token
```

### Test 3: Debug Output
```javascript
// Run this in browser console
AuthManager.debug();

// Expected output:
// === AuthManager Debug Info ===
// Has Access Token: true
// Has Refresh Token: true
// Access Token Length: 200+ (varies)
// Refresh Token Length: 200+ (varies)
// Access Token Expired: false
// Is Authenticated: true
// Access Token Parts: 3
// Access Token Structure: valid
// Token Payload: { token_type: "access", exp: 1234567890, ... }
// Token Expires: 2024-01-01T12:00:00.000Z
// ==============================
```

---

## Quick Fix Checklist

When you encounter "Given token not valid for any token type":

1. **Check which token you're using**
   ```javascript
   console.log('Using token:', localStorage.getItem('access_token') ? 'access' : 'none');
   ```

2. **Verify Authorization header**
   ```javascript
   console.log('Header:', 'Bearer ' + localStorage.getItem('access_token'));
   ```

3. **Check token structure**
   ```javascript
   const parts = localStorage.getItem('access_token').split('.');
   console.log('Parts:', parts.length); // Should be 3
   ```

4. **Check token expiration**
   ```javascript
   console.log('Expired:', AuthManager.isTokenExpired(localStorage.getItem('access_token')));
   ```

5. **Try token refresh**
   ```javascript
   await AuthManager.refreshAccessToken();
   ```

6. **Clear and re-login**
   ```javascript
   AuthManager.clearTokens();
   window.location.href = '/login/';
   ```

---

## Files Modified/Created

### Modified:
1. `config/settings.py` - Removed duplicate `load_dotenv()`
2. `users/templates/login.html` - Uses AuthManager for token storage
3. `users/templates/interviewsetuppage.html` - Uses AuthManager for API calls

### Created:
1. `static/js/auth.js` - AuthManager library
2. `JWT_TOKEN_DEBUG_GUIDE.md` - Comprehensive debugging guide
3. `TOKEN_ERROR_FIX_SUMMARY.md` - This document

---

## Prevention

To prevent this error in the future:

1. **Always use AuthManager** for authentication:
   ```javascript
   // Instead of manual token handling
   const response = await AuthManager.fetch('/api/endpoint/');
   ```

2. **Enable debug mode during development**:
   ```javascript
   AuthManager.setDebug(true);
   ```

3. **Check console for warnings** about token expiration

4. **Test token refresh** before deploying

5. **Never manually handle tokens** - let AuthManager do it

---

## Support

If you still encounter issues:

1. Run `AuthManager.debug()` in browser console
2. Check the output for any red flags
3. Review `JWT_TOKEN_DEBUG_GUIDE.md` for detailed troubleshooting
4. Verify your Django server is running and accessible

---

## Summary

The "Given token not valid for any token type" error is now handled by:

1. **AuthManager** - Automatically handles token refresh and validation
2. **Proper token storage** - Using `access_token` for API calls
3. **Debug utilities** - Easy diagnosis of token issues
4. **Updated templates** - Consistent authentication across the app

Your authentication system is now robust and self-healing!