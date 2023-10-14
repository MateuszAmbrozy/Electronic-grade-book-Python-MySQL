SELECT * FROM python.users;

drop table python.login;
CREATE TABLE python.login (
username VARCHAR(255) UNIQUE NOT NULL,
hashedPassword VARCHAR(255) NOT NULL,
userType VARCHAR(50) NOT NULL
);
SELECT * FROM python.login;
INSERT INTO python.login (login, passwd, userType) values (1, 2, 3);
ALTER TABLE python.login change passwd passwd VARCHAR(60); 

-----------------------------------------------------------------------------
insert into Users (first_name, last_name, password, type, email) values(1, 1, 1, 1, 1);
SELECT * FROM python.Users;
-- Users table
CREATE TABLE Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL, -- Consider using hashed passwords
    type ENUM('STUDENT', 'TEACHER', 'PRINCIPAL') NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

-- Classes table
CREATE TABLE Classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL
);

-- Subjects table
CREATE TABLE Subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE Schedule (
	id INT AUTO_INCREMENT PRIMARY KEY,
    time TIME,
    day VARCHAR(25),
    
);

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
CREATE TABLE Attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    date DATE NOT NULL,
    status ENUM('PRESENT', 'ABSENT', 'LATE') NOT NULL,
    FOREIGN KEY (student_id) REFERENCES Users(id)
);
