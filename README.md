# 🚀 AI Interview Simulator - Master Documentation

A comprehensive, AI-powered interview practice platform built with Django REST Framework (DRF) and OpenRouter. This application features secure JWT authentication, a modern responsive frontend, and real-time AI evaluation of user answers.

---

## 📋 Table of Contents
1. [Features & Tech Stack](#1-features--tech-stack)
2. [Project Structure](#2-project-structure)
3. [Quick Start & Installation](#3-quick-start--installation)
4. [Environment Variables](#4-environment-variables)
5. [API Documentation](#5-api-documentation)
6. [Frontend Integration (AuthManager)](#6-frontend-integration-authmanager)
7. [Debugging & Troubleshooting](#7-debugging--troubleshooting)

---

## 1. Features & Tech Stack

### ✨ Features
* **Secure Authentication:** Robust JWT implementation (Access & Refresh tokens) via SimpleJWT.
* **Modern UI:** Premium card-based layouts, glassmorphism aesthetics, and smooth UX.
* **AI Evaluation Engine:** Integrates with OpenRouter (GPT-4o) to evaluate technical and HR interview answers.
* **Dynamic Routing:** Protected profile and dashboard routes requiring active JWT validation.
* **Custom Logging:** Extensive backend logging for tracing AI provider requests and API health.

### 🛠 Tech Stack
* **Backend:** Python, Django, Django REST Framework (DRF)
* **Authentication:** djangorestframework-simplejwt, CORS Headers
* **AI Integration:** OpenRouter API (python-dotenv for secrets management)
* **Frontend:** HTML5, CSS3, Vanilla JavaScript (AuthManager class)
* **Database:** SQLite (Development)

---

## 2. Project Structure

    .
    ├── config/             # Main Django settings, JWT config, CORS middleware
    ├── users/              # Auth app: Registration, Login, Profile Views, Serializers
    ├── interviews/         # AI integration: Prompt generation, OpenRouter API calls
    ├── reports/            # Interview results and history analytics
    ├── static/             # JS scripts (including auth.js) and CSS
    ├── templates/          # Base UI layouts, Login, Dashboard, Session UI
    ├── .env                # Environment secrets (IGNORED IN GIT)
    ├── .gitignore          # Git exclusion rules
    ├── manage.py           # Django management script
    └── requirements.txt    # Python dependencies

---

## 3. Quick Start & Installation

### Step 1: Clone & Setup
    
    # Clone the repository
    git clone https://github.com/YOUR-USERNAME/prep-master-ai.git
    cd prep-master-ai

    # Create and activate a virtual environment
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate

    # Install dependencies
    pip install -r requirements.txt

### Step 2: Database & Server Setup
    
    # Apply database migrations
    python manage.py migrate

    # Create a superuser (optional)
    python manage.py createsuperuser

    # Start the development server
    python manage.py runserver
    
The application will be live at http://localhost:8000.

---

## 4. Environment Variables

Create a .env file in the root directory (same level as manage.py). Never commit this file to Git.

    # AI Provider Selection
    AI_PROVIDER=openrouter  # Options: openai, openrouter, grok (default: openrouter)

    # OpenRouter Configuration (Required)
    OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
    OPENROUTER_MODEL=openai/gpt-4o
    OPENROUTER_HTTP_REFERER=http://localhost:8000
    OPENROUTER_X_TITLE=AI Interview Simulator

To verify environment variables are loading, run the Django shell:
    
    python manage.py shell
    >>> import os
    >>> from dotenv import load_dotenv
    >>> load_dotenv()
    >>> print(os.getenv("OPENROUTER_API_KEY"))

---

## 5. API Documentation

All API endpoints are prefixed with /api/. Requests to protected routes must include the Authorization: Bearer <access_token> header.

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | /api/register/ | No | Register a new user |
| POST | /api/login/ | No | Get JWT tokens (access and refresh) |
| POST | /api/refresh/ | No | Refresh access token using refresh token |
| GET  | /api/profile/ | Yes | Get user profile (id, username, email) |
| PUT  | /api/profile/ | Yes | Update user profile |

Example cURL Request (Protected Profile Endpoint):
    
    curl -X GET http://localhost:8000/api/profile/ \
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
      -H "Content-Type: application/json"

---

## 6. Frontend Integration (AuthManager)

To handle token storage, expiration, and API requests securely, the frontend utilizes an AuthManager class.

Core Rules for Frontend Integration:
1. Never use the refresh token for API calls. Only send the access_token in the Authorization header.
2. Use AuthManager.fetch() to automatically handle token expiration and 401 retries.

Example AuthManager Usage:
    
    // Check if authenticated
    if (AuthManager.isAuthenticated()) {
        try {
            // Make authenticated request (AuthManager handles the Bearer token automatically)
            const response = await AuthManager.fetch('/api/profile/');
            const data = await response.json();
            console.log('Profile loaded:', data.username);
        } catch (error) {
            console.error('Session expired or request failed.');
        }
    } else {
        window.location.href = '/login/';
    }

---

## 7. Debugging & Troubleshooting

### JWT Token Issues
Error: "Given token not valid for any token type" (401 Unauthorized)

Quick Diagnostic Checklist:
1. Are you using the correct token? Ensure you are sending the access_token in headers, NOT the refresh_token.
2. Check Authorization header format: It must be exactly Bearer <token> (no extra spaces, case-sensitive "Bearer").
3. Is the token expired? Access tokens expire after 60 minutes. Use the /api/refresh/ endpoint to get a new one.
4. Did the SECRET_KEY change? If SECRET_KEY in settings.py was modified, all existing tokens are invalidated. Clear localStorage and log in again.
5. CORS Errors: Ensure CorsMiddleware is at the very top of the MIDDLEWARE list in settings.py.

### OpenRouter & AI Issues
Backend AI calls are logged to debug.log. Check the server terminal or tail the log file to view interactions:
    
    # Watch logs in real-time
    tail -f debug.log

Common Log Errors:
* 401 Authentication Failed: Your OPENROUTER_API_KEY is missing or invalid. Check your .env file.
* 429 rate_limit_exceeded: You have hit OpenRouter's limits. Wait a few minutes before trying again.
* Failed to parse extracted JSON: The AI model returned an answer outside of the expected JSON format.
* Missing 'choices' array in response: The OpenRouter API is experiencing issues or returning a server error.