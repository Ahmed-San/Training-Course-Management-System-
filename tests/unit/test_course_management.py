from __future__ import annotations

import pytest

from app.application.use_cases.courses import (
    CreateCourseDTO,
    CreateCourseUseCase,
    ListCoursesUseCase,
    UpdateCourseDTO,
    UpdateCourseUseCase,
    ViewCourseUseCase,
)
from app.domain.entities.course import Course
from app.domain.enums import CourseStatus
from app.domain.exceptions import DuplicateError, NotFoundError, ValidationError
from app.infrastructure.persistence.json_course_repository import JsonCourseRepository


def test_course_entity_valid_creation():
    course = Course(
        id="c-101",
        name="Python Programming",
        total_hours=40,
        description="Learn core Python concepts.",
        order_index=1,
        manager_id="mgr-1",
    )
    assert course.id == "c-101"
    assert course.name == "Python Programming"
    assert course.total_hours == 40
    assert course.description == "Learn core Python concepts."
    assert course.order_index == 1
    assert course.manager_id == "mgr-1"


def test_course_entity_invalid_fields():
    with pytest.raises(ValidationError):
        Course(id="", name="Python", total_hours=40, description="Desc", order_index=1, manager_id="mgr-1")

    with pytest.raises(ValidationError):
        Course(id="c-1", name="   ", total_hours=40, description="Desc", order_index=1, manager_id="mgr-1")

    with pytest.raises(ValidationError):
        Course(id="c-1", name="Python", total_hours=0, description="Desc", order_index=1, manager_id="mgr-1")

    with pytest.raises(ValidationError):
        Course(id="c-1", name="Python", total_hours=-10, description="Desc", order_index=1, manager_id="mgr-1")

    with pytest.raises(ValidationError):
        Course(id="c-1", name="Python", total_hours=40, description="   ", order_index=1, manager_id="mgr-1")

    with pytest.raises(ValidationError):
        Course(id="c-1", name="Python", total_hours=40, description="Desc", order_index=0, manager_id="mgr-1")

    with pytest.raises(ValidationError):
        Course(id="c-1", name="Python", total_hours=40, description="Desc", order_index=1, manager_id="")


def test_course_derived_progress_and_status():
    course = Course(
        id="c-101",
        name="Data Science",
        total_hours=30,
        description="Intro to Data Science",
        order_index=1,
        manager_id="mgr-1",
    )

    # NOT_STARTED
    assert course.calculate_remaining_hours(0) == 30
    assert course.is_completed(0) is False
    assert course.get_status(0) == CourseStatus.NOT_STARTED

    # IN_PROGRESS
    assert course.calculate_remaining_hours(15) == 15
    assert course.is_completed(15) is False
    assert course.get_status(15) == CourseStatus.IN_PROGRESS

    # COMPLETED
    assert course.calculate_remaining_hours(30) == 0
    assert course.is_completed(30) is True
    assert course.get_status(30) == CourseStatus.COMPLETED

    # Over-completed remains 0 remaining
    assert course.calculate_remaining_hours(35) == 0
    assert course.is_completed(35) is True
    assert course.get_status(35) == CourseStatus.COMPLETED

    # Invalid completed_hours
    with pytest.raises(ValidationError):
        course.calculate_remaining_hours(-1)

    with pytest.raises(ValidationError):
        course.is_completed(-5)

    with pytest.raises(ValidationError):
        course.get_status(-10)


def test_json_course_repository_crud_and_query():
    state = {"courses": []}
    repo = JsonCourseRepository(state=state)

    c1 = Course(id="c-1", name="Course 1", total_hours=20, description="Desc 1", order_index=1, manager_id="m-1")
    c2 = Course(id="c-2", name="Course 2", total_hours=30, description="Desc 2", order_index=2, manager_id="m-1")
    c3 = Course(id="c-3", name="Course 3", total_hours=40, description="Desc 3", order_index=3, manager_id="m-2")

    repo.add(c1)
    repo.add(c2)
    repo.add(c3)

    assert repo.count() == 3
    assert repo.get_by_id("c-1") == c1

    # Duplicate error
    with pytest.raises(DuplicateError):
        repo.add(c1)

    # get_by_manager
    m1_courses = repo.get_by_manager("m-1")
    assert len(m1_courses) == 2
    assert {c.id for c in m1_courses} == {"c-1", "c-2"}

    m2_courses = repo.get_by_manager("m-2")
    assert len(m2_courses) == 1
    assert m2_courses[0].id == "c-3"

    # Update
    updated_c1 = Course(id="c-1", name="Course 1 Updated", total_hours=25, description="Desc 1", order_index=1, manager_id="m-1")
    repo.update(updated_c1)
    assert repo.get_by_id("c-1").name == "Course 1 Updated"

    # Delete
    repo.delete("c-2")
    assert repo.count() == 2
    assert repo.get_by_id("c-2") is None


def test_course_use_cases():
    state = {"courses": []}
    repo = JsonCourseRepository(state=state)

    create_uc = CreateCourseUseCase(repo)
    update_uc = UpdateCourseUseCase(repo)
    view_uc = ViewCourseUseCase(repo)
    list_uc = ListCoursesUseCase(repo)

    # Create
    dto = CreateCourseDTO(
        id="c-100",
        name="Software Architecture",
        total_hours=50,
        description="Advanced topics",
        order_index=1,
        manager_id="mgr-10",
    )
    created = create_uc.execute(dto)
    assert created.id == "c-100"

    # View
    viewed = view_uc.execute("c-100")
    assert viewed == created

    # Update
    update_dto = UpdateCourseDTO(id="c-100", total_hours=60, description="Updated desc")
    updated = update_uc.execute(update_dto)
    assert updated.total_hours == 60
    assert updated.description == "Updated desc"
    assert updated.name == "Software Architecture"

    # List
    all_courses = list_uc.execute()
    assert len(all_courses) == 1

    by_mgr = list_uc.execute("mgr-10")
    assert len(by_mgr) == 1

    empty_mgr = list_uc.execute("mgr-99")
    assert len(empty_mgr) == 0


def test_course_scenario_13_lifecycle():
    """Scenario 13:
    Create C001=10 hours -> view/update C001 -> manager query returns correct courses ->
    validate 0h/5h/10h progress states -> compile and full suite.
    """
    state = {"courses": []}
    repo = JsonCourseRepository(state=state)

    create_uc = CreateCourseUseCase(repo)
    update_uc = UpdateCourseUseCase(repo)
    view_uc = ViewCourseUseCase(repo)
    list_uc = ListCoursesUseCase(repo)

    # 1. Create C001 = 10 hours
    create_req = CreateCourseDTO(
        id="C001",
        name="Intro to Programming",
        total_hours=10,
        description="Foundational coding course",
        order_index=1,
        manager_id="MGR-01",
    )
    course = create_uc.execute(create_req)
    assert course.id == "C001"
    assert course.total_hours == 10

    # 2. View C001
    viewed = view_uc.execute("C001")
    assert viewed.id == "C001"
    assert viewed.name == "Intro to Programming"

    # 3. Update C001
    update_req = UpdateCourseDTO(
        id="C001",
        name="Intro to Python Programming",
        description="Updated foundational course",
    )
    updated = update_uc.execute(update_req)
    assert updated.name == "Intro to Python Programming"
    assert updated.description == "Updated foundational course"
    assert updated.total_hours == 10

    # 4. Manager query returns correct courses
    mgr_courses = list_uc.execute("MGR-01")
    assert len(mgr_courses) == 1
    assert mgr_courses[0].id == "C001"

    other_mgr_courses = list_uc.execute("MGR-99")
    assert len(other_mgr_courses) == 0

    # 5. Validate 0h / 5h / 10h progress states
    # 0h: NOT_STARTED
    assert updated.calculate_remaining_hours(0) == 10
    assert updated.is_completed(0) is False
    assert updated.get_status(0) == CourseStatus.NOT_STARTED

    # 5h: IN_PROGRESS
    assert updated.calculate_remaining_hours(5) == 5
    assert updated.is_completed(5) is False
    assert updated.get_status(5) == CourseStatus.IN_PROGRESS

    # 10h: COMPLETED
    assert updated.calculate_remaining_hours(10) == 0
    assert updated.is_completed(10) is True
    assert updated.get_status(10) == CourseStatus.COMPLETED

