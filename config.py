import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
).strip()


GEMINI_WORKOUT_MODEL = os.getenv(
    "GEMINI_WORKOUT_MODEL",
    "gemini-3.8-flash"
).strip()


GEMINI_FLASH_MODEL = os.getenv(
    "GEMINI_FLASH_MODEL",
    "gemini-3.8-flash"
).strip()


DEMO_MODE = os.getenv(
    "DEMO_MODE",
    "false"
).lower() == "true"


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'fitbuddy.db'}"
)


APP_NAME = "FitBuddy"