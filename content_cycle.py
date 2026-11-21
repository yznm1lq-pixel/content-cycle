"""
دورة المحتوى | Content Cycle
أداة بسيطة لمتابعة رحلة إنتاج المحتوى وتحليل تدفق العمل.
"""

import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).with_name("contents.json")

STAGES = [
    "الفكرة",
    "التخطيط",
    "الكتابة",
    "المراجعة",
    "التصميم",
    "الاعتماد",
    "النشر",
    "الأرشفة",
]

PUBLISHED_STAGES = {"النشر", "الأرشفة"}


def now():
    """Return the current local date and time in ISO format."""
    return datetime.now().isoformat(timespec="seconds")


def load_contents():
    """Load content records from the JSON data file."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            print("تحذير: تنسيق ملف البيانات غير صحيح. سيتم بدء قائمة فارغة.")
            return []
        return data
    except (json.JSONDecodeError, OSError):
        print("تعذر قراءة contents.json. تحقق من الملف ثم أعد التشغيل.")
        return []


def save_contents(contents):
    """Save all content records to the JSON data file."""
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(contents, file, ensure_ascii=False, indent=4)


def next_id(contents):
    """Generate a unique numeric ID."""
    return max((item.get("id", 0) for item in contents), default=0) + 1


def add_content(contents):
    """Add a new item to the content production cycle."""
    print("\n--- إضافة محتوى جديد ---")
    title = input("عنوان المحتوى: ").strip()
    if not title:
        print("لم تتم الإضافة: العنوان مطلوب.")
        return

    content_type = input("نوع المحتوى (مقال/منشور/تقرير...): ").strip()
    if not content_type:
        content_type = "عام"

    timestamp = now()
    item = {
        "id": next_id(contents),
        "title": title,
        "type": content_type,
        "stage": STAGES[0],
        "created_at": timestamp,
        "updated_at": timestamp,
        "published_at": None,
    }

    contents.append(item)
    save_contents(contents)
    print(f"تمت إضافة المحتوى بنجاح. رقم المحتوى: {item['id']}")


def display_contents(contents):
    """Display all registered content items."""
    print("\n--- قائمة المحتوى ---")
    if not contents:
        print("لا يوجد محتوى مسجل حتى الآن.")
        return

    for item in contents:
        print(
            f"#{item['id']} | {item['title']} | النوع: {item['type']} "
            f"| المرحلة: {item['stage']}"
        )


def update_stage(contents):
    """Move a content item to a selected production stage."""
    if not contents:
        print("لا يوجد محتوى لتحديثه.")
        return

    display_contents(contents)
    try:
        content_id = int(input("\nأدخل رقم المحتوى المراد تحديثه: "))
    except ValueError:
        print("الرجاء إدخال رقم صحيح.")
        return

    item = next((record for record in contents if record["id"] == content_id), None)
    if item is None:
        print("لم يتم العثور على هذا المحتوى.")
        return

    print("\nمراحل دورة المحتوى:")
    for number, stage in enumerate(STAGES, start=1):
        print(f"{number}. {stage}")

    try:
        choice = int(input("اختر رقم المرحلة الجديدة: "))
        if not 1 <= choice <= len(STAGES):
            raise ValueError
    except ValueError:
        print("اختيار غير صحيح.")
        return

    new_stage = STAGES[choice - 1]
    item["stage"] = new_stage
    item["updated_at"] = now()
    item["published_at"] = (
        item["updated_at"] if new_stage in PUBLISHED_STAGES else None
    )

    save_contents(contents)
    print(f"تم تحديث مرحلة «{item['title']}» إلى: {new_stage}")


def show_report(contents):
    """Show basic production and flow indicators."""
    total = len(contents)
    completed = sum(item["stage"] in PUBLISHED_STAGES for item in contents)
    work_in_progress = total - completed

    print("\n========== تقرير دورة المحتوى ==========")
    print(f"إجمالي المحتويات: {total}")
    print(f"قيد الإنتاج: {work_in_progress}")
    print(f"منشور أو مؤرشف: {completed}")

    if total:
        completion_rate = completed / total * 100
        print(f"نسبة الوصول إلى النشر: {completion_rate:.1f}%")

    active_items = [item for item in contents if item["stage"] not in PUBLISHED_STAGES]
    stage_counts = {
        stage: sum(item["stage"] == stage for item in active_items)
        for stage in STAGES[:-2]
    }

    if active_items:
        busiest_stage = max(stage_counts, key=stage_counts.get)
        busiest_count = stage_counts[busiest_stage]
        print(f"أعلى مرحلة من حيث عدد المحتويات الحالية: {busiest_stage} ({busiest_count})")
        print("ملاحظة: هذا مؤشر ازدحام لحظي، وليس قياساً نهائياً لعنق الزجاجة.")

    cycle_times = []
    for item in contents:
        if item.get("published_at"):
            try:
                start = datetime.fromisoformat(item["created_at"])
                end = datetime.fromisoformat(item["published_at"])
                cycle_times.append((end - start).total_seconds() / 86400)
            except (KeyError, TypeError, ValueError):
                continue

    if cycle_times:
        average_days = sum(cycle_times) / len(cycle_times)
        print(f"متوسط زمن الدورة للمحتويات المنشورة: {average_days:.2f} يوم")

    print("========================================")


def main():
    """Run the Content Cycle application."""
    contents = load_contents()

    while True:
        print("\n===== دورة المحتوى | Content Cycle =====")
        print("1. إضافة محتوى جديد")
        print("2. عرض المحتوى")
        print("3. تحديث مرحلة الإنتاج")
        print("4. تقرير الإنتاج")
        print("5. خروج")

        choice = input("اختر العملية: ").strip()

        if choice == "1":
            add_content(contents)
        elif choice == "2":
            display_contents(contents)
        elif choice == "3":
            update_stage(contents)
        elif choice == "4":
            show_report(contents)
        elif choice == "5":
            print("شكراً لاستخدام دورة المحتوى.")
            break
        else:
            print("اختيار غير صحيح. حاول مرة أخرى.")


if __name__ == "__main__":
    main()
