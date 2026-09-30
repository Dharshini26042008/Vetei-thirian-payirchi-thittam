from pydantic import BaseModel, Field, field_validator


class UserInput(BaseModel):

    username: str = Field(
        min_length=2,
        max_length=100
    )

    user_id: str = Field(
        min_length=2,
        max_length=100
    )

    age: int = Field(
        ge=13,
        le=100
    )

    weight: float = Field(
        gt=20,
        le=500
    )

    goal: str = Field(
        min_length=2,
        max_length=100
    )

    intensity: str

    experience_level: str = "beginner"

    workout_schedule: str = "7 days"

    @field_validator("intensity")
    @classmethod
    def validate_intensity(cls, value):

        value = value.strip().lower()

        allowed = {
            "low",
            "medium",
            "high"
        }

        if value not in allowed:

            raise ValueError(
                "Intensity must be low, medium, or high."
            )

        return value


class FeedbackRequest(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=100
    )

    feedback: str = Field(
        min_length=3,
        max_length=2000
    )


class UserResponse(BaseModel):

    user_id: str

    username: str

    age: int

    weight: float

    goal: str

    intensity: str

    original_plan: str

    updated_plan: str | None = None

    nutrition_tip: str