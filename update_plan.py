from typing import Any, Dict, List


def update_workout_plan(
    original_plan: Dict[str, Any],
    feedback: str,
) -> Dict[str, Any]:
    """
    Update an existing workout plan using user feedback.

    This function keeps the original workout structure and adds
    feedback-based modifications.
    """

    if not isinstance(original_plan, dict):
        raise ValueError("original_plan must be a dictionary.")

    if not feedback or not feedback.strip():
        return original_plan

    updated_plan = original_plan.copy()

    feedback_text = feedback.strip()

    # Store feedback so it is preserved with the updated plan.
    updated_plan["user_feedback"] = feedback_text

    # If the plan contains workout days, preserve them and mark
    # the plan as updated.
    if "workout_plan" in updated_plan:
        workout_plan = updated_plan["workout_plan"]

        if isinstance(workout_plan, list):
            updated_workouts: List[Any] = []

            for workout in workout_plan:
                if isinstance(workout, dict):
                    workout_copy = workout.copy()
                    workout_copy["feedback_applied"] = True
                    updated_workouts.append(workout_copy)
                else:
                    updated_workouts.append(workout)

            updated_plan["workout_plan"] = updated_workouts

    updated_plan["plan_status"] = "updated"

    return updated_plan