from __future__ import annotations

from app.application.dto.requests import (
    CreateDailyReportRequest,
    CreateEvaluationRequest,
    UpdateDailyReportRequest,
    UpdateEvaluationRequest,
)
from app.domain.enums import Grade
from app.domain.exceptions import AppException
from app.presentation.cli.display import show_app_exception, show_course_progress, show_entity, show_list, show_success
from app.presentation.cli.input import pause, read_choice, read_date, read_int, read_optional_text, read_required_text
from app.presentation.cli.menus.common_menu import CommonMenu


class TrainerMenu(CommonMenu):
    def run(self) -> None:
        while self.app.session.is_authenticated:
            print("\n===== قائمة المدرب =====")
            print("1. دوراتي")
            print("2. المتدربون المسندون إليّ")
            print("3. التقارير اليومية")
            print("4. التقييمات")
            print("5. تفاصيل دورة")
            print("6. تسجيل الخروج")
            choice = read_choice("اختر رقم العملية: ", ["1", "2", "3", "4", "5", "6"])
            try:
                if choice == "1":
                    show_list(self.app.container.list_courses.execute(self.app.session.current_user))
                    pause()
                elif choice == "2":
                    self.my_trainees()
                elif choice == "3":
                    self.reports()
                elif choice == "4":
                    self.evaluations()
                elif choice == "5":
                    self.view_course()
                else:
                    self.app.logout()
            except AppException as exc:
                show_app_exception(exc)
                pause()
            except Exception:
                self.app.container.logger.exception("Unexpected error in trainer menu")
                print("\n[خطأ] حدث خطأ غير متوقع. راجع سجل النظام.")
                pause()

    def my_trainees(self) -> None:
        course_id = read_required_text("معرّف الدورة: ")
        assignments = self.app.container.list_trainer_trainees.execute(
            self.app.session.current_user, course_id
        )
        show_list(assignments)
        pause()

    def reports(self) -> None:
        c = self.app.container
        choice = read_choice(
            "\nالتقارير اليومية:\n1. عرض التقارير\n2. إنشاء تقرير\n3. تحديث تقرير\n4. حذف تقرير\nاختر: ",
            ["1", "2", "3", "4"],
        )
        if choice == "1":
            show_list(
                c.list_reports.execute(
                    self.app.session.current_user,
                    course_id=read_optional_text("معرّف الدورة (Enter=الكل): "),
                )
            )
        elif choice == "2":
            report, progress = c.create_report.execute(
                CreateDailyReportRequest(
                    read_required_text("معرّف الدورة: "),
                    read_date("التاريخ YYYY-MM-DD: "),
                    read_int("الساعات: ", min_value=1),
                    read_optional_text("الملاحظة: ") or "",
                ),
                self.app.session.current_user,
            )
            show_entity(report)
            show_course_progress(progress)
        elif choice == "3":
            report_id = read_required_text("معرّف التقرير: ")
            hours_raw = read_optional_text("الساعات الجديدة (Enter=الإبقاء): ")
            note = read_optional_text("الملاحظة الجديدة (Enter=الإبقاء): ")
            report, progress = c.update_report.execute(
                UpdateDailyReportRequest(
                    report_id,
                    hours_done=int(hours_raw) if hours_raw else None,
                    note=note,
                ),
                self.app.session.current_user,
            )
            show_entity(report)
            show_course_progress(progress)
        else:
            c.delete_report.execute(
                read_required_text("معرّف التقرير: "), self.app.session.current_user
            )
            show_success("تم حذف التقرير بنجاح.")
        pause()

    def evaluations(self) -> None:
        c = self.app.container
        choice = read_choice(
            "\n===== التقييمات =====\n"
            "1. عرض قائمة التقييمات\n"
            "2. عرض تقييم\n"
            "3. إنشاء تقييم\n"
            "4. تعديل تقييم\n"
            "اختر: ",
            ["1", "2", "3", "4"],
        )
        if choice == "1":
            show_list(c.list_evaluations.execute(self.app.session.current_user))
        elif choice == "2":
            self.view_evaluation()
            return
        elif choice == "3":
            result = c.create_evaluation.execute(
                CreateEvaluationRequest(
                    read_required_text("معرّف التسجيل: "),
                    Grade(read_choice("الدرجة [A/B/C/D]: ", ["A", "B", "C", "D"])),
                ),
                self.app.session.current_user,
            )
            show_entity(result)
            show_success("تم إنشاء التقييم بنجاح.")
        else:
            result = c.update_evaluation.execute(
                UpdateEvaluationRequest(
                    read_required_text("معرّف التقييم: "),
                    Grade(read_choice("الدرجة الجديدة [A/B/C/D]: ", ["A", "B", "C", "D"])),
                ),
                self.app.session.current_user,
            )
            show_entity(result)
            show_success("تم تحديث التقييم بنجاح.")
        pause()
