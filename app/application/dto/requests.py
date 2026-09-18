from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.domain.enums import Category, Grade, TrainingMethod


@dataclass(frozen=True, slots=True)
class LoginRequest:
    username: str
    password: str

@dataclass(frozen=True, slots=True)
class CreateTraineeRequest:
    id: str
    name: str
    age: int
    phone: str
    email: str
    category: Category

@dataclass(frozen=True, slots=True)
class CreateTrainerRequest:
    id: str
    name: str
    age: int
    phone: str
    email: str
    category: Category
    training_method: TrainingMethod

@dataclass(frozen=True, slots=True)
class CreateCourseRequest:
    id: str
    name: str
    total_hours: int
    description: str
    order_index: int
    manager_id: str

@dataclass(frozen=True, slots=True)
class EnrollTraineeRequest:
    trainee_id: str
    course_id: str

@dataclass(frozen=True, slots=True)
class AssignTrainerRequest:
    course_id: str
    trainer_id: str

@dataclass(frozen=True, slots=True)
class AssignTraineeRequest:
    course_id: str
    trainer_id: str
    trainee_id: str

@dataclass(frozen=True, slots=True)
class CreateDailyReportRequest:
    course_id: str
    report_date: date
    hours_done: int
    note: str

@dataclass(frozen=True, slots=True)
class UpdateDailyReportRequest:
    report_id: str
    report_date: date | None = None
    hours_done: int | None = None
    note: str | None = None

@dataclass(frozen=True, slots=True)
class CreateEvaluationRequest:
    enrollment_id: str
    grade: Grade

@dataclass(frozen=True, slots=True)
class UpdateEvaluationRequest:
    evaluation_id: str
    grade: Grade
