from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum

from app.domain.exceptions import AppException
from app.domain.enums import Category, CourseStatus, EnrollmentStatus, Grade, Role, TrainingMethod


FIELD_LABELS = {
    "id": "المعرّف",
    "username": "اسم المستخدم",
    "role": "الدور",
    "profile_id": "معرّف الملف الشخصي",
    "name": "الاسم",
    "age": "العمر",
    "phone": "الهاتف",
    "email": "البريد الإلكتروني",
    "category": "الفئة",
    "training_method": "طريقة التدريب",
    "course_id": "معرّف الدورة",
    "course_name": "اسم الدورة",
    "manager_id": "معرّف مدير الدورة",
    "description": "الوصف",
    "total_hours": "إجمالي الساعات",
    "order_index": "ترتيب الدورة",
    "status": "الحالة",
    "trainee_id": "معرّف المتدرب",
    "trainer_id": "معرّف المدرب",
    "enrollment_id": "معرّف التسجيل",
    "evaluation_id": "معرّف التقييم",
    "grade": "الدرجة",
    "report_date": "تاريخ التقرير",
    "hours_done": "الساعات المنجزة",
    "note": "الملاحظة",
    "created_at": "تاريخ الإنشاء",
    "updated_at": "تاريخ التحديث",
    "completed_at": "تاريخ الإكمال",
    "password_hash": "بيانات كلمة المرور",
}

VALUE_LABELS = {
    Category.A: "الفئة A",
    Category.B: "الفئة B",
    Category.C: "الفئة C",
    TrainingMethod.ONSITE: "حضوري",
    TrainingMethod.REMOTE: "عن بُعد",
    TrainingMethod.ADMINISTRATIVE: "إداري",
    CourseStatus.NOT_STARTED: "لم تبدأ",
    CourseStatus.IN_PROGRESS: "قيد التنفيذ",
    CourseStatus.COMPLETED: "مكتملة",
    EnrollmentStatus.ACTIVE: "نشط",
    EnrollmentStatus.COMPLETED: "مكتمل",
    Grade.A: "A — ممتاز",
    Grade.B: "B — جيد جدًا",
    Grade.C: "C — جيد",
    Grade.D: "D — مقبول",
    Role.COURSE_MANAGER: "مدير دورة",
    Role.TRAINER: "مدرب",
    Role.TRAINEE: "متدرب",
}

ERROR_DEFAULTS = {
    "APP_ERROR": "حدث خطأ في التطبيق.",
    "VALIDATION_ERROR": "البيانات المدخلة غير صحيحة.",
    "AUTHENTICATION_ERROR": "فشلت المصادقة أو بيانات الدخول غير صحيحة.",
    "AUTHORIZATION_ERROR": "ليس لديك الصلاحية لتنفيذ هذه العملية.",
    "NOT_FOUND": "العنصر المطلوب غير موجود.",
    "DUPLICATE_ERROR": "البيانات موجودة مسبقًا ولا يمكن تكرارها.",
    "BUSINESS_RULE_ERROR": "لا يمكن تنفيذ العملية بسبب قاعدة من قواعد العمل.",
    "STORAGE_ERROR": "حدث خطأ أثناء حفظ البيانات.",
    "INPUT_CANCELLED": "تم إلغاء الإدخال.",
}


def show_message(message: str) -> None:
    print(message)


def show_error(message: str) -> None:
    print(f"\n[خطأ] {message}")


def show_app_exception(exc: AppException) -> None:
    message = str(exc).strip()
    if not any("\u0600" <= char <= "\u06ff" for char in message):
        message = ERROR_DEFAULTS.get(exc.code, "حدث خطأ أثناء تنفيذ العملية.")
    show_error(f"[{exc.code}] {message}")


def show_success(message: str) -> None:
    print(f"\n[نجاح] {message}")


def _label_for(value: object) -> str:
    if isinstance(value, Enum):
        return VALUE_LABELS.get(value, str(value.value))
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="seconds")
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def show_entity(entity: object) -> None:
    print("-" * 60)
    if is_dataclass(entity):
        for key, value in asdict(entity).items():
            print(f"{FIELD_LABELS.get(key, key)}: {_label_for(value)}")
    else:
        print(_label_for(entity))
    print("-" * 60)


def show_list(items: list[object]) -> None:
    if not items:
        print("لا توجد بيانات للعرض.")
        return
    for index, item in enumerate(items, 1):
        print(f"\n[{index}]")
        show_entity(item)


def show_course_progress(progress) -> None:
    print(
        f"الساعات المنجزة: {progress.completed_hours} | "
        f"الساعات المتبقية: {progress.remaining_hours} | "
        f"حالة الدورة: {_label_for(progress.status)}"
    )
