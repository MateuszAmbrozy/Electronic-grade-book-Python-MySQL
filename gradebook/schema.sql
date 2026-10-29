CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('STUDENT', 'TEACHER', 'HEADTEACHER')),
    class_name VARCHAR(20),
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    CHECK ((role = 'STUDENT' AND class_name IS NOT NULL) OR (role != 'STUDENT' AND class_name IS NULL))
);
CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject VARCHAR(80) NOT NULL,
    class_name VARCHAR(20) NOT NULL,
    teacher_id INTEGER NOT NULL,
    weekday INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 4),
    start_time VARCHAR(5) NOT NULL,
    end_time VARCHAR(5) NOT NULL,
    room VARCHAR(80) NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES users(id),
    CHECK (start_time < end_time)
);
CREATE TABLE IF NOT EXISTS grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    subject VARCHAR(80) NOT NULL,
    grade REAL NOT NULL CHECK (grade BETWEEN 1 AND 6),
    weight INTEGER NOT NULL CHECK (weight BETWEEN 1 AND 10),
    date VARCHAR(10) NOT NULL,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (teacher_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    lesson_id INTEGER NOT NULL,
    date VARCHAR(10) NOT NULL,
    status VARCHAR(10) NOT NULL CHECK (status IN ('PRESENT', 'LATE', 'ABSENT')),
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id),
    UNIQUE (student_id, lesson_id, date)
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    subject VARCHAR(120) NOT NULL,
    body TEXT NOT NULL,
    sent_at VARCHAR(19) NOT NULL,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id)
);
