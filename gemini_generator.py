import time

from google import genai
from google.genai import types

from .config import (
    DEMO_MODE,
    GEMINI_API_KEY,
    GEMINI_WORKOUT_MODEL,
)


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are FitBuddy, an AI fitness planning assistant.

Create practical, structured and safe workout plans.

Do not diagnose medical conditions.
Do not provide medical treatment.

If the user mentions injury, pregnancy, severe pain,
medical conditions, or other health concerns,
recommend consulting a qualified healthcare professional.

Keep workouts realistic and progressive.
"""


# ============================================================
# GEMINI CLIENT
# ============================================================

def get_client():

    if not GEMINI_API_KEY:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured in the .env file."
        )

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


# ============================================================
# LOCAL FALLBACK PLAN
# ============================================================

def demo_workout_plan(
    username,
    goal,
    intensity,
    experience_level
):

    return f"""
FITBUDDY - 7 DAY WORKOUT PLAN

Name: {username}

Goal: {goal}

Intensity: {intensity}

Experience Level: {experience_level}


==================================================
DAY 1 - FULL BODY
==================================================

Warm-up:
5-10 minutes easy walking and mobility.

Main Workout:

1. Bodyweight Squats
3 sets x 10-12 reps

2. Incline Push-ups
3 sets x 8-12 reps

3. Glute Bridges
3 sets x 12-15 reps

4. Plank
3 sets x 20-30 seconds

Rest:
45-60 seconds between sets.

Cooldown:
5 minutes gentle stretching.


==================================================
DAY 2 - CARDIO
==================================================

Warm-up:
5 minutes easy walking.

Main Workout:

Brisk walking or cycling
25-30 minutes.

Rest:
Take short breaks if required.

Cooldown:
5 minutes easy walking and stretching.


==================================================
DAY 3 - UPPER BODY + CORE
==================================================

Warm-up:
5-10 minutes.

Main Workout:

1. Incline Push-ups
3 sets x 8-12 reps

2. Resistance Band Rows
3 sets x 10-12 reps

3. Shoulder Press
3 sets x 10 reps

4. Dead Bug
3 sets x 8 reps each side

Rest:
45-60 seconds between sets.

Cooldown:
5 minutes stretching.


==================================================
DAY 4 - ACTIVE RECOVERY
==================================================

Light Walking:
20-30 minutes.

Gentle Stretching:
10 minutes.

Focus on recovery.


==================================================
DAY 5 - LOWER BODY
==================================================

Warm-up:
5-10 minutes.

Main Workout:

1. Squats
3 sets x 10-12 reps

2. Reverse Lunges
3 sets x 8 reps each side

3. Glute Bridges
3 sets x 12-15 reps

4. Calf Raises
3 sets x 15 reps

Rest:
45-60 seconds between sets.

Cooldown:
5 minutes stretching.


==================================================
DAY 6 - CARDIO + CORE
==================================================

Warm-up:
5 minutes.

Main Workout:

Moderate Cardio
20-30 minutes

Bird Dog
3 sets x 8 reps each side

Plank
3 sets x 20-30 seconds

Cooldown:
5 minutes.


==================================================
DAY 7 - REST / RECOVERY
==================================================

Rest and recovery.

Optional light walking if comfortable.

Gentle mobility exercises.

Focus on sleep, hydration and recovery.


==================================================
GENERAL GUIDANCE
==================================================

Progress gradually.

Stay hydrated.

Take adequate rest.

Do not exercise through sharp pain.

Stop exercising if you experience:
- Chest pain
- Severe dizziness
- Sharp pain
- Breathing difficulty
- Other unusual symptoms

For injuries, pregnancy, medical conditions,
or severe pain, consult a qualified healthcare
professional before exercising.
"""


# ============================================================
# ERROR DETECTION
# ============================================================

def is_temporary_gemini_error(error):

    error_text = str(error).lower()

    temporary_errors = [
        "503",
        "unavailable",
        "high demand",
        "overloaded",
        "temporarily unavailable",
        "internal server error",
        "deadline exceeded",
        "timeout",
    ]

    return any(
        message in error_text
        for message in temporary_errors
    )


def is_quota_error(error):

    error_text = str(error).lower()

    quota_errors = [
        "429",
        "resource_exhausted",
        "quota exceeded",
        "rate limit",
    ]

    return any(
        message in error_text
        for message in quota_errors
    )


# ============================================================
# GEMINI GENERATION
# ============================================================

def generate_with_gemini(
    client,
    model_name,
    prompt
):

    response = client.models.generate_content(

        model=model_name,

        contents=prompt,

        config=types.GenerateContentConfig(

            system_instruction=SYSTEM_INSTRUCTION,

            max_output_tokens=5000,

            # Gemini 3 reasoning level.
            # Low keeps the request lighter/faster.
            thinking_config=types.ThinkingConfig(
                thinking_level="low"
            ),
        ),
    )

    if response is None:

        raise RuntimeError(
            "Gemini returned no response."
        )

    response_text = getattr(
        response,
        "text",
        None
    )

    if not response_text:

        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return response_text


# ============================================================
# MAIN WORKOUT GENERATOR
# ============================================================

def generate_workout_gemini(
    username,
    age,
    weight,
    goal,
    intensity,
    experience_level="beginner",
    workout_schedule="7 days"
):

    # --------------------------------------------------------
    # DEMO MODE
    # --------------------------------------------------------

    if DEMO_MODE:

        print(
            "[FitBuddy] DEMO_MODE=True -> "
            "Using local workout plan."
        )

        return demo_workout_plan(
            username,
            goal,
            intensity,
            experience_level
        )


    # --------------------------------------------------------
    # API KEY CHECK
    # --------------------------------------------------------

    if not GEMINI_API_KEY:

        print(
            "[FitBuddy] Gemini API key missing -> "
            "Using local workout plan."
        )

        return demo_workout_plan(
            username,
            goal,
            intensity,
            experience_level
        )


    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    prompt = f"""
Create a personalized 7-day workout plan.

USER INFORMATION

Name: {username}

Age: {age}

Weight: {weight} kg

Fitness Goal: {goal}

Workout Intensity: {intensity}

Experience Level: {experience_level}

Workout Schedule: {workout_schedule}


REQUIREMENTS

1. Create a complete Day 1 through Day 7 plan.

2. Include warm-up.

3. Include the main workout.

4. Include exercise names.

5. Include sets and repetitions OR duration.

6. Include rest intervals.

7. Include cooldown/recovery.

8. Match the selected intensity.

9. Keep the plan realistic and practical.

10. Make it easy for a beginner to understand.

11. Do not diagnose medical conditions.

12. Do not provide medical treatment.

13. Do not make unrealistic health or weight-loss promises.

14. Day 7 should be a rest/recovery day unless
    there is a strong reason otherwise.


FORMAT

FITBUDDY 7-DAY WORKOUT PLAN

DAY 1
Warm-up:
Workout:
Rest:
Cooldown:

DAY 2
Warm-up:
Workout:
Rest:
Cooldown:

DAY 3
Warm-up:
Workout:
Rest:
Cooldown:

DAY 4
Warm-up:
Workout:
Rest:
Cooldown:

DAY 5
Warm-up:
Workout:
Rest:
Cooldown:

DAY 6
Warm-up:
Workout:
Rest:
Cooldown:

DAY 7
Recovery:

GENERAL GUIDANCE:
"""


    # --------------------------------------------------------
    # CREATE CLIENT
    # --------------------------------------------------------

    try:

        client = get_client()

    except Exception as error:

        print(
            f"[FitBuddy] Client creation error: {error}"
        )

        return demo_workout_plan(
            username,
            goal,
            intensity,
            experience_level
        )


    # --------------------------------------------------------
    # MODELS TO TRY
    # --------------------------------------------------------

    models_to_try = []

    # Primary configured model
    if GEMINI_WORKOUT_MODEL:

        models_to_try.append(
            GEMINI_WORKOUT_MODEL
        )


    # Fallback model 1
    if "gemini-3.7-flash" not in models_to_try:

        models_to_try.append(
            "gemini-3.7-flash"
        )


    # Fallback model 2
    if "gemini-3.6-flash" not in models_to_try:

        models_to_try.append(
            "gemini-3.6-flash"
        )


    # --------------------------------------------------------
    # TRY MODELS
    # --------------------------------------------------------

    for model_name in models_to_try:

        print(
            f"[FitBuddy] Trying Gemini model: "
            f"{model_name}"
        )


        # ----------------------------------------------------
        # Try current model up to 2 times for 503
        # ----------------------------------------------------

        for attempt in range(2):

            try:

                result = generate_with_gemini(
                    client=client,
                    model_name=model_name,
                    prompt=prompt
                )

                print(
                    f"[FitBuddy] Success using "
                    f"{model_name}"
                )

                return result


            except Exception as error:

                print(
                    f"[FitBuddy] {model_name} error: "
                    f"{error}"
                )


                # ------------------------------------------------
                # 429 QUOTA ERROR
                # ------------------------------------------------

                if is_quota_error(error):

                    print(
                        "[FitBuddy] Gemini quota exceeded."
                    )

                    # Do NOT repeatedly retry quota errors.
                    # Move to the next model.
                    break


                # ------------------------------------------------
                # 503 TEMPORARY ERROR
                # ------------------------------------------------

                if is_temporary_gemini_error(error):

                    if attempt == 0:

                        wait_seconds = 3

                        print(
                            "[FitBuddy] Gemini temporarily "
                            "unavailable."
                        )

                        print(
                            f"[FitBuddy] Retrying in "
                            f"{wait_seconds} seconds..."
                        )

                        time.sleep(
                            wait_seconds
                        )

                        continue

                    else:

                        print(
                            "[FitBuddy] Model still unavailable."
                        )

                        break


                # ------------------------------------------------
                # Other error
                # ------------------------------------------------

                break


    # --------------------------------------------------------
    # ALL GEMINI MODELS FAILED
    # --------------------------------------------------------

    print(
        "[FitBuddy] All Gemini attempts failed."
    )

    print(
        "[FitBuddy] Using local FitBuddy fallback plan."
    )


    # --------------------------------------------------------
    # GUARANTEED FALLBACK
    # --------------------------------------------------------

    return demo_workout_plan(
        username,
        goal,
        intensity,
        experience_level
    )