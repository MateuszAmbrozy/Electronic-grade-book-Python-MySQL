"""Regression tests for authorization, validation, and persistence."""

from datetime import date, timedelta
import unittest

from gradebook.database import Database
from gradebook.demo import DEMO_PASSWORD, seed_demo
from gradebook.security import hash_password, verify_password
from gradebook.service import Gradebook, weighted_average


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.db = Database.sqlite()
        self.db.initialize()
        self.service = Gradebook(self.db)
        self.admin = self.service.bootstrap("Admin", "Reed", "admin@test.example", DEMO_PASSWORD)
        self.service.login("admin@test.example", DEMO_PASSWORD)
        self.teacher = self.service.create_user("Alex", "Taylor", "teacher@test.example", DEMO_PASSWORD, "TEACHER")
        self.other_teacher = self.service.create_user("Robin", "White", "other@test.example", DEMO_PASSWORD, "TEACHER")
        self.student = self.service.create_user(
            "Jamie", "Parker", "student@test.example", DEMO_PASSWORD, "STUDENT", "2A"
        )
        self.other_student = self.service.create_user(
            "Jamie", "Parker", "otherstudent@test.example", DEMO_PASSWORD, "STUDENT", "2B"
        )
        self.lesson = self.service.add_lesson("Mathematics", "2A", self.teacher, 0, "09:00", "09:45", "Room 1")
        self.monday = date.today() - timedelta(days=date.today().weekday())

    def tearDown(self):
        self.db.close()

    def login(self, role):
        self.service.login(f"{role}@test.example", DEMO_PASSWORD)

    def test_password_hashes_are_salted_and_verified(self):
        first, second = hash_password(DEMO_PASSWORD), hash_password(DEMO_PASSWORD)
        self.assertNotEqual(first, second)
        self.assertTrue(verify_password(first, DEMO_PASSWORD))
        self.assertFalse(verify_password(first, "incorrect"))
        self.assertFalse(verify_password("broken", DEMO_PASSWORD))
        with self.assertRaises(ValueError):
            hash_password("short")

    def test_failed_login_clears_existing_session(self):
        with self.assertRaises(ValueError):
            self.service.login("admin@test.example' OR 1=1 --", "bad")
        with self.assertRaises(PermissionError):
            self.service.users()

    def test_student_cannot_escalate_or_read_namesake_records(self):
        self.service.add_grade(self.other_student, "Physics", 6, 1, date.today().isoformat())
        self.login("student")
        self.assertEqual(self.service.grades(), [])
        self.assertEqual(self.service.attendance(), [])
        self.assertEqual(len(self.service.lessons()), 1)
        with self.assertRaises(PermissionError):
            self.service.create_user("New", "Admin", "new@test.example", DEMO_PASSWORD, "HEADTEACHER")
        with self.assertRaises(PermissionError):
            self.service.add_grade(self.student, "Mathematics", 5, 1, date.today().isoformat())

    def test_teacher_scope_is_enforced_on_writes_and_deletes(self):
        self.login("teacher")
        grade = self.service.add_grade(self.student, "Mathematics", 5, 2, date.today().isoformat())
        self.assertEqual([s["id"] for s in self.service.students()], [self.student])
        with self.assertRaises(PermissionError):
            self.service.add_grade(self.other_student, "Mathematics", 5, 1, date.today().isoformat())
        with self.assertRaises(PermissionError):
            self.service.add_grade(self.student, "Physics", 5, 1, date.today().isoformat())
        self.login("other")
        self.assertEqual(self.service.grades(), [])
        with self.assertRaises(PermissionError):
            self.service.delete_grade(grade)
        self.login("teacher")
        self.service.delete_grade(grade)
        self.assertEqual(self.service.grades(), [])

    def test_invalid_grades_never_persist(self):
        self.login("teacher")
        for grade, weight in [(0, 1), (7, 1), ("nan", 1), ("inf", 1), (5, 0), (5, 11), (5, "1.5"), ("bad", 1)]:
            with self.subTest(grade=grade, weight=weight), self.assertRaises(ValueError):
                self.service.add_grade(self.student, "Mathematics", grade, weight, date.today().isoformat())
        self.assertEqual(self.service.grades(), [])

    def test_weighted_average(self):
        self.assertEqual(weighted_average([{"grade": 6, "weight": 1}, {"grade": 2, "weight": 3}]), 3)
        self.assertIsNone(weighted_average([]))

    def test_schedule_conflicts_for_teacher_class_and_room(self):
        scenarios = [
            ("2B", self.teacher, "Room 2"),
            ("2A", self.other_teacher, "Room 2"),
            ("2B", self.other_teacher, "Room 1"),
        ]
        for class_name, teacher, room in scenarios:
            with self.subTest(class_name=class_name, teacher=teacher, room=room), self.assertRaises(ValueError):
                self.service.add_lesson("Physics", class_name, teacher, 0, "09:30", "10:15", room)
        self.service.add_lesson("Physics", "2A", self.teacher, 0, "09:45", "10:30", "Room 1")
        self.assertEqual(len(self.service.lessons()), 2)

    def test_attendance_updates_without_duplicates_and_preserves_lesson(self):
        self.login("teacher")
        self.service.mark_attendance(self.student, self.lesson, self.monday.isoformat(), "ABSENT")
        self.service.mark_attendance(self.student, self.lesson, self.monday.isoformat(), "PRESENT")
        records = self.service.attendance()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["status"], "PRESENT")
        self.login("other")
        with self.assertRaises(PermissionError):
            self.service.delete_attendance(records[0]["id"])
        self.login("admin")
        with self.assertRaises(ValueError):
            self.service.delete_lesson(self.lesson)
        self.login("student")
        self.assertEqual(len(self.service.attendance()), 1)

    def test_attendance_rejects_wrong_class_day_and_status(self):
        self.login("admin")
        with self.assertRaises(ValueError):
            self.service.mark_attendance(self.other_student, self.lesson, self.monday.isoformat(), "PRESENT")
        wrong_day = self.monday - timedelta(days=1)
        with self.assertRaises(ValueError):
            self.service.mark_attendance(self.student, self.lesson, wrong_day.isoformat(), "PRESENT")
        with self.assertRaises(ValueError):
            self.service.mark_attendance(self.student, self.lesson, self.monday.isoformat(), "UNKNOWN")

    def test_messages_are_private_and_ordered_newest_first(self):
        self.service.send_message("student@test.example", "First", "Hello Jamie")
        self.service.send_message("student@test.example", "Second", "Follow-up")
        self.login("student")
        self.assertEqual([r["subject"] for r in self.service.messages()], ["Second", "First"])
        self.login("otherstudent")
        self.assertEqual(self.service.messages(), [])
        with self.assertRaises(ValueError):
            self.service.send_message("missing@test.example", "Subject", "Body")
        with self.assertRaises(ValueError):
            self.service.send_message("admin@test.example", "", "Body")

    def test_deactivation_preserves_history_and_revokes_session(self):
        self.login("teacher")
        self.service.add_grade(self.student, "Mathematics", 4, 1, date.today().isoformat())
        session = Gradebook(self.db)
        session.login("student@test.example", DEMO_PASSWORD)
        self.login("admin")
        self.service.deactivate_user(self.student)
        self.assertEqual(len(self.service.grades()), 1)
        with self.assertRaises(PermissionError):
            _ = session.user
        with self.assertRaises(ValueError):
            session.login("student@test.example", DEMO_PASSWORD)
        with self.assertRaises(ValueError):
            self.service.deactivate_user(self.admin)

    def test_password_change_works_twice_without_relogin(self):
        self.login("student")
        self.service.change_password(DEMO_PASSWORD, "AnotherPassword123!")
        self.service.change_password("AnotherPassword123!", "ThirdPassword123!")
        self.service.login("student@test.example", "ThirdPassword123!")
        with self.assertRaises(ValueError):
            self.service.change_password(DEMO_PASSWORD, "FourthPassword123!")

    def test_transaction_rolls_back_all_changes(self):
        with self.assertRaises(RuntimeError):
            with self.db.transaction():
                self.db.execute("UPDATE users SET first_name = ? WHERE id = ?", ("Changed", self.student))
                raise RuntimeError("Simulated failure")
        self.assertEqual(
            self.db.execute("SELECT first_name FROM users WHERE id = ?", (self.student,))[0]["first_name"], "Jamie"
        )

    def test_future_dates_and_duplicate_emails_are_rejected(self):
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        with self.assertRaises(ValueError):
            self.service.add_grade(self.student, "Mathematics", 5, 1, tomorrow)
        with self.assertRaises(ValueError):
            self.service.create_user("Other", "User", "STUDENT@TEST.EXAMPLE", DEMO_PASSWORD, "STUDENT", "2A")
        with self.assertRaises(ValueError):
            self.service.bootstrap("Other", "Admin", "new@test.example", DEMO_PASSWORD)


class DemoTests(unittest.TestCase):
    def test_seed_is_repeatable_without_duplicate_records(self):
        db = Database.sqlite()
        try:
            db.initialize()
            seed_demo(db)
            seed_demo(db)
            service = Gradebook(db)
            service.login("student@gradebook.demo", DEMO_PASSWORD)
            self.assertEqual(len(service.lessons()), 15)
            self.assertEqual(len(service.grades()), 9)
            self.assertEqual(len(service.messages()), 2)
            self.assertGreater(len(service.attendance()), 0)
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
