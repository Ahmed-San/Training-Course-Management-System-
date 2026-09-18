from __future__ import annotations

from app.domain.exceptions import AppException
from app.presentation.cli.display import show_app_exception, show_list
from app.presentation.cli.input import pause, read_choice
from app.presentation.cli.menus.common_menu import CommonMenu


class TraineeMenu(CommonMenu):
    def run(self) -> None:
        while self.app.session.is_authenticated:
            print("\n===== قائمة المتدرب =====")
            print("1. دوراتي الحالية")
            print("2. تفاصيل دورة")
            print("3. التقارير اليومية")
            print("4. التقييمات")
            print("5. تسجيل الخروج")
            choice = read_choice("اختر رقم العملية: ", ["1", "2", "3", "4", "5"])
            try:
                if choice == "1":
                    show_list(
                        self.app.container.list_enrollments.execute(
                            self.app.session.current_user
                        )
                    )
                    pause()
                elif choice == "2":
                    self.view_course()
                elif choice == "3":
                    show_list(
                        self.app.container.list_reports.execute(
                            self.app.session.current_user
                        )
                    )
                    pause()
                elif choice == "4":
                    self.evaluations()
                else:
                    self.app.logout()
            except AppException as exc:
                show_app_exception(exc)
                pause()
            except Exception:
                self.app.container.logger.exception("Unexpected error in trainee menu")
                print("\n[خطأ] حدث خطأ غير متوقع. راجع سجل النظام.")
                pause()

    def evaluations(self) -> None:
        choice = read_choice(
            "\n===== التقييمات =====\n"
            "1. عرض تقييماتي\n"
            "2. عرض تقييم محدد\n"
            "اختر: ",
            ["1", "2"],
        )
        if choice == "1":
            evaluations = self.app.container.list_evaluations.execute(
                self.app.session.current_user
            )
            show_list(evaluations)
            pause()
        else:
            self.view_evaluation()
