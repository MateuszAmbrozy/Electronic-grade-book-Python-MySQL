#SELECT * FROM python.users;
#drop table python.login;

-- CREATE TABLE python.login (
-- username VARCHAR(255) UNIQUE NOT NULL,
-- hashedPassword VARCHAR(255) NOT NULL,
-- userType VARCHAR(50) NOT NULL
-- );
#SELECT * FROM python.login;
-- INSERT INTO python.login (login, passwd, userType) values (1, 2, 3);
-- ALTER TABLE python.login change passwd passwd VARCHAR(60); 

-----------------------------------------------------------------------------
-- SELECT * FROM python.Users;
-- Users table
-- DROP TABLE python.Users;
CREATE TABLE Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    type ENUM('STUDENT', 'TEACHER', 'PRINCIPAL') NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    class_ VARCHAR(50)
);


-- Classes table
CREATE TABLE Classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL
);
INSERT INTO Classes (name) 
VALUES 
('1a'), 
('1b'), 
('1c'), 
('2a'), 
('2b'), 
('2c'), 
('3a'), 
('3b'), 
('3c'), 
('4a'), 
('4b'), 
('4c'), 
('5a'), 
('5b'), 
('5c'), 
('6a'), 
('6b'), 
('6c');

SELECT * FROM classes;
-- Subjects table
CREATE TABLE Subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);
-- DROP TABLE Lessons;

-- ALTER TABLE Lessons 
-- MODIFY COLUMN day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL;

CREATE TABLE Lessons  (
	id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    classroom INT,
    class_ VARCHAR(50),
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday') NOT NULL,
	teacher VARCHAR(255),
	start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    FOREIGN KEY (class_) REFERENCES Classes(name),
    FOREIGN KEY (name) REFERENCES Subjects(name)
);

INSERT INTO Lessons (name, classroom, class_, day_of_week, teacher, start_time, end_time) VALUES
('Mathematics', 101, '1b', 'Thursday', '1 1', '09:00:00', '09:45:00');
INSERT INTO Lessons (name, classroom, class_, day_of_week, teacher, start_time, end_time) VALUES
('Mathematics', 101, '3a', 'Monday', 'T1', '08:00:00', '08:45:00'),
('English', 102, '3a', 'Monday', 'T2', '09:00:00', '09:45:00'),
('History', 103, '3b', 'Tuesday', 'T3', '08:00:00', '08:45:00'),
('Biology', 104, '3b', 'Tuesday', 'T4', '09:00:00', '09:45:00'),
('Physics', 101, '3c', 'Wednesday', 'T5', '08:00:00', '08:45:00'),
('Chemistry', 102, '3c', 'Wednesday', 'T6', '09:00:00', '09:45:00');
-- SELECT * FROM python.Lessons;
-- Grades table
CREATE TABLE Grades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    subject_id INT,
    grade ENUM('1', '2', '3', '4', '5', '6') NOT NULL,
    grade_evaluation INT,
    date DATE,
    FOREIGN KEY (student_id) REFERENCES Users(id),
    FOREIGN KEY (subject_id) REFERENCES Subjects(id)
);

-- Attendance table
drop table Attendance;
CREATE TABLE Attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    date DATE NOT NULL,
    status ENUM('PRESENT', 'ABSENT', 'LATE') NOT NULL,
    subject_name VARCHAR(100),
    class_ VARCHAR(20),
    FOREIGN KEY (student_id) REFERENCES Users(id)
);
-- select * from Attendance;

CREATE TABLE Notes(
	id INT auto_increment PRIMARY KEY,
    student_id INT,
    note Varchar(255),
    date DATE NOT NULL,
    FOREIGN KEY (student_id) REFERENCES Users(id)
);

