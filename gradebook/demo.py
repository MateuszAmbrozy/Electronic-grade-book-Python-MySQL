"""Fictional demo data, created only for an empty local demo database."""

from datetime import date, timedelta
from gradebook.service import Gradebook

DEMO_PASSWORD = "Portfolio2026!"


def seed_demo(db):
    if db.execute("SELECT id FROM users LIMIT 1"):
        return
    service = Gradebook(db)
    service.bootstrap("Morgan", "Reed", "admin@gradebook.demo", DEMO_PASSWORD)
    service.login("admin@gradebook.demo", DEMO_PASSWORD)
    teacher = service.create_user("Alex", "Taylor", "teacher@gradebook.demo", DEMO_PASSWORD, "TEACHER")
    student = service.create_user("Jamie", "Parker", "student@gradebook.demo", DEMO_PASSWORD, "STUDENT", "2A")
    other = service.create_user("Sam", "Bennett", "sam@gradebook.demo", DEMO_PASSWORD, "STUDENT", "2A")
    service.create_user("Riley", "Morgan", "riley@gradebook.demo", DEMO_PASSWORD, "STUDENT", "2B")
    subjects = ("Mathematics", "Computer Science", "Physics")
    lessons = []
    for weekday in range(5):
        for index, subject in enumerate(subjects):
            lessons.append(
                service.add_lesson(
                    subject, "2A", teacher, weekday, f"{9 + index:02}:00", f"{9 + index:02}:45", f"Room {201 + index}"
                )
            )
    service.logout()
    service.login("teacher@gradebook.demo", DEMO_PASSWORD)
    today = date.today()
    for index in range(9):
        on_date = (today - timedelta(days=index + 1)).isoformat()
        for student_id in (student, other):
            service.add_grade(student_id, subjects[index % 3], (4, 5, 6, 4.5)[index % 4], (1, 2, 3)[index % 3], on_date)
    for offset in range(1, 15):
        on_date = today - timedelta(days=offset)
        if on_date.weekday() < 5:
            lesson_id = lessons[on_date.weekday() * 3]
            service.mark_attendance(
                student,
                lesson_id,
                on_date.isoformat(),
                "ABSENT" if offset == 3 else "LATE" if offset == 5 else "PRESENT",
            )
    service.send_message(
        "student@gradebook.demo",
        "Your next chapter starts here",
        "Welcome to Gradebook, Jamie! Your timetable, grades, and attendance are all available in one place. If you have a question about a lesson, send me a message.",
    )
    service.send_message(
        "admin@gradebook.demo",
        "Class 2A: weekly update",
        "The new timetable is ready and this week's grades have been recorded. Class 2A is making good progress with the programming module.",
    )
    service.logout()
    service.login("admin@gradebook.demo", DEMO_PASSWORD)
    service.send_message(
        "student@gradebook.demo",
        "Welcome to the new term",
        "Your school account is ready. Use the Account page to change your password. Have a great term!",
    )
    service.send_message(
        "teacher@gradebook.demo",
        "Timetable confirmed",
        "The weekly timetable for Class 2A has been confirmed. Thank you for preparing the course materials.",
    )
    service.logout()
