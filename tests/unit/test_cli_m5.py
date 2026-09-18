from __future__ import annotations

from types import SimpleNamespace

from app.domain.enums import Role
from app.presentation.cli.app import CLIApp
from app.presentation.cli.session import Session


class FakeLogin:
    def __init__(self, user):
        self.user = user

    def execute(self, request):
        return self.user


class FakeLogout:
    def execute(self):
        return None


class FakeLogger:
    def exception(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


def test_login_screen_is_arabic(monkeypatch, capsys):
    user = SimpleNamespace(username="manager", role=Role.COURSE_MANAGER)
    container = SimpleNamespace(
        login=FakeLogin(user),
        logout=FakeLogout(),
        logger=FakeLogger(),
    )
    app = CLIApp(Session(), container)
    answers = iter(["1", "manager", "manager123"])
    monkeypatch.setattr("builtins.input", lambda prompt="": (print(prompt, end=""), next(answers))[1])

    assert app._login_loop() is True
    output = capsys.readouterr().out
    assert "تسجيل الدخول" in output
    assert "اسم المستخدم" in output
    assert "كلمة المرور" in output
    assert "تم تسجيل الدخول بنجاح" in output
    assert "Manager Menu" not in output


def test_role_labels_are_arabic():
    user = SimpleNamespace(username="trainer", role=Role.TRAINER)
    container = SimpleNamespace(login=FakeLogin(user), logout=FakeLogout(), logger=FakeLogger())
    app = CLIApp(Session(), container)
    app.session.start(user)
    assert app.session.is_authenticated

from app.presentation.cli.menus.manager_menu import ManagerMenu
from app.presentation.cli.menus.trainer_menu import TrainerMenu
from app.presentation.cli.menus.trainee_menu import TraineeMenu


def _menu_app(user):
    session = Session()

    class Logout:
        def __init__(self):
            self.called = False

        def execute(self):
            self.called = True
            session.clear()

    logout = Logout()
    container = SimpleNamespace(
        logout=logout,
        logger=FakeLogger(),
    )
    app = SimpleNamespace(session=session, container=container, logout=lambda: (logout.execute()))
    session.start(user)
    return app


def test_manager_menu_is_arabic(monkeypatch, capsys):
    user = SimpleNamespace(username="manager", role=Role.COURSE_MANAGER)
    app = _menu_app(user)
    monkeypatch.setattr("builtins.input", lambda prompt="": "8")
    ManagerMenu(app).run()
    output = capsys.readouterr().out
    assert "قائمة مدير الدورة" in output
    assert "التقييمات" in output
    assert "تسجيل الخروج" in output
    assert "Manager Menu" not in output


def test_trainer_menu_is_arabic(monkeypatch, capsys):
    user = SimpleNamespace(username="trainer", role=Role.TRAINER, profile_id="TR001")
    app = _menu_app(user)
    monkeypatch.setattr("builtins.input", lambda prompt="": "6")
    TrainerMenu(app).run()
    output = capsys.readouterr().out
    assert "قائمة المدرب" in output
    assert "التقييمات" in output
    assert "تسجيل الخروج" in output
    assert "Trainer Menu" not in output


def test_trainee_menu_is_arabic(monkeypatch, capsys):
    user = SimpleNamespace(username="trainee", role=Role.TRAINEE, profile_id="T001")
    app = _menu_app(user)
    monkeypatch.setattr("builtins.input", lambda prompt="": "5")
    TraineeMenu(app).run()
    output = capsys.readouterr().out
    assert "قائمة المتدرب" in output
    assert "التقييمات" in output
    assert "تسجيل الخروج" in output
    assert "Trainee Menu" not in output
