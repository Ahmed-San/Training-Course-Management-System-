# TCMS V2 — دليل تنفيذ M5
## Evaluation + CLI عربي + Integration + Release

**الفرع المستهدف:** `feature/m5-evaluation-cli-integration`

هذا الإصدار يحافظ على حدود M5: التقييم، حالات الصلاحية والنطاق، واجهة CLI، اختبارات التكامل، وتجهيز النقل/الإصدار. لا يعيد بناء M1 أو M2 أو M3 أو M4.

## 1. ملفات M5 التي تم تنفيذها

```text
app/domain/entities/evaluation.py
app/application/use_cases/evaluations.py
app/presentation/cli/app.py
app/presentation/cli/input.py
app/presentation/cli/display.py
app/presentation/cli/menus/common_menu.py
app/presentation/cli/menus/manager_menu.py
app/presentation/cli/menus/trainer_menu.py
app/presentation/cli/menus/trainee_menu.py

tests/unit/test_evaluation.py
tests/unit/test_cli_m5.py
tests/integration/test_workflows.py

docs/M5_EXECUTION_GUIDE_AR.md
docs/M5_COMPLETION_REPORT_AR.md
```

## 2. Evaluation Domain

الكيان يحتوي:

```text
id
enrollment_id
trainer_id
grade
created_at
updated_at
```

ويتحقق من:

```text
IDs غير فارغة
Grade صحيح
التواريخ من نوع datetime
updated_at >= created_at
```

`change_grade()` يغيّر الدرجة فقط. تحديث `updated_at` قرار workflow ويحدث في Application.

## 3. Evaluation Application

### CreateEvaluationUseCase

يسمح بالإنشاء للمدرب المصادق عليه فقط، مع الشروط:

```text
Trainer
→ profile موجود
→ TrainingMethod = ONSITE
→ assigned إلى Course
→ assigned إلى Trainee داخل Course
→ Enrollment = ACTIVE
→ لا يوجد Evaluation مسبق
→ إنشاء Evaluation
```

التكرار ينتج `DuplicateError`.

### UpdateEvaluationUseCase

```text
Trainer
→ ONSITE
→ Course assignment
→ Trainee assignment
→ التقييم يخص المدرب
→ Enrollment ACTIVE
→ update
```

بعد إكمال Enrollment يمنع المدرب من التعديل.

مدير الدورة يستطيع التصحيح فقط عندما يكون `course.manager_id` داخل هوية المدير الحالية.

### ViewEvaluationUseCase

```text
Manager → evaluations داخل دوراته فقط
Trainer → داخل course + trainee assignment
Trainee → تقييمه الشخصي بعد completion فقط
```

البحث مدعوم بواسطة `evaluation_id` أو `enrollment_id`.

### ListEvaluationsUseCase

يعيد البيانات حسب نفس قواعد scope، وليس كل السجلات بلا فلترة.

## 4. CLI

الـCLI لا يصل مباشرة إلى JSON أو Repository. المسار:

```text
CLI
 ↓
Use Case
 ↓
Repository Contract
 ↓
Infrastructure
```

واجهة التشغيل عربية، وتشمل:

```text
تسجيل الدخول
اسم المستخدم
كلمة المرور
القوائم بحسب الدور
خيارات التقييم
رسائل النجاح والأخطاء
تسجيل الخروج
```

### مدير الدورة

```text
1. إدارة المتدربين
2. إدارة المدربين
3. إدارة الدورات
4. التسجيلات
5. الإسنادات
6. التقارير اليومية
7. التقييمات
8. تسجيل الخروج
```

داخل التقييمات:

```text
1. عرض قائمة التقييمات
2. عرض تقييم
3. تصحيح تقييم
```

### المدرب

```text
1. دوراتي
2. المتدربون المسندون إليّ
3. التقارير اليومية
4. التقييمات
5. تفاصيل دورة
6. تسجيل الخروج
```

داخل التقييمات:

```text
1. عرض قائمة التقييمات
2. عرض تقييم
3. إنشاء تقييم
4. تعديل تقييم
```

### المتدرب

داخل التقييمات:

```text
1. عرض تقييماتي
2. عرض تقييم محدد
```

ولا توجد خيارات إنشاء أو تعديل أو حذف.

## 5. Input Layer

`input.py` مسؤول عن شكل الإدخال فقط:

```text
read_required_text()
read_optional_text()
read_int()
read_date()
read_choice()
confirm()
pause()
```

لا توجد Business Rules داخل Input Layer.

## 6. Error Handling

الـCLI يمسك `AppException` عند حدود العرض ويمنع ظهور stack trace للمستخدم في التشغيل الطبيعي.

أمثلة العرض:

```text
[خطأ] [AUTHORIZATION_ERROR] ليس لديك الصلاحية لتنفيذ هذه العملية.
[نجاح] تم تسجيل الدخول بنجاح.
```

## 7. الاختبارات

تمت إضافة Unit Tests لتغطية:

```text
Entity validation
change_grade()
Create
Duplicate
Completed enrollment
Remote trainer
Trainer خارج scope
Trainer update قبل completion
Trainer update بعد completion
Trainer ownership
View scope
List scope
CLI Arabic menus/login
```

واختبارات Integration لتغطية:

```text
Create evaluation
Duplicate rejected
Remote trainer rejected
Trainer outside scope rejected
Trainer update before completion
Completion lock
Manager correction
Manager outside course scope
Manager view/list scope
Trainee visibility
Cross-trainee isolation
Persistence after success
Rollback after failure
```

## 8. بوابات التحقق

شغّل من جذر المشروع:

```bash
python -m pytest -q
python -m compileall -q app main.py
git diff --check
```

ثم فحص الحالة:

```bash
git status
git diff --stat
git log --oneline -n 10
```

## 9. تشغيل CLI

```bash
python main.py
```

حسابات العرض الموجودة في المشروع:

```text
manager / manager123
trainer / trainer123
trainee / trainee123
```

هذه بيانات Demo وليست بيانات إنتاج.

## 10. Vibe Coding

استخدم AI في الوحدات الصغيرة بعد تثبيت العقد، مثل:

```text
Implement ONLY app/domain/entities/evaluation.py.
Respect the existing contracts.
Do not modify unrelated files.
Do not add dependencies.
Do not invent business rules.
Return the complete file.
```

ثم:

```bash
git diff -- <file>
python -m pytest <focused-test> -q
```

لا تستخدم Prompt من نوع: `Build the whole M5 system`.

## 11. النقل إلى المشروع الرئيسي

هذه الحزمة تم إعدادها كـoverlay. حافظ على ملفات M1/M2/M3/M4 الموجودة في مشروعك، واستبدل ملفات M5 المرفقة فقط. عند اختلاف عقد مشروعك الحالي مع هذه النسخة، لا تجبر الدمج؛ عالج اختلاف العقد أولًا.
