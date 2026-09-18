from __future__ import annotations

from app.presentation.cli.display import show_course_progress, show_entity, show_list
from app.presentation.cli.input import pause, read_choice, read_required_text


class CommonMenu:
    def __init__(self, app) -> None:
        self.app = app

    def view_course(self) -> None:
        course_id = read_required_text("معرّف الدورة: ")
        course, progress = self.app.container.view_course.execute(
            course_id, self.app.session.current_user
        )
        show_entity(course)
        show_course_progress(progress)
        pause()

    def view_evaluation(self) -> None:
        choice = read_choice(
            "\nطريقة البحث عن التقييم:\n"
            "1. باستخدام معرّف التقييم\n"
            "2. باستخدام معرّف التسجيل\n"
            "اختر: ",
            ["1", "2"],
        )
        if choice == "1":
            evaluation = self.app.container.view_evaluation.execute(
                self.app.session.current_user,
                evaluation_id=read_required_text("معرّف التقييم: "),
            )
        else:
            evaluation = self.app.container.view_evaluation.execute(
                self.app.session.current_user,
                enrollment_id=read_required_text("معرّف التسجيل: "),
            )
        if evaluation is None:
            print("لا يوجد تقييم مرتبط بهذا التسجيل.")
        else:
            show_entity(evaluation)
        pause()

    def show_items(self, items) -> None:
        show_list(items)
        pause()

    def logout(self) -> None:
        self.app.logout()
