from __future__ import annotations

from datetime import date

from app.domain.exceptions import InputCancelled


def _read(prompt: str) -> str:
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt) as exc:
        raise InputCancelled("تم إلغاء الإدخال.") from exc


def read_required_text(prompt: str) -> str:
    while True:
        value = _read(prompt).strip()
        if value:
            return value
        print("القيمة مطلوبة.")


def read_optional_text(prompt: str) -> str | None:
    value = _read(prompt).strip()
    return value or None


def read_int(
    prompt: str,
    *,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    while True:
        raw = _read(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("أدخل رقمًا صحيحًا.")
            continue
        if min_value is not None and value < min_value:
            print(f"القيمة يجب ألا تقل عن {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"القيمة يجب ألا تزيد عن {max_value}.")
            continue
        return value


def read_date(prompt: str) -> date:
    while True:
        raw = _read(prompt).strip()
        try:
            return date.fromisoformat(raw)
        except ValueError:
            print("صيغة التاريخ غير صحيحة. استخدم YYYY-MM-DD.")


def read_choice(prompt: str, choices: list[str]) -> str:
    if not choices:
        raise ValueError("choices must not be empty")
    while True:
        value = _read(prompt).strip()
        if value in choices:
            return value
        print(f"اختر إحدى القيم التالية: {', '.join(choices)}")


def confirm(prompt: str) -> bool:
    return read_choice(f"{prompt} (نعم/لا): ", ["نعم", "لا"]) == "نعم"


def pause() -> None:
    _read("\nاضغط Enter للمتابعة...")
