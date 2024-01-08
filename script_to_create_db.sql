create table Subjects (id int auto_increment primary key, name varchar(50) UNIQUE);
create table Classes (id int auto_increment primary key, name varchar(50) UNIQUE);
create table LessonTimes(id int auto_increment primary key, start_time time UNIQUE, end_time time UNIQUE);
create table Classrooms(id int auto_increment primary key, building VARCHAR(255), room_number varchar(20),INDEX idx_classroom_building (room_number, building), UNIQUE (building, room_number));
create table Weekdays(id int auto_increment primary key, day_name ENUM('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY') unique);

CREATE TABLE Users(
	id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    password VARCHAR(500),
    type ENUM('STUDENT', 'TEACHER', 'HEADTEACHER'),
    email VARCHAR(255) UNIQUE,
    class_ VARCHAR(20),
	FOREIGN KEY (class_) REFERENCES Classes(name) 
);

CREATE TABLE Messages(
	id INT AUTO_INCREMENT PRIMARY KEY,
    senderEmail VARCHAR(255),
    receiverEmail VARCHAR(255),
    topic VARCHAR(255),
    messageText text,
    sendDate datetime,
    FOREIGN KEY (senderEmail) REFERENCES Users(email),
    FOREIGN KEY (receiverEmail) REFERENCES Users(email)
);

CREATE TABLE Attendance(
	id INT AUTO_INCREMENT PRIMARY KEY,
	student_id int,
    date date, 
    start_time time,
    end_time time,
    status ENUM('PRESENT', 'LATE', 'ABSENT'),
    subject varchar(50),
    class_ varchar(20),
    FOREIGN KEY (student_id) REFERENCES Users(id),
    FOREIGN KEY (start_time) REFERENCES LessonTimes(start_time),
    FOREIGN KEY (end_time) REFERENCES LessonTimes(end_time),
    FOREIGN KEY (subject) REFERENCES Subjects(name),
	FOREIGN KEY (class_) REFERENCES Classes(name)
);

CREATE TABLE Lessons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject VARCHAR(50),
    classroom VARCHAR(20),
    building VARCHAR(255),
    class_ VARCHAR(20),
    day_of_week ENUM('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'),
    start_time TIME,
    end_time TIME,
    teacher VARCHAR(255),
    FOREIGN KEY (subject) REFERENCES Subjects(name),
	FOREIGN KEY (classroom, building) REFERENCES Classrooms(room_number, building),
    FOREIGN KEY (class_) REFERENCES Classes(name),
    FOREIGN KEY (day_of_week) REFERENCES Weekdays(day_name),
    FOREIGN KEY (start_time) REFERENCES LessonTimes(start_time),
    FOREIGN KEY (end_time) REFERENCES LessonTimes(end_time)
);

CREATE TABLE Grades
(
	id INT AUTO_INCREMENT PRIMARY KEY,
    student_id int,
    grade float,
    grades_weight int,
    teacher VARCHAR(255),
    subject VARCHAR(50),
    date DATETIME,
    FOREIGN KEY (student_id) REFERENCES Users(id),
    FOREIGN KEY (subject) REFERENCES Subjects(name)
);
CREATE TABLE SchoolAttention(
	id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id int,
    student_id int,
    attentioneText text,
    sendDate datetime,
    FOREIGN KEY (teacher_id) REFERENCES Users(id),
    FOREIGN KEY (student_id) REFERENCES Users(id)
);


INSERT INTO Subjects (name) VALUES
('Mathematics'),
('Physics'),
('Chemistry'),
('Biology'),
('English Literature'),
('History'),
('Geography'),
('Computer Science'),
('Economics'),
('Psychology'),
('Sociology'),
('Art'),
('Music'),
('Physical Education'),
('Foreign Language'),
('Philosophy'),
('Political Science'),
('Environmental Science'),
('Statistics'),
('Theater Arts');

INSERT INTO Classes (name) VALUES
('1A'),
('1B'),
('1C'),
('2A'),
('2B'),
('2C'),
('3A'),
('3B'),
('3C'),
('4A'),
('4B'),
('4C'),
('5A'),
('5B'),
('5C'),
('6A'),
('6B'),
('6C');

INSERT INTO LessonTimes (start_time, end_time) VALUES
('07:00', '07:45'),
('07:55', '08:40'),
('08:50', '09:35'),
('09:55', '10:40'),
('10:50', '11:35'),
('11:45', '12:30'),
('12:50', '13:35'),
('13:45', '14:30'),
('14:40', '15:25'),
('15:35', '16:20');

-- Przykładowe dane dla 100 sal lekcyjnych
INSERT INTO Classrooms (building, room_number) VALUES
('Main Building', 'Room 101'),
('Main Building', 'Room 102'),
('Main Building', 'Room 103'),
('Main Building', 'Room 104'),
('Main Building', 'Room 105'),
('Science Building', 'Lab 201'),
('Science Building', 'Lab 202'),
('Science Building', 'Lab 203'),
('Arts Building', 'Studio 301'),
('Arts Building', 'Studio 302'),
('Arts Building', 'Studio 303'),
('Math Building', 'Room 401'),
('Math Building', 'Room 402'),
('Math Building', 'Room 403'),
('Math Building', 'Room 404'),
('Language Building', 'Classroom 501'),
('Language Building', 'Classroom 502'),
('Language Building', 'Classroom 503'),
('Language Building', 'Classroom 504'),
('Main Building', 'Room 106'),
('Main Building', 'Room 107'),
('Main Building', 'Room 108'),
('Main Building', 'Room 109'),
('Main Building', 'Room 110'),
('Science Building', 'Lab 204'),
('Science Building', 'Lab 205'),
('Science Building', 'Lab 206'),
('Arts Building', 'Studio 304'),
('Arts Building', 'Studio 305'),
('Arts Building', 'Studio 306'),
('Math Building', 'Room 405'),
('Math Building', 'Room 406'),
('Math Building', 'Room 407'),
('Language Building', 'Classroom 505'),
('Language Building', 'Classroom 506'),
('Language Building', 'Classroom 507'),
-- Dodaj więcej wierszy w podobny sposób
('Extra Building', 'Room 901'),
('Extra Building', 'Room 902'),
('Extra Building', 'Room 903'),
('Extra Building', 'Room 904');

INSERT INTO Weekdays (day_name) VALUES
('MONDAY'),
('TUESDAY'),
('WEDNESDAY'),
('THURSDAY'),
('FRIDAY'),
('SATURDAY'),
('SUNDAY');
