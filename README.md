# 🤖 Prep Master AI - AI-Powered Interview Simulator

**Prep Master AI** is an AI-powered interview practice platform built using **Python, Django REST Framework, JWT Authentication, SQLite, and OpenRouter API**.

The platform helps users practice technical and HR interviews by selecting a role and difficulty level, answering interview questions, and receiving AI-generated feedback with a score, strengths, weaknesses, and an ideal answer.

---

## 🚀 Key Features

### 🔐 User Authentication

* User registration
* User login
* JWT access and refresh token authentication
* Protected APIs for logged-in users

### 🧠 AI-Powered Answer Evaluation

* Evaluates user answers using an AI model through OpenRouter API
* Returns structured feedback:

  * Score out of 10
  * Strengths
  * Weaknesses
  * Ideal answer

### 🎯 Role-Based Interview Practice

Users can practice interview questions based on different roles:

* Python
* Django
* Full Stack
* HR

### 📊 Difficulty-Based Questions

Each role supports multiple difficulty levels:

* Beginner
* Intermediate
* Advanced

### 📝 Interview Session Management

* Create interview sessions
* Retrieve interview questions
* Submit answers
* Store answer evaluations in the database
* View previous interview history

### 📈 Reports and Dashboard

* View total interviews
* View total answers
* Calculate average score
* Display detailed interview report with AI feedback

### 🖥️ Frontend Interface

* Login page
* Home page
* Interview setup page
* Interview session page
* Report page
* Dashboard/history page

---

## 🛠️ Tech Stack

| Category              | Technology                              |
| --------------------- | --------------------------------------- |
| Backend               | Python, Django, Django REST Framework   |
| Authentication        | JWT Authentication, SimpleJWT           |
| Database              | SQLite                                  |
| AI Integration        | OpenRouter API                          |
| Frontend              | HTML, CSS, JavaScript, Django Templates |
| API Testing           | Postman                                 |
| Tools                 | Git, GitHub, VS Code                    |
| Environment Variables | python-dotenv                           |

---

## 📂 Project Structure

```text
prep-master-ai/
│
├── AI_Interview_Simulator/
│   │
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   │
│   ├── users/
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── templates/
│   │
│   ├── interviews/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── question_bank.py
│   │   ├── ai_service.py
│   │   └── ai_providers.py
│   │
│   ├── reports/
│   │   ├── views.py
│   │   └── urls.py
│   │
│   ├── frontend_views.py
│   ├── frontend_urls.py
│   ├── manage.py
│   └── .gitignore
│
└── README.md
```

---

## 🗃️ Database Models

### 🎤 Interview

Stores interview session details.

Main fields:

* user
* role
* difficulty
* created_at

### 📝 Answer

Stores user answers and AI evaluation results.

Main fields:

* interview
* question
* user_answer
* score
* strengths
* weaknesses
* ideal_answer
* created_at

---

## 🔄 Application Flow

1. User registers or logs in.
2. Backend generates JWT access and refresh tokens.
3. User selects interview role and difficulty.
4. Django creates an interview session.
5. Backend returns questions from the question bank.
6. User submits an answer.
7. Django sends the question and answer to the AI evaluation service.
8. OpenRouter API returns structured feedback.
9. Backend stores the score, strengths, weaknesses, and ideal answer in SQLite.
10. User can view the final report and dashboard statistics.

---

## 🤖 AI Evaluation Flow

The AI is instructed to evaluate each answer and return structured feedback.

Example response format:

```json
{
  "score": 8,
  "strengths": "Good explanation with correct points.",
  "weaknesses": "Could include a real-time example.",
  "ideal_answer": "A better answer would explain the concept clearly with an example."
}
```

This makes the feedback easy to store, display, and use in reports.

---

## 🔐 Environment Variables

This project uses environment variables for sensitive configuration.

Create a `.env` file inside the `AI_Interview_Simulator` folder:

```env
SECRET_KEY=your_django_secret_key_here
DEBUG=True
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

> ⚠️ Never upload the `.env` file to GitHub.
> Make sure `.env` is added inside `.gitignore`.

---

## ⚙️ How to Run Locally

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/magaavelan/prep-master-ai.git
```

### 2️⃣ Move into the Project Folder

```bash
cd prep-master-ai/AI_Interview_Simulator
```

### 3️⃣ Create a Virtual Environment

```bash
python -m venv venv
```

### 4️⃣ Activate the Virtual Environment

For Windows:

```bash
venv\Scripts\activate
```

For macOS/Linux:

```bash
source venv/bin/activate
```

### 5️⃣ Install Required Packages

If `requirements.txt` is available:

```bash
pip install -r requirements.txt
```

Or install the main packages manually:

```bash
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers python-dotenv openai requests
```

### 6️⃣ Create `.env` File

Create a `.env` file and add:

```env
SECRET_KEY=your_django_secret_key_here
DEBUG=True
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 7️⃣ Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 8️⃣ Start the Development Server

```bash
python manage.py runserver
```

### 9️⃣ Open in Browser

```text
http://127.0.0.1:8000/
```

---

## 🔗 Main API Endpoints

### 👤 User APIs

| Method | Endpoint               | Description                 |
| ------ | ---------------------- | --------------------------- |
| POST   | `/api/users/register/` | Register a new user         |
| POST   | `/api/users/login/`    | Login and get JWT tokens    |
| POST   | `/api/users/refresh/`  | Refresh access token        |
| GET    | `/api/users/profile/`  | View logged-in user profile |

### 🎤 Interview APIs

| Method | Endpoint                                    | Description                     |
| ------ | ------------------------------------------- | ------------------------------- |
| POST   | `/api/interviews/create/`                   | Create a new interview          |
| GET    | `/api/interviews/`                          | View interview history          |
| GET    | `/api/interviews/<interview_id>/questions/` | Get questions for an interview  |
| POST   | `/api/interviews/submit-answer/`            | Submit answer for AI evaluation |
| GET    | `/api/interviews/answers/`                  | View submitted answers          |

### 📊 Report APIs

| Method | Endpoint                                 | Description                    |
| ------ | ---------------------------------------- | ------------------------------ |
| GET    | `/api/reports/dashboard/`                | View dashboard statistics      |
| GET    | `/api/reports/interview/<interview_id>/` | View detailed interview report |

---

## 💡 Example Use Case

A user can select:

```text
Role: Python
Difficulty: Beginner
```

Then the system provides interview questions. After the user submits an answer, the AI evaluates it and returns:

* Score
* Strengths
* Weaknesses
* Ideal answer

This helps the user understand how to improve their interview answers.

---

## 📚 What I Learned

Through this project, I practiced:

* Django project structure
* Django REST Framework APIs
* JWT authentication
* Access and refresh token handling
* Protected API endpoints
* Django ORM relationships
* Serializers and API views
* SQLite database handling
* AI API integration using OpenRouter
* Prompt-based answer evaluation
* JSON response parsing
* Dashboard and report generation
* Frontend and backend integration
* API testing using Postman

---

## ⚠️ Important Note

This project is created for learning and portfolio purposes.

It is not a real interview hiring system. The AI feedback is generated for practice and improvement, not for official candidate evaluation.

---

## 👨‍💻 Author

**Magaavelan S**
Python Developer Fresher

🔗 GitHub: https://github.com/magaavelan
