from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    Integer,
    String,
    Text
)

from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True
    )

    username: Mapped[str] = mapped_column(
        String(100)
    )

    age: Mapped[int] = mapped_column(
        Integer
    )

    weight: Mapped[float] = mapped_column(
        Float
    )

    goal: Mapped[str] = mapped_column(
        String(100)
    )

    intensity: Mapped[str] = mapped_column(
        String(30)
    )

    experience_level: Mapped[str] = mapped_column(
        String(50),
        default="beginner"
    )

    workout_schedule: Mapped[str] = mapped_column(
        String(100),
        default="7 days"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    original_plan: Mapped[str] = mapped_column(
        Text,
        default=""
    )

    updated_plan: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    nutrition_tip: Mapped[str] = mapped_column(
        Text,
        default=""
    )

    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )


def save_user(db, data):

    user = User(
        user_id=data.user_id,
        username=data.username,
        age=data.age,
        weight=data.weight,
        goal=data.goal,
        intensity=data.intensity,
        experience_level=data.experience_level,
        workout_schedule=data.workout_schedule
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return user


def save_plan(
    db,
    user,
    workout_plan,
    nutrition_tip
):

    user.original_plan = workout_plan

    user.nutrition_tip = nutrition_tip

    db.commit()

    db.refresh(user)

    return user


def update_plan(
    db,
    user,
    updated_plan,
    feedback
):

    user.updated_plan = updated_plan

    user.feedback = feedback

    db.commit()

    db.refresh(user)

    return user


def get_user(
    db,
    user_id
):

    return (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )


def get_all_users(db):

    return (
        db.query(User)
        .order_by(User.created_at.desc())
        .all()
    )


def delete_user(
    db,
    user_id
):

    user = get_user(
        db,
        user_id
    )

    if not user:
        return False

    db.delete(user)

    db.commit()

    return True