from __future__ import annotations

from app.application.dto.requests import LoginRequest
from app.domain.enums import Role
from app.domain.exceptions import AppException, InputCancelled
from app.presentation.cli.display import show_app_exception, show_success
from app.presentation.cli.input import pause, read_choice, read_required_text
from app.presentation.cli.menus.manager_menu import ManagerMenu
from app.presentation.cli.menus.trainee_menu import TraineeMenu
from app.presentation.cli.menus.trainer_menu import TrainerMenu
from app.presentation.cli.session import Session


ROLE_LABELS = {
    Role.COURSE_MANAGER: "مدير دورة",
    Role.TRAINER: "مدرب",
    Role.TRAINEE: "متدرب",
}


class CLIApp:
    """Presentation boundary for the TCMS terminal application."""

    def __init__(self, session: Session, container) -> None:
        self.session = session
        self.container = container
        self.manager_menu = ManagerMenu(self)
        self.trainer_menu = TrainerMenu(self)
        self.trainee_menu = TraineeMenu(self)

    def run(self) -> None:
        print("=" * 64)
        print("        نظام إدارة الدورات التدريبية — TCMS V2")
        print("=" * 64)
        try:
            while True:
                if not self.session.is_authenticated:
                    if not self._login_loop():
                        return
                self._dispatch_role_menu()
        except InputCancelled:
            self.logout(silent=True)
            print("\nتم إغلاق النظام بأمان.")

    def _login_loop(self) -> bool:
        print("\n===== تسجيل الدخول =====")
        choice = read_choice(
            "1. تسجيل الدخول\n0. خروج\nاختر: ",
            ["1", "0"],
        )
        if choice == "0":
            return False

        username = read_required_text("اسم المستخدم: ")
        password = read_required_text("كلمة المرور: ")
        try:
            user = self.container.login.execute(
                LoginRequest(username=username, password=password)
            )
            self.session.start(user)
            show_success(
                f"تم تسجيل الدخول بنجاح. مرحبًا {user.username} — "
                f"الدور: {ROLE_LABELS.get(user.role, str(user.role))}."
            )
            return True
        except AppException as exc:
            show_app_exception(exc)
            pause()
            return True
        except Exception:
            self.container.logger.exception("Unexpected error during login")
            print("\n[خطأ] حدث خطأ غير متوقع أثناء تسجيل الدخول. راجع سجل النظام.")
            pause()
            return True

    def _dispatch_role_menu(self) -> None:
        role = self.session.current_user.role
        if role is Role.COURSE_MANAGER:
            self.manager_menu.run()
        elif role is Role.TRAINER:
            self.trainer_menu.run()
        elif role is Role.TRAINEE:
            self.trainee_menu.run()
        else:
            self.container.logger.error("Unsupported session role: %r", role)
            self.session.clear()
            print("\n[خطأ] دور المستخدم غير مدعوم.")

    def logout(self, *, silent: bool = False) -> None:
        self.container.logout.execute()
        self.session.clear()
        if not silent:
            show_success("تم تسجيل الخروج بنجاح.")
