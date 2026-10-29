"""Application rules and authorization, independent of desktop widgets."""

from datetime import date, datetime
import re

from gradebook.security import hash_password, verify_password

ROLES = ("STUDENT", "TEACHER", "HEADTEACHER")
DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")
STATUSES = ("PRESENT", "LATE", "ABSENT")


def required(value, label, limit=80):
    value = str(value).strip()
    if not value or len(value) > limit:
        raise ValueError(f"{label} is required and must contain at most {limit} characters.")
    return value


def email_address(value):
    value = required(value, "Email", 254).lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
        raise ValueError("Enter a valid email address.")
    return value


def record_date(value):
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Enter a valid date in YYYY-MM-DD format.") from exc
    if parsed > date.today():
        raise ValueError("Grades and attendance cannot be recorded in the future.")
    return parsed.isoformat()


class Gradebook:
    def __init__(self, db):
        self.db = db
        self._user_id = None

    @property
    def user(self):
        if self._user_id is None:
            raise PermissionError("Sign in to continue.")
        users = self.db.execute(
            "SELECT id, first_name, last_name, email, role, class_name FROM users WHERE id = ? AND active = 1",
            (self._user_id,),
        )
        if not users:
            self.logout()
            raise PermissionError("This account is inactive.")
        return users[0]

    def require(self, *roles):
        user = self.user
        if user["role"] not in roles:
            raise PermissionError("Your account does not have permission to perform this action.")
        return user

    def login(self, email, password):
        self.logout()
        users = self.db.execute("SELECT * FROM users WHERE email = ? AND active = 1", (email.strip().lower(),))
        if not users or not verify_password(users[0]["password_hash"], password):
            raise ValueError("The email or password is incorrect.")
        self._user_id = users[0]["id"]
        return self.user

    def logout(self):
        self._user_id = None

    def create_user(self, first_name, last_name, email, password, role, class_name=""):
        self.require("HEADTEACHER")
        return self._insert_user(first_name, last_name, email, password, role, class_name)

    def _insert_user(self, first_name, last_name, email, password, role, class_name=""):
        first_name = required(first_name, "First name")
        last_name = required(last_name, "Last name")
        email = email_address(email)
        if role not in ROLES:
            raise ValueError("Choose a valid account role.")
        class_name = required(class_name, "Class", 20).upper() if role == "STUDENT" else None
        if self.db.execute("SELECT id FROM users WHERE email = ?", (email,)):
            raise ValueError("An account with this email already exists.")
        with self.db.transaction():
            return self.db.execute(
                "INSERT INTO users (first_name, last_name, email, password_hash, role, class_name) VALUES (?, ?, ?, ?, ?, ?)",
                (first_name, last_name, email, hash_password(password), role, class_name),
            )

    def bootstrap(self, first_name, last_name, email, password):
        if self.db.execute("SELECT id FROM users LIMIT 1"):
            raise ValueError("The database already has users. Sign in as a headteacher to manage accounts.")
        return self._insert_user(first_name, last_name, email, password, "HEADTEACHER")

    def users(self):
        self.require("HEADTEACHER")
        return self.db.execute(
            "SELECT id, first_name, last_name, email, role, class_name, active FROM users ORDER BY last_name, first_name, id"
        )

    def deactivate_user(self, user_id):
        actor = self.require("HEADTEACHER")
        if int(user_id) == actor["id"]:
            raise ValueError("You cannot deactivate your own account.")
        if not self.db.execute("SELECT id FROM users WHERE id = ? AND active = 1", (user_id,)):
            raise ValueError("Choose an active account.")
        with self.db.transaction():
            self.db.execute("UPDATE users SET active = 0 WHERE id = ?", (user_id,))

    def reset_password(self, user_id, password):
        self.require("HEADTEACHER")
        if not self.db.execute("SELECT id FROM users WHERE id = ? AND active = 1", (user_id,)):
            raise ValueError("Choose an active account.")
        hashed = hash_password(password)
        with self.db.transaction():
            self.db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed, user_id))

    def change_password(self, old_password, new_password):
        user = self.user
        stored = self.db.execute("SELECT password_hash FROM users WHERE id = ?", (user["id"],))[0]
        if not verify_password(stored["password_hash"], old_password):
            raise ValueError("Your current password is incorrect.")
        hashed = hash_password(new_password)
        with self.db.transaction():
            self.db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed, user["id"]))

    def lessons(self):
        user = self.user
        where, params = "", ()
        if user["role"] == "STUDENT":
            where, params = "WHERE l.class_name = ?", (user["class_name"],)
        elif user["role"] == "TEACHER":
            where, params = "WHERE l.teacher_id = ?", (user["id"],)
        return self.db.execute(
            "SELECT l.*, u.first_name, u.last_name FROM lessons l JOIN users u ON l.teacher_id = u.id "
            + where
            + " ORDER BY l.weekday, l.start_time, l.class_name",
            params,
        )

    def add_lesson(self, subject, class_name, teacher_id, weekday, start_time, end_time, room):
        self.require("HEADTEACHER")
        subject = required(subject, "Subject")
        class_name = required(class_name, "Class", 20).upper()
        room = required(room, "Room")
        try:
            weekday = int(weekday)
        except (ValueError, TypeError) as exc:
            raise ValueError("Choose a weekday.") from exc
        if weekday not in range(5):
            raise ValueError("Choose a weekday from Monday to Friday.")
        for value in (start_time, end_time):
            if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value):
                raise ValueError("Enter lesson times in HH:MM format.")
        if start_time >= end_time:
            raise ValueError("The lesson must end after it starts.")
        teacher = self.db.execute("SELECT role FROM users WHERE id = ? AND active = 1", (teacher_id,))
        if not teacher or teacher[0]["role"] not in ("TEACHER", "HEADTEACHER"):
            raise ValueError("Choose an active teacher.")
        overlaps = self.db.execute(
            "SELECT id FROM lessons WHERE weekday = ? AND start_time < ? AND end_time > ? "
            "AND (teacher_id = ? OR class_name = ? OR room = ?)",
            (weekday, end_time, start_time, teacher_id, class_name, room),
        )
        if overlaps:
            raise ValueError("This time conflicts with the teacher, class, or room schedule.")
        with self.db.transaction():
            return self.db.execute(
                "INSERT INTO lessons (subject, class_name, teacher_id, weekday, start_time, end_time, room) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (subject, class_name, teacher_id, weekday, start_time, end_time, room),
            )

    def delete_lesson(self, lesson_id):
        self.require("HEADTEACHER")
        if self.db.execute("SELECT id FROM attendance WHERE lesson_id = ? LIMIT 1", (lesson_id,)):
            raise ValueError("This lesson has attendance records and must be retained.")
        with self.db.transaction():
            self.db.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))

    def students(self):
        user = self.require("TEACHER", "HEADTEACHER")
        if user["role"] == "HEADTEACHER":
            return self.db.execute(
                "SELECT id, first_name, last_name, class_name FROM users WHERE role = 'STUDENT' AND active = 1 ORDER BY class_name, last_name, id"
            )
        return self.db.execute(
            "SELECT DISTINCT u.id, u.first_name, u.last_name, u.class_name FROM users u "
            "JOIN lessons l ON u.class_name = l.class_name WHERE u.role = 'STUDENT' AND u.active = 1 AND l.teacher_id = ? ORDER BY u.class_name, u.last_name, u.id",
            (user["id"],),
        )

    def _student_access(self, student_id, subject):
        actor = self.require("TEACHER", "HEADTEACHER")
        student = self.db.execute(
            "SELECT class_name FROM users WHERE id = ? AND role = 'STUDENT' AND active = 1", (student_id,)
        )
        if not student:
            raise ValueError("Choose an active student.")
        if actor["role"] != "HEADTEACHER" and not self.db.execute(
            "SELECT id FROM lessons WHERE class_name = ? AND subject = ? AND teacher_id = ?",
            (student[0]["class_name"], subject, actor["id"]),
        ):
            raise PermissionError("You can only manage students and subjects assigned to you.")
        return student[0]

    def grades(self):
        user = self.user
        where, params = "", ()
        if user["role"] == "STUDENT":
            where, params = "WHERE g.student_id = ?", (user["id"],)
        elif user["role"] == "TEACHER":
            where, params = "WHERE g.teacher_id = ?", (user["id"],)
        return self.db.execute(
            "SELECT g.*, u.first_name, u.last_name, u.class_name FROM grades g JOIN users u ON g.student_id = u.id "
            + where
            + " ORDER BY g.date DESC, g.id DESC",
            params,
        )

    def add_grade(self, student_id, subject, grade, weight, on_date):
        subject = required(subject, "Subject")
        self._student_access(student_id, subject)
        try:
            grade, weight = float(grade), int(weight)
        except (ValueError, TypeError, OverflowError) as exc:
            raise ValueError("Enter a numeric grade and an integer weight.") from exc
        if not 1 <= grade <= 6 or not 1 <= weight <= 10:
            raise ValueError("Grades must be between 1 and 6; weights between 1 and 10.")
        on_date = record_date(on_date)
        with self.db.transaction():
            return self.db.execute(
                "INSERT INTO grades (student_id, teacher_id, subject, grade, weight, date) VALUES (?, ?, ?, ?, ?, ?)",
                (student_id, self.user["id"], subject, grade, weight, on_date),
            )

    def delete_grade(self, grade_id):
        actor = self.require("TEACHER", "HEADTEACHER")
        rows = self.db.execute("SELECT * FROM grades WHERE id = ?", (grade_id,))
        if not rows:
            raise ValueError("Choose an existing grade.")
        if actor["role"] != "HEADTEACHER":
            if rows[0]["teacher_id"] != actor["id"]:
                raise PermissionError("You can only remove grades that you recorded.")
            self._student_access(rows[0]["student_id"], rows[0]["subject"])
        with self.db.transaction():
            self.db.execute("DELETE FROM grades WHERE id = ?", (grade_id,))

    def attendance(self):
        user = self.user
        where, params = "", ()
        if user["role"] == "STUDENT":
            where, params = "WHERE a.student_id = ?", (user["id"],)
        elif user["role"] == "TEACHER":
            where, params = "WHERE l.teacher_id = ?", (user["id"],)
        return self.db.execute(
            "SELECT a.*, l.subject, l.start_time, l.teacher_id, u.first_name, u.last_name, u.class_name "
            "FROM attendance a JOIN lessons l ON a.lesson_id = l.id JOIN users u ON a.student_id = u.id "
            + where
            + " ORDER BY a.date DESC, l.start_time, a.id DESC",
            params,
        )

    def mark_attendance(self, student_id, lesson_id, on_date, status):
        self.require("TEACHER", "HEADTEACHER")
        lesson = self.db.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,))
        if not lesson:
            raise ValueError("Choose an existing lesson.")
        lesson = lesson[0]
        student = self._student_access(student_id, lesson["subject"])
        if student["class_name"] != lesson["class_name"]:
            raise ValueError("The student does not belong to this lesson's class.")
        if self.user["role"] != "HEADTEACHER" and lesson["teacher_id"] != self.user["id"]:
            raise PermissionError("You can only record attendance for your own lessons.")
        on_date = record_date(on_date)
        if date.fromisoformat(on_date).weekday() != lesson["weekday"]:
            raise ValueError("The attendance date must match the lesson's weekday.")
        if status not in STATUSES:
            raise ValueError("Choose Present, Late, or Absent.")
        with self.db.transaction():
            existing = self.db.execute(
                "SELECT id FROM attendance WHERE student_id = ? AND lesson_id = ? AND date = ?",
                (student_id, lesson_id, on_date),
            )
            if existing:
                self.db.execute("UPDATE attendance SET status = ? WHERE id = ?", (status, existing[0]["id"]))
            else:
                self.db.execute(
                    "INSERT INTO attendance (student_id, lesson_id, date, status) VALUES (?, ?, ?, ?)",
                    (student_id, lesson_id, on_date, status),
                )

    def delete_attendance(self, attendance_id):
        actor = self.require("TEACHER", "HEADTEACHER")
        rows = self.db.execute(
            "SELECT l.teacher_id FROM attendance a JOIN lessons l ON a.lesson_id = l.id WHERE a.id = ?",
            (attendance_id,),
        )
        if not rows:
            raise ValueError("Choose an attendance record.")
        if actor["role"] != "HEADTEACHER" and rows[0]["teacher_id"] != actor["id"]:
            raise PermissionError("You can only remove attendance for your own lessons.")
        with self.db.transaction():
            self.db.execute("DELETE FROM attendance WHERE id = ?", (attendance_id,))

    def messages(self, sent=False):
        user = self.user
        column = "sender_id" if sent else "receiver_id"
        return self.db.execute(
            "SELECT m.*, s.email AS sender, r.email AS receiver FROM messages m "
            "JOIN users s ON m.sender_id = s.id JOIN users r ON m.receiver_id = r.id "
            f"WHERE m.{column} = ? ORDER BY m.sent_at DESC, m.id DESC",
            (user["id"],),
        )

    def send_message(self, receiver_email, subject, body):
        actor = self.user
        receiver_email = email_address(receiver_email)
        subject, body = required(subject, "Subject", 120), required(body, "Message", 10000)
        receiver = self.db.execute("SELECT id FROM users WHERE email = ? AND active = 1", (receiver_email,))
        if not receiver:
            raise ValueError("No active account uses this email address.")
        with self.db.transaction():
            self.db.execute(
                "INSERT INTO messages (sender_id, receiver_id, subject, body, sent_at) VALUES (?, ?, ?, ?, ?)",
                (actor["id"], receiver[0]["id"], subject, body, datetime.now().isoformat(sep=" ", timespec="seconds")),
            )


def weighted_average(grades):
    total_weight = sum(row["weight"] for row in grades)
    if not total_weight:
        return None
    return sum(row["grade"] * row["weight"] for row in grades) / total_weight
