from google import genai
from google.genai import types

from .config import (
    DEMO_MODE,
    GEMINI_API_KEY,
    GEMINI_FLASH_MODEL
)


def get_client():

    if not GEMINI_API_KEY:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


def demo_nutrition_tip(goal):

    return (
        f"For {goal}, focus on balanced meals, "
        "adequate hydration, a protein source with "
        "your meals, and enough sleep for recovery."
    )


def generate_nutrition_tip_with_flash(
    goal,
    age,
    weight
):

    if DEMO_MODE or not GEMINI_API_KEY:

        return demo_nutrition_tip(goal)


    prompt = f"""
Give one concise nutrition or recovery tip.

Fitness Goal:
{goal}

Age:
{age}

Weight:
{weight} kg

Requirements:

- 2 to 4 sentences.
- Practical.
- Easy to understand.
- Focus on hydration,
  balanced nutrition,
  protein,
  sleep,
  or recovery.
- Do not provide medical treatment.
"""


    client = get_client()


    response = client.models.generate_content(

        model=GEMINI_FLASH_MODEL,

        contents=prompt,

        config=types.GenerateContentConfig(

            temperature=0.5,

            max_output_tokens=300
        )
    )


    return (
        response.text
        if response.text
        else
        "Focus on hydration, balanced meals, protein and adequate recovery."
    )