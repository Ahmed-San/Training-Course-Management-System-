# Training Course Management System (TCMS)
## V2 Technical Design Baseline

**Version:** V2.0  
**Architecture:** Clean Architecture  
**Language:** Python 3.11+  
**Interface:** CLI  
**Persistence:** One JSON file  
**Testing:** pytest  
**Runtime third-party dependencies:** None  
**Development dependency:** pytest  
**Project mode:** One-day team project / academic course project with real-world structure

---

# 1. Purpose

هذا المستند هو خط الأساس التقني للمشروع قبل بدء البرمجة. الهدف هو تثبيت النموذج، العلاقات، المسؤوليات، الصلاحيات، شكل التخزين، والملفات المطلوبة بحيث يستطيع خمسة أعضاء العمل بالتوازي دون تضارب.

المبدأ الأساسي:

> نقل التكرار إلى طبقات مشتركة، مع إبقاء قواعد العمل المتخصصة في مكان واضح.

لذلك سيتم استخدام:

- `BaseEntity` لتوحيد الهوية.
- `Person` للحقول المشتركة بين `Trainee` و`Trainer`.
- Generic Repository لعمليات CRUD المشتركة.
- `JsonDatabase` كمخزن منخفض المستوى.
- Serializer عام لتحويل Entities إلى JSON والعكس.
- Unit of Work لضمان أن العمليات التي تغيّر أكثر من Entity تحفظ مرة واحدة.
- Authorization Service مركزي للصلاحيات.
- Course Progress Service لحساب الساعات والحالة.
- Use Cases لتنفيذ حالات الاستخدام وقواعد العمل.

---

# 2. قرارات التصميم المعتمدة

## 2.1 الوراثة

الوراثة ستكون:

```text
BaseEntity
├── Person
│   ├── Trainee
│   └── Trainer
├── Course
├── Enrollment
├── Evaluation
├── DailyReport
├── User
├── CourseTrainerAssignment
└── TrainerTraineeAssignment
```

لا ترث `Course` أو `Enrollment` أو `Evaluation` من `Person` لأنها ليست أشخاصًا.

## 2.2 حالة الدورة والساعات المتبقية

لن يتم تخزين `remaining_hours` و`status` كمصدر حقيقة مستقل عن التقارير.

المصدر الحقيقي:

```text
Course.total_hours
+
DailyReport.hours_done
```

ومنها يحسب النظام:

```text
completed_hours
remaining_hours
status
```

هذا يمنع التناقض بين السجلات.

## 2.3 ملف JSON واحد

سيكون لدينا:

```text
data/database.json
```

وهيكل المستوى الأعلى هو Dictionary، وكل Collection هي List of Dictionaries.

## 2.4 Repository

العمليات العامة مثل:

```text
add
get_by_id
get_all
update
delete
exists
count
```

تُنفذ مرة واحدة في Generic Repository.

الاستعلامات المتخصصة فقط تذهب إلى Repositories متخصصة عند الحاجة.

## 2.5 المصادقة والصلاحيات

`Role` منفصل عن `TrainingMethod`.

مثال:

```text
Role = TRAINER
TrainingMethod = ONSITE
```

والصلاحية النهائية تعتمد على:

```text
Role
+ TrainingMethod
+ Assignment Scope
+ Course Status
```

## 2.6 التسجيل والتقييم

لا يرتبط التقييم بالمتدرب مباشرة.

العلاقة الصحيحة:

```text
Trainee -> Enrollment -> Evaluation
```

وبالتالي يمكن للمتدرب الحصول على تقييم مختلف لكل دورة.

---

# 3. البيئة والتثبيت

## 3.1 متطلبات التشغيل

يفضل توحيد الفريق على Python 3.11 أو أحدث ضمن نفس الإصدار قدر الإمكان.

المشروع لا يحتاج مكتبات خارجية وقت التشغيل؛ `dataclasses`, `json`, `pathlib`, `typing`, `enum`, `datetime`, `logging`, `hashlib`, `secrets` وغيرها من الأدوات الأساسية موجودة في Python Standard Library.

Python يوفر `venv` لإنشاء بيئات معزولة للمشروع، والبيئة الافتراضية لا يجب إضافتها إلى Git. [Official Python venv documentation](https://docs.python.org/3.13/library/venv.html)

`dataclasses` توفر إنشاء الكلاسات البياناتية وطرقًا مثل `__init__` و`__repr__` تلقائيًا. [Official Python dataclasses documentation](https://docs.python.org/3.13/library/dataclasses.html)

`typing` يدعم الـ Generic classes والـ TypeVar والـ Type hints المستخدمة في Generic Repository. [Official Python typing documentation](https://docs.python.org/3.13/library/typing.html)

`json` موجود في Python Standard Library ويحوّل Python objects الأساسية إلى JSON والعكس. [Official Python json documentation](https://docs.python.org/3.13/library/json.html)

للاختبارات سنستخدم pytest كمكتبة تطوير فقط. التثبيت الرسمي هو عبر pip. [Official pytest getting started](https://docs.pytest.org/en/stable/getting-started.html)

## 3.2 إنشاء البيئة

### Windows PowerShell

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

### Git Bash على Windows

```bash
python --version
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

### Linux

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

## 3.3 إيقاف البيئة

```bash
deactivate
```

## 3.4 `requirements-dev.txt`

```text
pytest>=9.1,<10
```

لا نضع مكتبات runtime خارجية في V1.

---

# 4. لماذا لا نضيف ORM أو Database Package؟

لأن المتطلب في V1 هو JSON، والهدف من المشروع هو تطبيق مفاهيم Python وClean Architecture وGit/Linux وVibe Coding، وليس إدارة قاعدة بيانات فعلية.

إضافة SQLAlchemy أو PostgreSQL الآن ستزيد وقت الإنشاء والاختبار ولا تضيف قيمة تناسب مدة يوم واحد.

لكن Architecture ستفصل Domain/Application عن Infrastructure، بحيث يمكن استبدال JSON مستقبلًا دون إعادة كتابة Business Rules.

---

# 5. الهيكل النهائي للمشروع

```text
training_course_management/
│
├── app/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── base_entity.py
│   │   │   ├── person.py
│   │   │   ├── trainee.py
│   │   │   ├── trainer.py
│   │   │   ├── course.py
│   │   │   ├── enrollment.py
│   │   │   ├── evaluation.py
│   │   │   ├── daily_report.py
│   │   │   ├── user.py
│   │   │   └── assignments.py
│   │   │
│   │   ├── enums.py
│   │   ├── exceptions.py
│   │   └── repositories/
│   │       ├── base_repository.py
│   │       ├── user_repository.py
│   │       ├── course_repository.py
│   │       ├── enrollment_repository.py
│   │       ├── assignment_repository.py
│   │       ├── daily_report_repository.py
│   │       └── evaluation_repository.py
│   │
│   ├── application/
│   │   ├── dto/
│   │   │   └── requests.py
│   │   │
│   │   ├── use_cases/
│   │   │   ├── auth.py
│   │   │   ├── trainees.py
│   │   │   ├── trainers.py
│   │   │   ├── courses.py
│   │   │   ├── enrollments.py
│   │   │   ├── assignments.py
│   │   │   ├── reports.py
│   │   │   └── evaluations.py
│   │   │
│   │   ├── services/
│   │   │   ├── authorization.py
│   │   │   └── course_progress.py
│   │   │
│   │   └── unit_of_work.py
│   │
│   ├── infrastructure/
│   │   ├── persistence/
│   │   │   ├── json_database.py
│   │   │   ├── json_repository.py
│   │   │   ├── json_unit_of_work.py
│   │   │   └── serializer.py
│   │   │
│   │   ├── auth/
│   │   │   └── password_hasher.py
│   │   │
│   │   └── logging/
│   │       └── app_logger.py
│   │
│   ├── presentation/
│   │   └── cli/
│   │       ├── app.py
│   │       ├── session.py
│   │       ├── input.py
│   │       ├── display.py
│   │       └── menus/
│   │           ├── manager_menu.py
│   │           ├── trainer_menu.py
│   │           ├── trainee_menu.py
│   │           └── common_menu.py
│   │
│   └── bootstrap.py
│
├── data/
│   └── database.json
│
├── logs/
│   └── .gitkeep
│
├── tests/
│   ├── unit/
│   │   ├── test_entities.py
│   │   ├── test_serializer.py
│   │   ├── test_repository.py
│   │   ├── test_authorization.py
│   │   └── test_course_progress.py
│   │
│   └── integration/
│       └── test_workflows.py
│
├── screenshots/
│   ├── 01_environment/
│   ├── 02_project_setup/
│   ├── 03_git_github/
│   ├── 04_architecture/
│   ├── 05_vibe_coding/
│   ├── 06_cli/
│   ├── 07_business_rules/
│   ├── 08_tests/
│   └── 09_final_demo/
│
├── docs/
│   └── technical_design.md
│
├── main.py
├── README.md
├── requirements-dev.txt
└── .gitignore
```

---

# 6. ملفات لا نحتاجها في V1

لن ننشئ الملفات التالية إلا إذا ظهر احتياج حقيقي أثناء التنفيذ:

```text
factory.py
strategy.py
observer.py
mediator.py
specification.py
container.py
unit_of_work_factory.py
base_service.py
base_use_case.py
database_manager_for_each_entity.py
repository_for_every_crud_operation.py
mapper_for_every_single_field.py
```

الهدف هو تقليل التجريدات غير الضرورية.

كذلك لا نريد:

```text
services.py
```

يحتوي كل Business Logic في النظام.

ولا:

```text
utils.py
```

يصبح صندوقًا عشوائيًا لكل شيء.

---

# 7. Domain Model

## 7.1 BaseEntity

### Fields

```text
id: str
```

### Responsibility

توحيد الهوية لكل Entity.

### Methods

لا نضيف عمليات CRUD هنا.

---

# 8. Person

`Person` يرث من `BaseEntity`.

### Fields

```text
id: str
name: str
age: int
phone: str
email: str
```

### Shared methods

يمكن أن يحتوي على عمليات صغيرة مرتبطة بالبيانات المشتركة، مثل:

```text
update_contact_info()
```

لكن لا يحتوي على أي صلاحيات أو Repository Logic.

---

# 9. Trainee

يرث من `Person`.

### Fields

```text
id: str
name: str
age: int
phone: str
email: str
category: Category
```

### Methods

```text
change_category()
update_personal_info()
```

لا يحتوي على:

```text
save()
load()
enroll()
calculate_course_progress()
```

لأنها ليست مسؤولية Entity.

---

# 10. Trainer

يرث من `Person`.

### Fields

```text
id: str
name: str
age: int
phone: str
email: str
category: Category
training_method: TrainingMethod
```

### Methods

```text
change_training_method()
update_personal_info()
```

---

# 11. Course

يرث من `BaseEntity`.

### Persisted fields

```text
id: str
name: str
total_hours: int
description: str
order_index: int
manager_id: str
```

### Derived values

```text
completed_hours
remaining_hours
status
```

لا يتم حفظ القيم المشتقة كحقيقة مستقلة.

### Methods

```text
calculate_remaining_hours(completed_hours)
is_completed(completed_hours)
get_status(completed_hours)
```

### قواعد Entity

```text
total_hours > 0
order_index >= 1
name != empty
manager_id != empty
```

---

# 12. Enrollment

يمثل تسجيل متدرب معين في دورة معينة.

### Fields

```text
id: str
trainee_id: str
course_id: str
status: EnrollmentStatus
completed_at: datetime | None
```

`status` يمكن أن يكون قيمة محفوظة لأنه يمثل حالة التسجيل، لكن يجب أن يحدث تلقائيًا مع دورة الإنجاز.

### Methods

```text
complete(completed_at)
is_active()
is_completed()
```

---

# 13. Evaluation

يمثل تقييم متدرب داخل Enrollment معين.

### Fields

```text
id: str
enrollment_id: str
trainer_id: str
grade: Grade
created_at: datetime
updated_at: datetime
```

### Methods

```text
change_grade(new_grade)
```

لكن Use Case هو المسؤول عن السماح بالتغيير وفق الصلاحيات والحالة.

أي أن Entity لا تقرر هل المستخدم الحالي مخول أم لا.

---

# 14. DailyReport

### Fields

```text
id: str
course_id: str
trainer_id: str
report_date: date
hours_done: int
note: str
created_at: datetime
updated_at: datetime
```

### Rules

```text
hours_done > 0
course_id موجود
trainer_id موجود
report_date صحيح
```

في V1 يفضل وجود تقرير واحد فقط لنفس:

```text
course_id + trainer_id + report_date
```

لتقليل الازدواجية.

---

# 15. User

`User` منفصل عن `Person` لأن حساب الدخول ليس هو الملف الأكاديمي للشخص.

### Fields

```text
id: str
username: str
password_hash: str
role: Role
profile_id: str | None
```

### Rules

```text
username unique
password_hash is never plaintext
role is valid
```

---

# 16. Assignments

يمكن وضع العلاقات الوسيطة في ملف واحد لأنهما كيانات صغيرة ومترابطة.

## CourseTrainerAssignment

```text
id: str
course_id: str
trainer_id: str
```

## TrainerTraineeAssignment

```text
id: str
course_id: str
trainer_id: str
trainee_id: str
```

---

# 17. Enums

```text
Category
    A
    B
    C

TrainingMethod
    ONSITE
    REMOTE
    ADMINISTRATIVE

CourseStatus
    NOT_STARTED
    IN_PROGRESS
    COMPLETED

EnrollmentStatus
    ACTIVE
    COMPLETED

Grade
    A
    B
    C
    D

Role
    COURSE_MANAGER
    TRAINER
    TRAINEE
```

يجب استخدام Enum بدل Magic Strings المنتشرة في المشروع.

---

# 18. العلاقات

```text
Trainee 1 ---- N Enrollment N ---- 1 Course

Enrollment 1 ---- 0..1 Evaluation

Trainer N ---- N Course
        via CourseTrainerAssignment

Trainer N ---- N Trainee
        via TrainerTraineeAssignment
        scoped by Course

Trainer 1 ---- N DailyReport
Course  1 ---- N DailyReport

User 1 ---- 0..1 profile
Course N ---- 1 CourseManager(User)
```

---

# 19. قاعدة الدورة الحالية للمتدرب

المتدرب لا يملك أكثر من Enrollment واحد بحالة `ACTIVE` في نفس الوقت.

مثال صحيح:

```text
T001 -> C001 ACTIVE
T001 -> C002 COMPLETED
T001 -> C003 COMPLETED
```

مثال مرفوض:

```text
T001 -> C001 ACTIVE
T001 -> C002 ACTIVE
```

---

# 20. الانتقال إلى الدورة التالية

عند اكتمال الدورة الحالية:

```text
Course.remaining_hours == 0
        ↓
CourseStatus.COMPLETED
        ↓
Current Enrollment -> COMPLETED
        ↓
Evaluation becomes visible to trainee
        ↓
Trainee may enroll in next course
```

يجب أن يكون الانتقال إلى الدورة التالية صريحًا من خلال Use Case أو عملية Enrollment، وليس تلقائيًا بإنشاء Enrollment جديد في نفس لحظة إكمال الدورة إلا إذا كان هذا مطلوبًا في العرض النهائي.

هذا يمنع إنشاء تسجيل خاطئ قبل أن يوافق المدير أو يختار النظام الدورة التالية.

---

# 21. Course Progress Service

هذه الخدمة مسؤولة عن كل الحسابات المتعلقة بتقدم الدورة.

### Inputs

```text
course
reports
```

### Outputs

```text
completed_hours
remaining_hours
status
```

### Rules

```text
completed_hours = sum(report.hours_done)

remaining_hours = max(total_hours - completed_hours, 0)

if completed_hours == 0:
    status = NOT_STARTED
elif completed_hours < total_hours:
    status = IN_PROGRESS
else:
    status = COMPLETED
```

إذا تم تجاوز الساعات فلا يتم القص إلى `total_hours` أثناء الإنشاء؛ بل يرفض التقرير أولًا في Business Rule.

---

# 22. Generic Repository

## 22.1 العقد العام

```text
Repository[T]
    add(entity)
    get_by_id(id)
    get_all()
    update(entity)
    delete(id)
    exists(id)
    count()
```

هذا هو المكان الذي نزيل فيه CRUD المكرر.

## 22.2 لا نضع فيه Business Logic

لا يحتوي على:

```text
complete_course()
assign_trainer()
lock_evaluation()
calculate_progress()
can_edit_student()
```

لأن هذه ليست مسؤوليات التخزين العام.

---

# 23. Specialized Repositories

نستخدم Repository متخصص فقط عندما نحتاج Query حقيقي غير موجود في CRUD العام.

## UserRepository

```text
get_by_username(username)
```

## EnrollmentRepository

```text
get_active_by_trainee(trainee_id)
get_by_course(course_id)
get_by_trainee(trainee_id)
```

## CourseRepository

```text
get_by_manager(manager_id)
```

## AssignmentRepository

```text
is_trainer_assigned_to_course(trainer_id, course_id)
is_trainer_assigned_to_trainee(trainer_id, trainee_id, course_id)
get_courses_by_trainer(trainer_id)
get_trainees_by_trainer(trainer_id, course_id)
```

## DailyReportRepository

```text
get_by_course(course_id)
get_by_trainer(trainer_id)
get_by_course_trainer_date(course_id, trainer_id, report_date)
```

## EvaluationRepository

```text
get_by_enrollment(enrollment_id)
```

لا ننشئ `TraineeRepository` و`TrainerRepository` متخصصين في V1 طالما أن CRUD العام كافٍ لهما.

---

# 24. JsonDatabase

هذه أدنى طبقة في التخزين.

### مسؤولياتها فقط

```text
load()
save(data)
get_collection(name)
replace_collection(name, data)
initialize_empty_database()
```

ولا تعرف `Trainee`, `Trainer`, `Course` كقواعد مجال.

هي فقط تعرف:

```text
JSON file -> Python dict
Python dict -> JSON file
```

---

# 25. شكل database.json

```json
{
  "users": [],
  "trainees": [],
  "trainers": [],
  "courses": [],
  "enrollments": [],
  "evaluations": [],
  "daily_reports": [],
  "course_trainer_assignments": [],
  "trainer_trainee_assignments": []
}
```

كل Collection:

```text
entity_name -> list[dict]
```

مثال:

```json
{
  "trainees": [
    {
      "id": "T001",
      "name": "Ahmed",
      "age": 20,
      "phone": "777777777",
      "email": "ahmed@example.com",
      "category": "A"
    }
  ]
}
```

---

# 26. Serializer

بدل كتابة:

```text
TraineeMapper
TrainerMapper
CourseMapper
EnrollmentMapper
...
```

لكل Entity، نستخدم Serializer عام يدعم أنواع المشروع:

```text
str
int
float
bool
None
Enum
date
datetime
list
dict
```

المطلوب:

```text
entity -> dict -> JSON
JSON -> dict -> entity
```

### قاعدة مهمة

لا يتم تخزين Enum كنص تمثيل Python مثل:

```text
Category.A
```

بل:

```text
"A"
```

وكذلك التاريخ:

```text
ISO 8601 string
```

حتى يكون JSON واضحًا وقابلًا للقراءة.

---

# 27. JsonRepository

`JsonRepository[T]` هو التنفيذ العام للعقد.

يعتمد على:

```text
JsonDatabase
Serializer
collection_name
entity_type
```

مثال مفاهيمي:

```text
JsonRepository[Trainee]
    collection = "trainees"
    entity_type = Trainee

JsonRepository[Course]
    collection = "courses"
    entity_type = Course
```

وبذلك لا نكتب CRUD مرتين.

---

# 28. Unit of Work

نحتاج Unit of Work لأن بعض العمليات تغيّر أكثر من Collection.

مثال إكمال الدورة:

```text
reports
courses
active enrollments
```

لا نريد حفظ كل تغيير بشكل مستقل.

### النموذج

```text
begin
  ↓
load/snapshot state
  ↓
multiple repository operations
  ↓
validate
  ↓
commit once
```

وعند الفشل:

```text
exception
  ↓
rollback in-memory changes
  ↓
original file remains unchanged
```

---

# 29. Atomic JSON Save

`JsonDatabase.save()` يجب أن يحفظ بشكل آمن نسبيًا:

```text
serialize
   ↓
write temporary file
   ↓
flush
   ↓
replace database.json
```

الهدف هو تقليل احتمال ترك `database.json` فارغًا أو مكسورًا إذا توقف البرنامج أثناء الكتابة.

---

# 30. حدود التخزين

هذا التخزين مناسب لمشروع CLI صغير يعمل من عملية واحدة.

لا نعتبره Database Server حقيقيًا.

في V1:

```text
no concurrent writers
no multi-process locking
no network access
```

هذه قيود مقصودة وليست أخطاء في نطاق المشروع.

---

# 31. Use Cases

## Authentication

```text
Login
Logout
```

## Trainees

```text
CreateTrainee
UpdateTrainee
ViewTrainee
ListTrainees
```

## Trainers

```text
CreateTrainer
UpdateTrainer
ViewTrainer
ListTrainers
```

## Courses

```text
CreateCourse
UpdateCourse
ViewCourse
ListCourses
```

## Enrollment

```text
EnrollTrainee
CompleteEnrollment
ViewEnrollment
```

## Assignment

```text
AssignTrainerToCourse
AssignTrainerToTrainee
```

## Reports

```text
CreateDailyReport
UpdateDailyReport
DeleteDailyReport
ListDailyReports
```

## Evaluation

```text
CreateEvaluation
UpdateEvaluation
ViewEvaluation
```

لا يلزم إنشاء Use Case لكل `get_all` إذا كانت العملية العامة يمكن استدعاؤها من Use Case متعلق بالعرض.

---

# 32. Authorization Service

يكون في:

```text
app/application/services/authorization.py
```

ويقدم قرارات مثل:

```text
can_view_course()
can_edit_course()
can_view_trainee()
can_edit_trainee()
can_add_report()
can_edit_report()
can_delete_report()
can_add_evaluation()
can_edit_evaluation()
can_view_evaluation()
```

هذه الدوال لا تنفذ عملية التخزين؛ فقط تحدد هل العملية مسموحة أم لا.

---

# 33. مصفوفة الصلاحيات

| العملية | Manager | Onsite Trainer | Remote Trainer | Trainee |
|---|---|---|---|---|
| عرض الدورة | نعم | نعم | نعم | نعم |
| تعديل الدورة | نعم | لا | لا | لا |
| عرض المتدربين | نعم | متدربوه فقط | طلاب دوراته | بياناته فقط |
| تعديل متدرب | نعم | متدربوه فقط | لا | لا |
| إضافة/تعديل Daily Report | نعم | نعم ضمن دوراته | لا | لا |
| عرض Daily Reports | نعم | نعم | نعم | نعم |
| إضافة Evaluation | نعم | نعم لمتدربيه | لا | لا |
| تعديل Evaluation قبل الإكمال | نعم | نعم لمتدربيه | لا | لا |
| تعديل Evaluation بعد الإكمال | نعم | لا | لا | لا |
| عرض تقييمه | نعم | حسب الصلاحية | لا | بعد اكتمال الدورة |
| Assign Trainer | نعم | لا | لا | لا |
| Assign Trainee | نعم | لا | لا | لا |

ملاحظة: كلمة `Manager` تعني مدير الدورة المخولة له العملية في الدورة المعنية، وليست حسابًا عالميًا بالضرورة.

---

# 34. Business Rules للصلاحيات

## 34.1 Onsite Trainer

يمكنه تعديل Trainee فقط إذا:

```text
user.role == TRAINER
AND training_method == ONSITE
AND trainer is assigned to trainee in this course
```

## 34.2 Remote Trainer

يقتصر على القراءة في نطاق دوراته وطلابه.

## 34.3 Evaluation

التعديل متاح للمدرب الحضوري قبل اكتمال الدورة فقط:

```text
ONSITE
AND owns/assigned-to trainee
AND course != COMPLETED
```

بعد اكتمال الدورة:

```text
Trainer -> denied
Course Manager -> allowed
```

## 34.4 Trainee

التقييم لا يظهر له قبل إكمال الدورة.

بعد الإكمال يرى:

```text
his enrollment
his evaluation
```

ولا يرى تقييم طالب آخر.

---

# 35. Business Rules للتقارير

عند إنشاء Report:

```text
1. Verify authenticated user
2. Verify onsite trainer
3. Verify trainer assigned to course
4. Verify course is not completed
5. Validate hours > 0
6. Calculate current remaining hours
7. Reject if hours_done > remaining_hours
8. Save report
9. Recalculate course progress
10. Complete course if remaining == 0
11. Complete active enrollments if course completed
12. Commit transaction
```

عند Update أو Delete Report يعاد الحساب بنفس الطريقة.

---

# 36. Business Rules للـ Evaluation

عند Create:

```text
1. Enrollment exists
2. Enrollment is active
3. Trainer is onsite
4. Trainer teaches the course
5. Trainer is assigned to the trainee in the course
6. Grade is valid A/B/C/D
```

عند Update:

```text
Course is not completed
```

أو:

```text
Current user is Course Manager
```

إذا كانت الدورة مكتملة والمدرب حاول التعديل:

```text
AuthorizationError / BusinessRuleError
```

---

# 37. Validation

Validation تنقسم إلى مستويين.

## Input Validation

مثل:

```text
name non-empty
age integer
email valid format
hours integer
hours > 0
```

## Business Validation

مثل:

```text
trainer assigned
course active
trainee not already active in another course
report does not exceed remaining hours
trainer cannot edit completed evaluation
```

لا نخلط النوعين في ملف واحد ضخم.

---

# 38. Exceptions

```text
AppException
├── ValidationError
├── AuthenticationError
├── AuthorizationError
├── NotFoundError
├── DuplicateError
├── BusinessRuleError
└── StorageError
```

### أمثلة

```text
ValidationError:
Age must be a positive integer.

DuplicateError:
Username already exists.

AuthorizationError:
Trainer is not assigned to this trainee.

BusinessRuleError:
Reported hours exceed remaining course hours.

NotFoundError:
Course C001 was not found.

StorageError:
Unable to save database.
```

---

# 39. Logging

الملف:

```text
logs/app.log
```

نسجل الأحداث المهمة:

```text
LOGIN_SUCCESS
LOGIN_FAILED
CREATE_TRAINEE
UPDATE_TRAINEE
CREATE_COURSE
ENROLL_TRAINEE
ASSIGN_TRAINER
CREATE_REPORT
UPDATE_REPORT
DELETE_REPORT
COURSE_COMPLETED
CREATE_EVALUATION
UPDATE_EVALUATION
UNAUTHORIZED_ACTION
STORAGE_ERROR
```

لا نسجل:

```text
plaintext passwords
password hashes in normal informational logs
```

---

# 40. Password Hashing

يستخدم:

```text
salt + standard-library password derivation
```

والـ CLI يأخذ كلمة المرور من `getpass` بدل طباعتها.

المهم في V1:

```text
No plaintext passwords in database.
```

---

# 41. Session

بعد Login ننشئ Session تحتوي:

```text
current_user
login_time
```

والـ menus تقرأ Session بدل تمرير المستخدم يدويًا بين كل وظيفة.

---

# 42. CLI Architecture

```text
main.py
   ↓
bootstrap.py
   ↓
CLI App
   ↓
Session
   ↓
Role Menu
   ↓
Use Case
   ↓
Application services
   ↓
Repository
   ↓
JSON infrastructure
```

## Manager Menu

```text
1. Trainees
2. Trainers
3. Courses
4. Enrollments
5. Assignments
6. Reports
7. Evaluations
8. Logout
```

## Onsite Trainer Menu

```text
1. My Courses
2. My Trainees
3. Reports
4. Evaluations
5. View Course
6. Logout
```

## Remote Trainer Menu

```text
1. My Courses
2. My Students
3. Reports
4. Course Details
5. Logout
```

## Trainee Menu

```text
1. My Current Course
2. Course Details
3. Daily Reports
4. My Evaluation
5. Logout
```

---

# 43. Dependency Flow

القاعدة:

```text
Presentation
      ↓
Application
      ↓
Domain
```

Infrastructure تنفذ abstractions المطلوبة من Application/Domain.

لا يوجد:

```text
Domain -> JSON
Domain -> CLI
Domain -> pytest
Domain -> filesystem path
```

ولا:

```text
CLI -> database.json
```

---

# 44. Bootstrap و Dependency Injection

لن نستخدم DI Container خارجي.

`bootstrap.py` ينشئ الاعتماديات مرة واحدة:

```text
JsonDatabase
JsonUnitOfWork
JsonRepositories
AuthorizationService
CourseProgressService
Use Cases
CLI App
```

هذا هو Dependency Injection يدوي بسيط ومناسب لحجم المشروع.

---

# 45. DTOs

في V1 يكفي ملف:

```text
application/dto/requests.py
```

يحتوي Requests التي تفصل CLI input عن Domain Entities عندما نحتاج ذلك.

لا ننشئ عشرات DTO files.

مثال:

```text
CreateTraineeRequest
CreateCourseRequest
CreateDailyReportRequest
CreateEvaluationRequest
LoginRequest
```

---

# 46. لماذا لا نضع Input Validation داخل CLI فقط؟

لأن CLI ليس مصدر الحقيقة.

حتى لو أخطأ CLI أو استُدعيت Use Case من اختبار، يجب أن تبقى Business Rules صحيحة.

إذن:

```text
CLI validates format
Use Case validates business conditions
Domain protects its own invariants
```

---

# 47. Test Strategy

لا نختبر كل getter.

نختبر القواعد ذات المخاطر.

## Unit Tests

```text
Entity validation
Serializer
Generic repository
Authorization
Course progress
```

## Integration Tests

```text
Login -> action -> JSON persistence
Create report -> progress update
Complete course -> enrollment completion
Evaluation lock
```

---

# 48. Minimum Acceptance Tests

يجب أن تنجح السيناريوهات التالية:

```text
1. Create trainee
2. Prevent duplicate trainee ID
3. Create trainer
4. Create course
5. Assign trainer to course
6. Assign trainee to onsite trainer
7. Enroll trainee
8. Prevent second active enrollment
9. Create daily report
10. Update remaining hours automatically
11. Reject report larger than remaining hours
12. Complete course automatically
13. Complete enrollment automatically
14. Create evaluation before completion
15. Edit evaluation by authorized onsite trainer
16. Block trainer evaluation update after completion
17. Allow manager to correct completed evaluation
18. Hide incomplete evaluation from trainee
19. Show own evaluation after completion
20. Reject unauthorized actions
```

---

# 49. تشغيل الاختبارات

```bash
pytest
```

أو:

```bash
python -m pytest -q
```

الاختبار يجب أن ينتج نجاحًا واضحًا قبل الدمج إلى `main`.

---

# 50. Git Strategy

الفروع:

```text
main
feature/domain
feature/infrastructure
feature/application
feature/cli
feature/testing-docs
```

لا يعمل الأعضاء مباشرة على `main`.

## Commit examples

```text
feat(domain): add person and trainee entities
feat(domain): add trainer and course entities
feat(infrastructure): add json database
feat(infrastructure): add generic repository
feat(application): add enrollment workflow
feat(application): add authorization rules
feat(cli): add trainer menu
fix(report): reject excessive hours
test(progress): cover course completion
docs(project): add technical design
```

---

# 51. Git Ignore

يجب أن يتضمن `.gitignore` على الأقل:

```text
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.vscode/
.idea/
*.log
```

`data/database.json` يبقى tracked في V1 إذا كان يحتوي بيانات demo مستقرة؛ اختبارات التكامل يجب أن تعمل على ملف مؤقت أو نسخة معزولة، لا على ملف المشروع الحقيقي.

---

# 52. Linux Work

يجب تنفيذ وتصوير جزء من المشروع على Linux، مثل:

```bash
pwd
ls -la
find app -type f
find tests -type f
chmod +x scripts/*  # فقط إذا استخدمت scripts قابلة للتنفيذ
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pytest -q
python main.py
```

لا نضيف أوامر Linux لمجرد التقرير؛ يجب أن تكون مرتبطة فعليًا ببناء المشروع وتشغيله.

---

# 53. Vibe Coding Policy

Vibe Coding يستخدم لتنفيذ وحدات محددة بعد تثبيت التصميم.

## مناسب للـ AI

```text
Generic JsonRepository
Serializer helpers
CLI formatting
repetitive DTO definitions
seed/demo data
unit tests after rules are defined
README formatting
refactoring duplicate code
```

## لا يُفوّض بالكامل للـ AI

```text
Domain model
Relationships
Business rules
Authorization model
Evaluation locking policy
Enrollment lifecycle
Final architecture
Integration decisions
Final code review
```

## Prompt boundary

يجب أن يكون طلب AI محددًا مثل:

```text
Implement only the generic JsonRepository according to the existing Repository[T] contract.
Do not change domain entities.
Do not add third-party dependencies.
Do not add business rules.
Return the complete file.
```

ثم يراجع عضو الفريق الكود قبل الدمج.

---

# 54. Team Boundaries

## Member 1 — Domain

يتولى:

```text
entities
Enums
Exceptions
repository contracts
```

لا يغيّر CLI أو JSON implementation.

## Member 2 — Infrastructure

يتولى:

```text
JsonDatabase
Serializer
JsonRepository
UnitOfWork
PasswordHasher
Logger
```

لا يكتب Business Rules.

## Member 3 — Application

يتولى:

```text
Use Cases
Authorization
Course Progress
DTOs
```

يعتمد على contracts ويستخدم Infrastructure عبر Dependency Injection.

## Member 4 — Presentation

يتولى:

```text
CLI
Session
menus
input/display
```

لا يضع قواعد الصلاحيات داخل القوائم فقط؛ Use Cases هي الحماية النهائية.

## Member 5 — QA / Integration / Git / Documentation

يتولى:

```text
tests
integration
Git branches
GitHub PRs
Linux screenshots
final demo
README
```

ويبدأ من أول ساعة بإنشاء test scenarios.

---

# 55. Work Isolation Rules

لتقليل التعارض:

```text
Member 1 -> app/domain/**
Member 2 -> app/infrastructure/**
Member 3 -> app/application/**
Member 4 -> app/presentation/**
Member 5 -> tests/** + docs/** + screenshots/** + README.md
```

الملفات المشتركة الحساسة:

```text
main.py
app/bootstrap.py
requirements-dev.txt
.gitignore
```

يعدلها شخص واحد فقط بعد التنسيق، ويفضل العضو 5 بالتنسيق مع العضوين 1 و2.

---

# 56. Implementation Order

الترتيب النهائي:

```text
Phase 0
Environment + Git + folders

Phase 1
Domain entities + enums + exceptions

Phase 2
JSON database + serializer + generic repository

Phase 3
Unit of Work + specialized repository queries

Phase 4
Authorization + progress service

Phase 5
Use Cases

Phase 6
CLI + Session + menus

Phase 7
Unit tests

Phase 8
Integration workflow

Phase 9
GitHub merge + Linux execution + screenshots

Phase 10
Final demo + README
```

لا يبدأ بناء CLI الكامل قبل تثبيت Use Case contracts الأساسية.

---

# 57. Main Demo Scenario

```text
Manager Login
   ↓
Create Course C001
   ↓
Create Trainer TR001 (ONSITE)
   ↓
Create Trainer TR002 (REMOTE)
   ↓
Create Trainees T001/T002
   ↓
Assign TR001/TR002 to C001
   ↓
Assign T001/T002 to TR001
   ↓
Enroll T001/T002 in C001
   ↓
Trainer TR001 submits 5 hours
   ↓
Course shows 5 completed
   ↓
Trainer adds evaluation for T001
   ↓
More reports
   ↓
Course reaches total hours
   ↓
Course becomes COMPLETED
   ↓
Enrollments become COMPLETED
   ↓
Trainer attempts evaluation edit
   ↓
System rejects
   ↓
Trainee T001 logs in
   ↓
Own evaluation becomes visible
   ↓
Manager corrects evaluation
   ↓
Final report/demo
```

---

# 58. Screenshot Plan

## Environment

```text
Python version
venv creation
pytest version
```

## Project setup

```text
folders
file tree
```

## Git/GitHub

```text
git init
git status
branch
commit
remote
push
GitHub repository
```

## Architecture

```text
final tree
architecture diagram
JSON structure
```

## Vibe Coding

```text
prompt
AI-generated bounded implementation
human review
commit after review
```

## CLI

```text
login
manager menu
trainer menu
trainee menu
```

## Business Rules

```text
duplicate ID rejected
unauthorized trainer rejected
excessive hours rejected
evaluation locked
```

## Tests

```text
pytest -q
```

## Final demo

```text
course progress
course completion
evaluation visibility
manager correction
```

---

# 59. Clean Code Rules

1. لا Magic Strings للحالات والأدوار.
2. استخدام Type Hints في الدوال والكلاسات المهمة.
3. أسماء واضحة للمتغيرات والدوال.
4. الدوال الصغيرة ذات هدف واحد.
5. لا تكرار CRUD في كل Repository.
6. لا تكرار validation المشترك.
7. لا Business Logic داخل CLI.
8. لا File I/O داخل Domain.
9. لا استدعاء `open()` في Use Cases.
10. لا استخدام `except Exception` بشكل عام إلا عند حدود التطبيق لتسجيل الخطأ وتحويله إلى رسالة مناسبة.
11. لا ملفات ضخمة؛ عند نمو module بشكل غير معقول يُقسم حسب مسؤولية واضحة.
12. لا إضافة Design Pattern بدون مشكلة حقيقية يحلها.

---

# 60. نقاط التوسع المستقبلية

هذا التصميم يسمح لاحقًا بإضافة:

```text
SQLite/PostgreSQL
REST API
Web UI
more roles
attendance
certificates
payments
notifications
advanced reports
search/filtering
```

من دون تعديل Domain Rules جذريًا.

الاستبدال المستقبلي يتركز أساسًا في Infrastructure:

```text
JsonRepository
        ↓
SqlRepository
```

مع الحفاظ على Use Cases قدر الإمكان.

---

# 61. قرارات V2 التي يجب عدم تغييرها أثناء التنفيذ إلا باتفاق الفريق

```text
1. One JSON file.
2. BaseEntity -> Person -> Trainee/Trainer inheritance.
3. Enrollment as an independent entity.
4. Evaluation linked to Enrollment.
5. Generic CRUD Repository.
6. Specialized repositories only for real queries.
7. Course progress derived from reports.
8. Unit of Work for multi-entity changes.
9. Central authorization service.
10. Separate Role and TrainingMethod.
11. No business rules in CLI.
12. No third-party runtime dependencies.
13. pytest as development dependency.
14. No hard deletion of academic history in normal flows.
15. One active enrollment per trainee.
16. Trainer scope is course/assignment-based.
17. Evaluation is locked for trainers after course completion.
18. Course Manager can correct completed evaluations.
```

---

# 62. Definition of Done

يعتبر المشروع جاهزًا عندما:

```text
[ ] Virtual environment works
[ ] pytest installed
[ ] Git repository configured
[ ] Clean Architecture tree exists
[ ] Entities implemented
[ ] JSON storage implemented
[ ] Generic Repository implemented
[ ] Serializer tested
[ ] Unit of Work works
[ ] Authentication works
[ ] Authorization works
[ ] Enrollment rules work
[ ] Reports update progress automatically
[ ] Course completion works
[ ] Evaluation locking works
[ ] CLI roles work
[ ] Tests pass
[ ] Linux execution demonstrated
[ ] GitHub history is clean
[ ] Screenshots collected
[ ] README explains setup and demo
[ ] Final end-to-end demo succeeds
```

---

# 63. الخلاصة المعمارية

الهيكل النهائي هو:

```text
                    Presentation
                         CLI
                          │
                          ▼
                    Application
                   Use Cases
                   Services
                   UnitOfWork
                          │
                          ▼
                       Domain
              Entities / Enums / Rules
                    Repository APIs
                          │
                          ▼
                   Infrastructure
                JSON / Serializer
                Generic Repository
                Logging / Auth
                          │
                          ▼
                    database.json
```

والـ Domain model:

```text
                         BaseEntity
                             │
              ┌──────────────┼──────────────┐
              │              │              │
           Person          Course          User
              │
         ┌────┴────┐
         │         │
      Trainee   Trainer

Trainee ───── Enrollment ───── Course
                 │
                 └──── Evaluation

Trainer ── CourseTrainerAssignment ── Course

Trainer ── TrainerTraineeAssignment ── Trainee
                 │
               Course

Trainer ───── DailyReport ───── Course
```

هذه هي الـ baseline المعتمدة قبل كتابة implementation code.
