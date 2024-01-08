# Electronic grade book

## Overview
This project is a Python application with a graphical user interface (GUI) developed using Tkinter and MySQL for managing an
electronic grade book. The system is designed to cater to three user roles: Student, Teacher, and Headteacher. The project follows
an inheritance structure with the base class "User" providing different options and access for each role.
## Features

### Login window
![image](https://github.com/MateuszAmbrozy/Electronic-grade-book-Python-MySQL/assets/127397482/69e7457f-4ee5-4b64-92a7-13f306ea3d64)


### Every user
* Display own schedule of week
* Sending and receiving messages
### Student
* Display own grades
* Display own attendance

### Teacher
* Inserting and removing grades for students in the classes being taught
* Inserting and removing attendance for students in the classes being taught

### HeadTeacher(administrator)
* Inserting and removing grades for students in the classes being taught
* Inserting and removing attendance for students in the classes being taught
* Manage users
  * register new users
  * removing users
  * changing passwords
  * displaying all users
* Manage lessons
  * displaying all lessons
  * adding lessons
  * removing lesson
  * removing all lessons

### Sreenshots
![image](https://github.com/MateuszAmbrozy/Electronic-grade-book-Python-MySQL/assets/127397482/427234e8-af9a-4ffa-bc76-70cf0f8bc06d)
![image](https://github.com/MateuszAmbrozy/Electronic-grade-book-Python-MySQL/assets/127397482/cbc7be79-2611-4a98-a820-679337bbcff6)


### Setup
* Fork this repo
* Clone repo
* Create database pasting sript_to_create_db.sql into MySQL commandline before running project
* Configure stuff in config.json
```
  {
    "pass": "DATABASE PASSWORD",
    "user": "root",
    "host": "localhost",
    "database": "employees",
    "port": Your port
  }
```
* Install requirements
```
  pip install -r requirements.txt
```
* Run main.py
```
  python main.py
```
