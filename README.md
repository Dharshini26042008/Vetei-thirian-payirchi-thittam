# FitBuddy - AI Fitness Plan Generator

FitBuddy is an AI-powered fitness planning application built using:

- FastAPI
- Google Gemini
- SQLite
- SQLAlchemy
- Jinja2
- HTML
- CSS
- Python

## Features

1. Personalized 7-day workout plans
2. Nutrition/recovery tips
3. Feedback-based workout plan updates
4. SQLite database
5. Admin dashboard
6. Delete user
7. FastAPI API documentation
8. JSON API
9. Demo mode

## Installation

Create virtual environment:

python -m venv venv

Activate on Windows:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

## Environment

Create `.env`.

Example:

GEMINI_API_KEY=YOUR_GEMINI_API_KEY

GEMINI_WORKOUT_MODEL=gemini-3.8-flash

GEMINI_FLASH_MODEL=gemini-3.8-flash

DEMO_MODE=false

DATABASE_URL=sqlite:///./fitbuddy.db

## Run

uvicorn app.main:app --reload

Open:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

Admin:

http://127.0.0.1:8000/view-all-users

Health check:

http://127.0.0.1:8000/health