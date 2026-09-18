from __future__ import annotations

from datetime import date
from pathlib import Path
import json
import pytest

from app.bootstrap import create_container
from app.application.dto.requests import *
from app.domain.enums import Category, Grade, TrainingMethod, EnrollmentStatus, CourseStatus, Role
from app.domain.entities.user import User
from app.domain.exceptions import AuthorizationError, BusinessRuleError, ValidationError


def app(tmp_path: Path):
    container = create_container(tmp_path, seed_demo=False)
    with container.new_unit_of_work() as uow:
        uow.user_repository.add(
            User("U001", "manager", container.password_hasher.hash("manager123"), Role.COURSE_MANAGER)
        )
        uow.user_repository.add(
            User("U002", "trainer", container.password_hasher.hash("trainer123"), Role.TRAINER, "TR001")
        )
        uow.user_repository.add(
            User("U003", "trainee", container.password_hasher.hash("trainee123"), Role.TRAINEE, "T001")
        )
    return container

def manager(c):
    return c.login.execute(LoginRequest("manager","manager123"))

def trainer(c):
    return c.login.execute(LoginRequest("trainer","trainer123"))

def trainee(c):
    return c.login.execute(LoginRequest("trainee","trainee123"))


def seed_core(c):
    m=manager(c)
    c.create_trainer.execute(CreateTrainerRequest("TR001","Trainer",30,"777111111","tr@example.com",Category.A,TrainingMethod.ONSITE),m)
    c.create_trainee.execute(CreateTraineeRequest("T001","Trainee",20,"777222222","t@example.com",Category.A),m)
    c.create_course.execute(CreateCourseRequest("C001","Python Course",10,"Testing",1,m.id),m)
    c.assign_trainer_to_course.execute(AssignTrainerRequest("C001","TR001"),m)
    c.assign_trainer_to_trainee.execute(AssignTraineeRequest("C001","TR001","T001"),m)
    en=c.enroll_trainee.execute(EnrollTraineeRequest("T001","C001"),m)
    return m,en


def test_enrollment_and_duplicate_active(tmp_path):
    c=app(tmp_path); m,en=seed_core(c)
    with pytest.raises(BusinessRuleError): c.enroll_trainee.execute(EnrollTraineeRequest("T001","C001"),m)


def test_report_progress_and_reject_oversized(tmp_path):
    c=app(tmp_path); m,en=seed_core(c); tr=trainer(c)
    report,progress=c.create_report.execute(CreateDailyReportRequest("C001",date(2026,9,18),5,"half"),tr)
    assert progress.remaining_hours==5
    with pytest.raises(BusinessRuleError): c.create_report.execute(CreateDailyReportRequest("C001",date(2026,9,19),6,"too much"),tr)


def test_completion_auto_completes_enrollment(tmp_path):
    c=app(tmp_path); m,en=seed_core(c); tr=trainer(c)
    c.create_report.execute(CreateDailyReportRequest("C001",date(2026,9,18),5,"a"),tr)
    _,progress=c.create_report.execute(CreateDailyReportRequest("C001",date(2026,9,19),5,"b"),tr)
    assert progress.status is CourseStatus.COMPLETED
    stored=c.view_enrollment.execute(en.id,m)
    assert stored.status is EnrollmentStatus.COMPLETED


def test_evaluation_lifecycle_and_trainee_visibility(tmp_path):
    c=app(tmp_path); m,en=seed_core(c); tr=trainer(c); te=trainee(c)
    ev=c.create_evaluation.execute(CreateEvaluationRequest(en.id,Grade.A),tr)
    assert c.view_evaluation.execute(tr,evaluation_id=ev.id).grade is Grade.A
    with pytest.raises(AuthorizationError): c.view_evaluation.execute(te,evaluation_id=ev.id)
    c.create_report.execute(CreateDailyReportRequest("C001",date(2026,9,18),10,"done"),tr)
    with pytest.raises(AuthorizationError): c.update_evaluation.execute(UpdateEvaluationRequest(ev.id,Grade.B),tr)
    updated=c.update_evaluation.execute(UpdateEvaluationRequest(ev.id,Grade.C),m)
    assert updated.grade is Grade.C
    assert c.view_evaluation.execute(te,evaluation_id=ev.id).grade is Grade.C


def test_remote_trainer_cannot_mutate_report(tmp_path):
    c=app(tmp_path); m,en=seed_core(c)
    # Replace trainer profile with a remote method using manager-authorized update.
    c.update_trainer.execute("TR001",m,training_method=TrainingMethod.REMOTE)
    tr=trainer(c)
    with pytest.raises(AuthorizationError): c.create_report.execute(CreateDailyReportRequest("C001",date(2026,9,18),1,"x"),tr)


def test_rollback_keeps_json_unchanged(tmp_path):
    c=app(tmp_path); m=manager(c)
    db=c.database
    before=json.loads(db.path.read_text(encoding="utf-8"))
    from app.infrastructure.persistence.json_unit_of_work import JsonUnitOfWork
    from app.domain.entities.course import Course
    with pytest.raises(RuntimeError):
        with JsonUnitOfWork(db) as uow:
            uow.course_repository.add(Course("C999","Transient",3,"x",1,m.id))
            raise RuntimeError("forced")
    after=json.loads(db.path.read_text(encoding="utf-8"))
    assert before==after


def add_user(c, *, user_id, username, role, profile_id=None, password=None):
    from app.domain.entities.user import User
    password = password or f"{username}123"
    with c.new_unit_of_work() as uow:
        uow.user_repository.add(
            User(
                id=user_id,
                username=username,
                password_hash=c.password_hasher.hash(password),
                role=role,
                profile_id=profile_id,
            )
        )
    return c.login.execute(LoginRequest(username, password))


def add_trainer(c, manager_user, *, trainer_id, user_id, username, method=TrainingMethod.ONSITE):
    c.create_trainer.execute(
        CreateTrainerRequest(
            trainer_id, username, 35, "777333333", f"{username}@example.com",
            Category.A, method,
        ),
        manager_user,
    )
    return add_user(
        c,
        user_id=user_id,
        username=username,
        role=Role.TRAINER,
        profile_id=trainer_id,
    )


def add_trainee(c, manager_user, *, trainee_id, user_id, username):
    c.create_trainee.execute(
        CreateTraineeRequest(
            trainee_id, username, 25, "777444444", f"{username}@example.com", Category.A
        ),
        manager_user,
    )
    return add_user(
        c,
        user_id=user_id,
        username=username,
        role=Role.TRAINEE,
        profile_id=trainee_id,
    )


def test_m5_remote_trainer_rejected_from_evaluation_mutation(tmp_path):
    c = app(tmp_path)
    m, en = seed_core(c)
    c.update_trainer.execute("TR001", m, training_method=TrainingMethod.REMOTE)
    tr = trainer(c)
    with pytest.raises(AuthorizationError):
        c.create_evaluation.execute(CreateEvaluationRequest(en.id, Grade.A), tr)


def test_m5_trainer_outside_scope_rejected(tmp_path):
    c = app(tmp_path)
    m, en = seed_core(c)
    tr2 = add_trainer(c, m, trainer_id="TR002", user_id="U004", username="trainer2")
    with pytest.raises(AuthorizationError):
        c.create_evaluation.execute(CreateEvaluationRequest(en.id, Grade.A), tr2)


def test_m5_create_for_completed_enrollment_rejected(tmp_path):
    c = app(tmp_path)
    m, en = seed_core(c)
    tr = trainer(c)
    c.create_report.execute(CreateDailyReportRequest("C001", date(2026, 9, 18), 10, "done"), tr)
    with pytest.raises(BusinessRuleError):
        c.create_evaluation.execute(CreateEvaluationRequest(en.id, Grade.A), tr)


def test_m5_trainer_update_before_completion_and_lock_after(tmp_path):
    c = app(tmp_path)
    m, en = seed_core(c)
    tr = trainer(c)
    ev = c.create_evaluation.execute(CreateEvaluationRequest(en.id, Grade.A), tr)
    changed = c.update_evaluation.execute(UpdateEvaluationRequest(ev.id, Grade.B), tr)
    assert changed.grade is Grade.B
    c.create_report.execute(CreateDailyReportRequest("C001", date(2026, 9, 18), 10, "done"), tr)
    with pytest.raises(AuthorizationError):
        c.update_evaluation.execute(UpdateEvaluationRequest(ev.id, Grade.C), tr)


def test_m5_manager_correction_inside_scope_succeeds(tmp_path):
    c = app(tmp_path)
    m, en = seed_core(c)
    tr = trainer(c)
    ev = c.create_evaluation.execute(CreateEvaluationRequest(en.id, Grade.A), tr)
    updated = c.update_evaluation.execute(UpdateEvaluationRequest(ev.id, Grade.C), m)
    assert updated.grade is Grade.C


def test_m5_manager_outside_scope_rejected_and_list_is_scoped(tmp_path):
    c = app(tmp_path)
    m1, en1 = seed_core(c)
    tr1 = trainer(c)
    ev1 = c.create_evaluation.execute(CreateEvaluationRequest(en1.id, Grade.A), tr1)

    m2 = add_user(
        c, user_id="U005", username="manager2", role=Role.COURSE_MANAGER
    )
    tr2 = add_trainer(c, m2, trainer_id="TR002", user_id="U006", username="trainer2")
    t2 = add_trainee(c, m2, trainee_id="T002", user_id="U007", username="trainee2")
    c.create_course.execute(
        CreateCourseRequest("C002", "Second Course", 5, "Second", 2, m2.id), m2
    )
    c.assign_trainer_to_course.execute(AssignTrainerRequest("C002", "TR002"), m2)
    c.assign_trainer_to_trainee.execute(AssignTraineeRequest("C002", "TR002", "T002"), m2)
    en2 = c.enroll_trainee.execute(EnrollTraineeRequest("T002", "C002"), m2)
    ev2 = c.create_evaluation.execute(CreateEvaluationRequest(en2.id, Grade.B), tr2)

    with pytest.raises(AuthorizationError):
        c.update_evaluation.execute(UpdateEvaluationRequest(ev2.id, Grade.D), m1)

    assert [e.id for e in c.list_evaluations.execute(m1)] == [ev1.id]
    assert [e.id for e in c.list_evaluations.execute(m2)] == [ev2.id]


def test_m5_manager_view_is_scoped_to_managed_course(tmp_path):
    c = app(tmp_path)
    m1, en1 = seed_core(c)
    tr1 = trainer(c)
    ev1 = c.create_evaluation.execute(CreateEvaluationRequest(en1.id, Grade.A), tr1)
    m2 = add_user(c, user_id="U005", username="manager2", role=Role.COURSE_MANAGER)
    with pytest.raises(AuthorizationError):
        c.view_evaluation.execute(m2, evaluation_id=ev1.id)


def test_m5_trainee_visibility_and_cross_trainee_isolation(tmp_path):
    c = app(tmp_path)
    m, en = seed_core(c)
    tr = trainer(c)
    t1 = trainee(c)
    ev = c.create_evaluation.execute(CreateEvaluationRequest(en.id, Grade.A), tr)

    with pytest.raises(AuthorizationError):
        c.view_evaluation.execute(t1, evaluation_id=ev.id)

    t2 = add_trainee(c, m, trainee_id="T002", user_id="U004", username="trainee2")
    with pytest.raises(AuthorizationError):
        c.view_evaluation.execute(t2, evaluation_id=ev.id)

    c.create_report.execute(CreateDailyReportRequest("C001", date(2026, 9, 18), 10, "done"), tr)
    visible = c.view_evaluation.execute(t1, enrollment_id=en.id)
    assert visible is not None
    assert visible.id == ev.id
    assert [item.id for item in c.list_evaluations.execute(t1)] == [ev.id]


def test_m5_successful_evaluation_is_persisted(tmp_path):
    c = app(tmp_path)
    m, en = seed_core(c)
    tr = trainer(c)
    ev = c.create_evaluation.execute(CreateEvaluationRequest(en.id, Grade.A), tr)
    state = json.loads(c.database.path.read_text(encoding="utf-8"))
    assert any(item["id"] == ev.id and item["grade"] == "A" for item in state["evaluations"])


def test_m5_failed_update_does_not_change_json(tmp_path):
    c = app(tmp_path)
    m, en = seed_core(c)
    tr = trainer(c)
    ev = c.create_evaluation.execute(CreateEvaluationRequest(en.id, Grade.A), tr)
    before = json.loads(c.database.path.read_text(encoding="utf-8"))
    with pytest.raises(ValidationError):
        c.update_evaluation.execute(UpdateEvaluationRequest(ev.id, "Z"), tr)
    after = json.loads(c.database.path.read_text(encoding="utf-8"))
    assert after == before
