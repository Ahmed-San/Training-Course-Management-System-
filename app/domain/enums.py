from __future__ import annotations

from enum import StrEnum


class Category(StrEnum):
    A = "A"
    B = "B"
    C = "C"


class TrainingMethod(StrEnum):
    ONSITE = "onsite"
    REMOTE = "remote"
    ADMINISTRATIVE = "administrative"


class CourseStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class EnrollmentStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"


class Grade(StrEnum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class Role(StrEnum):
    COURSE_MANAGER = "course_manager"
    TRAINER = "trainer"
    TRAINEE = "trainee"


class Permission(StrEnum):
    VIEW_COURSE = "view_course"
    EDIT_COURSE = "edit_course"
    VIEW_TRAINEE = "view_trainee"
    EDIT_TRAINEE = "edit_trainee"
    VIEW_REPORT = "view_report"
    MANAGE_REPORT = "manage_report"
    VIEW_EVALUATION = "view_evaluation"
    MANAGE_EVALUATION = "manage_evaluation"
    ASSIGN_TRAINER = "assign_trainer"
    ASSIGN_TRAINEE = "assign_trainee"
    MANAGE_ENROLLMENT = "manage_enrollment"
