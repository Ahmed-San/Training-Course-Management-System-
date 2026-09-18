# TCMS V2 — M5 Transfer Manifest

هذه الحزمة تحتوي M5 جاهزًا للنقل إلى جذر المشروع، مع فصل واضح بين الملفات التي يملكها M5 والملف المشترك الخاص باختبارات التكامل.

## 1. ملفات M5 المملوكة — قابلة للنقل مباشرة

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

docs/M5_EXECUTION_GUIDE_AR.md
docs/M5_COMPLETION_REPORT_AR.md
```

انسخ هذه الملفات فوق النسخ الموجودة في المشروع الرئيسي.

## 2. ملف التكامل المشترك

```text
tests/integration/test_workflows.py
```

هذا الملف يجمع سيناريوهات M1–M5، لذلك **لا تستبدله يدويًا فوق نسخة أحدث من مشروعك** إذا كان M4 أضاف اختبارات مختلفة.

الطريقة الآمنة:

```bash
git apply --3way TCMS_V2_M5_CHANGESET.patch
```

أو طبّق الجزء الخاص بـM5 من الـpatch بعد مراجعة التعارضات.

## 3. Integration Wiring

في النسخة التي تم اختبارها، تسجيل M5 موجود بالفعل في:

```text
app/bootstrap.py
app/application/unit_of_work.py
```

ويجب التأكد أن مشروعك الرئيسي يملك:

```text
evaluation use cases في AppContainer
 evaluation_repository في UnitOfWork
 JsonEvaluationRepository في نقطة التكوين
```

إذا كانت هذه العقود غير موجودة في مشروعك بعد M4، لا تستبدل `bootstrap.py` أو `UnitOfWork` بالكامل دون مراجعة تغييرات M4؛ أضف نقطة الربط الخاصة بـM5 فقط.

## 4. لا تلمس ملفات الشرائح الأخرى لإجبار الدمج

```text
M1
M2
M3
M4
```

خصوصًا ملفات Domain أو Infrastructure المملوكة لهم.

## 5. التحقق بعد النقل

```bash
python -m pytest -q
python -m compileall -q app main.py
git diff --check
git status
```

ثم:

```bash
python main.py
```

## 6. الفرع

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/m5-evaluation-cli-integration
```

إذا كان الفرع موجودًا:

```bash
git switch feature/m5-evaluation-cli-integration
git pull origin feature/m5-evaluation-cli-integration
```

## 7. Commit مقترح

```bash
git add app/domain/entities/evaluation.py app/application/use_cases/evaluations.py
git commit -m "feat(m5): implement evaluation domain and use cases"

git add app/presentation/cli tests/unit docs/M5_EXECUTION_GUIDE_AR.md docs/M5_COMPLETION_REPORT_AR.md M5_TRANSFER_MANIFEST_AR.md
git commit -m "feat(m5): integrate arabic cli and release tests"
```

إذا استخدمت `git apply` للـpatch بدل النسخ، قد لا تحتاج إعادة بناء نفس الـcommits؛ راجع `git diff` أولًا.

## 8. Push

```bash
git push -u origin feature/m5-evaluation-cli-integration
```

## 9. Pull Request

```text
feat(m5): complete evaluation, CLI, integration and release
```

يذكر الـPR:

```text
Evaluation lifecycle
Authorization and scope
Arabic CLI
Unit and integration tests
Dependencies on M1/M2/M3/M4
pytest result
compileall result
architecture result
```
