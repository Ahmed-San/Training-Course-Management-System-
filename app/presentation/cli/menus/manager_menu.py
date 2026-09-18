from __future__ import annotations

from app.application.dto.requests import (
    AssignTraineeRequest,
    AssignTrainerRequest,
    CreateCourseRequest,
    CreateTrainerRequest,
    CreateTraineeRequest,
    CreateEvaluationRequest,
    EnrollTraineeRequest,
    UpdateEvaluationRequest,
)
from app.domain.enums import Category, Grade, TrainingMethod
from app.domain.exceptions import AppException
from app.presentation.cli.display import (
    show_app_exception,
    show_course_progress,
    show_entity,
    show_list,
    show_success,
)
from app.presentation.cli.input import pause, read_choice, read_int, read_optional_text, read_required_text
from app.presentation.cli.menus.common_menu import CommonMenu


class ManagerMenu(CommonMenu):
    def run(self) -> None:
        while self.app.session.is_authenticated:
            print("\n===== قائمة مدير الدورة =====")
            print("1. إدارة المتدربين")
            print("2. إدارة المدربين")
            print("3. إدارة الدورات")
            print("4. التسجيلات")
            print("5. الإسنادات")
            print("6. التقارير اليومية")
            print("7. التقييمات")
            print("8. تسجيل الخروج")
            choice = read_choice("اختر رقم العملية: ", [str(i) for i in range(1, 9)])
            try:
                actions = {
                    "1": self.trainees,
                    "2": self.trainers,
                    "3": self.courses,
                    "4": self.enrollments,
                    "5": self.assignments,
                    "6": self.reports,
                    "7": self.evaluations,
                    "8": self.app.logout,
                }
                actions[choice]()
            except AppException as exc:
                show_app_exception(exc)
                pause()
            except Exception:
                self.app.container.logger.exception("Unexpected error in manager menu")
                print("\n[خطأ] حدث خطأ غير متوقع. راجع سجل النظام.")
                pause()

    def trainees(self) -> None:
        c = self.app.container
        choice = read_choice(
            "\nإدارة المتدربين:\n1. إنشاء متدرب\n2. تحديث متدرب\n3. عرض المتدربين\nاختر: ",
            ["1", "2", "3"],
        )
        if choice == "1":
            request = CreateTraineeRequest(
                read_required_text("المعرّف: "),
                read_required_text("الاسم: "),
                read_int("العمر: ", min_value=1, max_value=120),
                read_required_text("الهاتف: "),
                read_required_text("البريد الإلكتروني: "),
                Category(read_choice("الفئة [A/B/C]: ", ["A", "B", "C"])),
            )
            show_entity(c.create_trainee.execute(request, self.app.session.current_user))
            show_success("تم إنشاء المتدرب بنجاح.")
        elif choice == "2":
            trainee_id = read_required_text("معرّف المتدرب: ")
            email = read_optional_text("البريد الإلكتروني الجديد (اتركه فارغًا للإبقاء): ")
            name = read_optional_text("الاسم الجديد (اتركه فارغًا للإبقاء): ")
            phone = read_optional_text("الهاتف الجديد (اتركه فارغًا للإبقاء): ")
            age_raw = read_optional_text("العمر الجديد (اتركه فارغًا للإبقاء): ")
            category_raw = read_optional_text("الفئة الجديدة [A/B/C] (اتركه فارغًا للإبقاء): ")
            age = int(age_raw) if age_raw else None
            category = Category(category_raw) if category_raw else None
            result = c.update_trainee.execute(
                trainee_id,
                self.app.session.current_user,
                name=name,
                age=age,
                phone=phone,
                email=email,
                category=category,
            )
            show_entity(result)
            show_success("تم تحديث المتدرب بنجاح.")
        else:
            show_list(c.list_trainees.execute(self.app.session.current_user))
        pause()

    def trainers(self) -> None:
        c = self.app.container
        choice = read_choice(
            "\nإدارة المدربين:\n1. إنشاء مدرب\n2. تحديث مدرب\n3. عرض المدربين\nاختر: ",
            ["1", "2", "3"],
        )
        if choice == "1":
            request = CreateTrainerRequest(
                read_required_text("المعرّف: "),
                read_required_text("الاسم: "),
                read_int("العمر: ", min_value=1, max_value=120),
                read_required_text("الهاتف: "),
                read_required_text("البريد الإلكتروني: "),
                Category(read_choice("الفئة [A/B/C]: ", ["A", "B", "C"])),
                TrainingMethod(
                    {
                        "1": TrainingMethod.ONSITE,
                        "2": TrainingMethod.REMOTE,
                        "3": TrainingMethod.ADMINISTRATIVE,
                    }[read_choice(
                        "طريقة التدريب:\n1. حضوري\n2. عن بُعد\n3. إداري\nاختر: ",
                        ["1", "2", "3"],
                    )]
                ),
            )
            show_entity(c.create_trainer.execute(request, self.app.session.current_user))
            show_success("تم إنشاء المدرب بنجاح.")
        elif choice == "2":
            trainer_id = read_required_text("معرّف المدرب: ")
            method_choice = read_optional_text(
                "طريقة التدريب الجديدة (حضوري/عن بُعد/إداري؛ اتركه فارغًا للإبقاء): "
            )
            method = {
                "1": TrainingMethod.ONSITE.value,
                "2": TrainingMethod.REMOTE.value,
                "3": TrainingMethod.ADMINISTRATIVE.value,
                "حضوري": TrainingMethod.ONSITE.value,
                "عن بُعد": TrainingMethod.REMOTE.value,
                "إداري": TrainingMethod.ADMINISTRATIVE.value,
            }.get(method_choice, method_choice)
            name = read_optional_text("الاسم الجديد (اتركه فارغًا للإبقاء): ")
            phone = read_optional_text("الهاتف الجديد (اتركه فارغًا للإبقاء): ")
            email = read_optional_text("البريد الإلكتروني الجديد (اتركه فارغًا للإبقاء): ")
            age_raw = read_optional_text("العمر الجديد (اتركه فارغًا للإبقاء): ")
            training_method = TrainingMethod(method) if method else None
            result = c.update_trainer.execute(
                trainer_id,
                self.app.session.current_user,
                name=name,
                age=int(age_raw) if age_raw else None,
                phone=phone,
                email=email,
                training_method=training_method,
            )
            show_entity(result)
            show_success("تم تحديث المدرب بنجاح.")
        else:
            show_list(c.list_trainers.execute(self.app.session.current_user))
        pause()

    def courses(self) -> None:
        c = self.app.container
        choice = read_choice(
            "\nإدارة الدورات:\n1. إنشاء دورة\n2. تحديث دورة\n3. عرض الدورات\n4. عرض تفاصيل دورة\nاختر: ",
            ["1", "2", "3", "4"],
        )
        if choice == "1":
            request = CreateCourseRequest(
                read_required_text("المعرّف: "),
                read_required_text("اسم الدورة: "),
                read_int("إجمالي الساعات: ", min_value=1),
                read_required_text("الوصف: "),
                read_int("ترتيب الدورة: ", min_value=1),
                self.app.session.current_user.id,
            )
            show_entity(c.create_course.execute(request, self.app.session.current_user))
            show_success("تم إنشاء الدورة بنجاح.")
        elif choice == "2":
            course_id = read_required_text("معرّف الدورة: ")
            result = c.update_course.execute(
                course_id,
                self.app.session.current_user,
                name=read_optional_text("اسم الدورة الجديد (اتركه فارغًا للإبقاء): "),
                description=read_optional_text("الوصف الجديد (اتركه فارغًا للإبقاء): "),
                total_hours=(lambda raw: int(raw) if raw else None)(read_optional_text("إجمالي الساعات الجديد (اتركه فارغًا للإبقاء): ")),
                order_index=(lambda raw: int(raw) if raw else None)(read_optional_text("ترتيب الدورة الجديد (اتركه فارغًا للإبقاء): ")),
            )
            show_entity(result)
            show_success("تم تحديث الدورة بنجاح.")
        elif choice == "3":
            show_list(c.list_courses.execute(self.app.session.current_user))
        else:
            course, progress = c.view_course.execute(
                read_required_text("معرّف الدورة: "), self.app.session.current_user
            )
            show_entity(course)
            show_course_progress(progress)
        pause()

    def enrollments(self) -> None:
        c = self.app.container
        choice = read_choice(
            "\nالتسجيلات:\n1. تسجيل متدرب\n2. عرض التسجيلات\n3. إكمال التسجيل\nاختر: ",
            ["1", "2", "3"],
        )
        if choice == "1":
            result = c.enroll_trainee.execute(
                EnrollTraineeRequest(
                    read_required_text("معرّف المتدرب: "),
                    read_required_text("معرّف الدورة: "),
                ),
                self.app.session.current_user,
            )
            show_entity(result)
            show_success("تم تسجيل المتدرب بنجاح.")
        elif choice == "2":
            show_list(c.list_enrollments.execute(self.app.session.current_user))
        else:
            result = c.complete_enrollment.execute(
                read_required_text("معرّف التسجيل: "), self.app.session.current_user
            )
            show_entity(result)
            show_success("تم إكمال التسجيل بنجاح.")
        pause()

    def assignments(self) -> None:
        c = self.app.container
        choice = read_choice(
            "\nالإسنادات:\n1. إسناد مدرب إلى دورة\n2. إسناد مدرب إلى متدرب داخل دورة\n3. عرض الإسنادات\nاختر: ",
            ["1", "2", "3"],
        )
        if choice == "1":
            result = c.assign_trainer_to_course.execute(
                AssignTrainerRequest(
                    read_required_text("معرّف الدورة: "),
                    read_required_text("معرّف المدرب: "),
                ),
                self.app.session.current_user,
            )
            show_entity(result)
            show_success("تم إسناد المدرب إلى الدورة.")
        elif choice == "2":
            result = c.assign_trainer_to_trainee.execute(
                AssignTraineeRequest(
                    read_required_text("معرّف الدورة: "),
                    read_required_text("معرّف المدرب: "),
                    read_required_text("معرّف المتدرب: "),
                ),
                self.app.session.current_user,
            )
            show_entity(result)
            show_success("تم إسناد المدرب إلى المتدرب داخل الدورة.")
        else:
            show_list(c.list_assignments.execute(self.app.session.current_user))
        pause()

    def reports(self) -> None:
        c = self.app.container
        choice = read_choice("\nالتقارير اليومية:\n1. عرض التقارير\n2. حذف تقرير\nاختر: ", ["1", "2"])
        if choice == "1":
            show_list(
                c.list_reports.execute(
                    self.app.session.current_user,
                    course_id=read_optional_text("معرّف الدورة (Enter=الكل): "),
                )
            )
        else:
            c.delete_report.execute(
                read_required_text("معرّف التقرير: "), self.app.session.current_user
            )
            show_success("تم حذف التقرير بنجاح.")
        pause()

    def evaluations(self) -> None:
        c = self.app.container
        choice = read_choice(
            "\n===== تقييمات الدورات =====\n"
            "1. عرض قائمة التقييمات\n"
            "2. عرض تقييم\n"
            "3. تصحيح تقييم\n"
            "اختر: ",
            ["1", "2", "3"],
        )
        if choice == "1":
            show_list(c.list_evaluations.execute(self.app.session.current_user))
            pause()
        elif choice == "2":
            self.view_evaluation()
        else:
            result = c.update_evaluation.execute(
                UpdateEvaluationRequest(
                    read_required_text("معرّف التقييم: "),
                    Grade(read_choice("الدرجة الجديدة [A/B/C/D]: ", ["A", "B", "C", "D"])),
                ),
                self.app.session.current_user,
            )
            show_entity(result)
            show_success("تم تصحيح التقييم بنجاح.")
            pause()
