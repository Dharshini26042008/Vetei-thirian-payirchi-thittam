from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from .database import get_db

from .gemini_generator import (
    generate_workout_gemini
)

from .gemini_flash_generator import (
    generate_nutrition_tip_with_flash
)

from .update_plan import (
    update_workout_plan
)

from .models import (
    delete_user,
    get_all_users,
    get_user,
    save_plan,
    save_user,
    update_plan
)

from .schemas import (
    FeedbackRequest,
    UserInput,
    UserResponse
)


BASE_DIR = Path(
    __file__
).resolve().parent.parent


templates = Jinja2Templates(
    directory=str(
        BASE_DIR / "templates"
    )
)


router = APIRouter()


# ==========================================
# HOME
# ==========================================

@router.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="index.html",

        context={
            "error": None
        }
    )


# ==========================================
# GENERATE WORKOUT
# ==========================================

@router.post(
    "/generate-workout",
    response_class=HTMLResponse
)
def generate_workout(

    request: Request,

    username: str = Form(...),

    user_id: str = Form(...),

    age: int = Form(...),

    weight: float = Form(...),

    goal: str = Form(...),

    intensity: str = Form(...),

    experience_level: str = Form(
        "beginner"
    ),

    workout_schedule: str = Form(
        "7 days"
    ),

    db: Session = Depends(get_db)
):

    try:

        data = UserInput(

            username=username.strip(),

            user_id=user_id.strip(),

            age=age,

            weight=weight,

            goal=goal.strip(),

            intensity=intensity,

            experience_level=experience_level,

            workout_schedule=workout_schedule
        )


        # Check duplicate User ID

        existing_user = get_user(
            db,
            data.user_id
        )


        if existing_user:

            return templates.TemplateResponse(

                request=request,

                name="index.html",

                context={
                    "error":
                    f"User ID '{data.user_id}' already exists."
                },

                status_code=409
            )


        # Generate workout

        workout_plan = generate_workout_gemini(

            username=data.username,

            age=data.age,

            weight=data.weight,

            goal=data.goal,

            intensity=data.intensity,

            experience_level=data.experience_level,

            workout_schedule=data.workout_schedule
        )


        # Generate nutrition tip

        nutrition_tip = (
            generate_nutrition_tip_with_flash(

                goal=data.goal,

                age=data.age,

                weight=data.weight
            )
        )


        # Save user

        user = save_user(
            db,
            data
        )


        # Save generated plan

        save_plan(

            db,

            user,

            workout_plan,

            nutrition_tip
        )


        return templates.TemplateResponse(

            request=request,

            name="result.html",

            context={

                "user": user,

                "workout_plan":
                workout_plan,

                "nutrition_tip":
                nutrition_tip,

                "message": None
            }
        )


    except Exception as exc:

        return templates.TemplateResponse(

            request=request,

            name="index.html",

            context={
                "error":
                f"Unable to generate plan: {exc}"
            },

            status_code=500
        )


# ==========================================
# SUBMIT FEEDBACK
# ==========================================

@router.post(
    "/submit-feedback",
    response_class=HTMLResponse
)
def submit_feedback(

    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...),

    db: Session = Depends(get_db)
):

    try:

        data = FeedbackRequest(

            user_id=user_id.strip(),

            feedback=feedback.strip()
        )


        user = get_user(

            db,

            data.user_id
        )


        if not user:

            raise HTTPException(

                status_code=404,

                detail="User ID not found."
            )


        # If updated plan exists,
        # use it as the latest plan.

        current_plan = (

            user.updated_plan
            or
            user.original_plan
        )


        # Generate revised plan

        revised_plan = update_workout_plan(

            original_plan=current_plan,

            feedback=data.feedback,

            goal=user.goal,

            intensity=user.intensity,

            experience_level=user.experience_level
        )


        # Save updated plan

        update_plan(

            db,

            user,

            revised_plan,

            data.feedback
        )


        return templates.TemplateResponse(

            request=request,

            name="result.html",

            context={

                "user": user,

                "workout_plan":
                revised_plan,

                "nutrition_tip":
                user.nutrition_tip,

                "message":
                "Your workout plan has been updated successfully."
            }
        )


    except HTTPException:

        raise


    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=f"Unable to update plan: {exc}"
        )


# ==========================================
# ADMIN DASHBOARD
# ==========================================

@router.get(
    "/view-all-users",
    response_class=HTMLResponse
)
def view_all_users(

    request: Request,

    db: Session = Depends(get_db)
):

    users = get_all_users(db)


    return templates.TemplateResponse(

        request=request,

        name="all_users.html",

        context={
            "users": users
        }
    )


# ==========================================
# DELETE USER
# ==========================================

@router.post(
    "/delete-user/{user_id}"
)
def remove_user(

    user_id: str,

    db: Session = Depends(get_db)
):

    delete_user(
        db,
        user_id
    )


    return RedirectResponse(

        url="/view-all-users",

        status_code=303
    )


# ==========================================
# JSON API - ALL USERS
# ==========================================

@router.get(
    "/api/users",
    response_model=list[UserResponse]
)
def api_users(

    db: Session = Depends(get_db)
):

    return get_all_users(db)


# ==========================================
# JSON API - SINGLE USER
# ==========================================

@router.get(
    "/api/users/{user_id}",
    response_model=UserResponse
)
def api_user(

    user_id: str,

    db: Session = Depends(get_db)
):

    user = get_user(
        db,
        user_id
    )


    if not user:

        raise HTTPException(

            status_code=404,

            detail="User not found."
        )


    return user