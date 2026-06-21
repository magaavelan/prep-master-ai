# 🚀 AI Interview Simulator

A comprehensive, AI-powered interview practice platform built with Django REST Framework (DRF) and OpenRouter. This application features secure JWT authentication, a modern responsive frontend, and real-time AI evaluation of user answers.

---

## 📋 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start & Installation](#-quick-start--installation)
- [Environment Configuration](#-environment-configuration)
- [API Documentation](#-api-documentation)
- [Frontend Integration (AuthManager)](#-frontend-integration)
- [Troubleshooting & Debugging](#-troubleshooting--debugging)

---

## ✨ Features
* **Secure Authentication:** Robust JWT implementation (Access & Refresh tokens) via SimpleJWT.
* **Modern UI:** Premium card-based layouts, glassmorphism aesthetics, and smooth UX (including "Show Password" toggles).
* **AI Evaluation Engine:** Integrates with OpenRouter (GPT-4o) to evaluate technical and HR interview answers.
* **Dynamic Routing:** Protected profile and dashboard routes requiring active JWT validation.
* **Custom Logging:** Extensive backend logging for tracing AI provider requests and API health.

---

## 🛠 Tech Stack
* **Backend:** Python, Django, Django REST Framework (DRF)
* **Authentication:** djangorestframework-simplejwt, CORS Headers
* **AI Integration:** OpenRouter API (`python-dotenv` for secrets management)
* **Frontend:** HTML5, CSS3 (Modern Flex/Grid), Vanilla JavaScript (`AuthManager` class)
* **Database:** SQLite (Development)

---

## 📂 Project Structure
```text
AI_Interview_Simulator/
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