from abc import ABC, abstractmethod
import mysql.connector
from tkinter import *
from tkinter import ttk
import sys
import datetime
class User(ABC):
   
   #CONSTRUCTOR
    def __init__(self, cursor, conn):
        self._current_user = None
        self.cursor = cursor
        self.conn = conn


    #PUBLIC FUNCTIONS
    @abstractmethod #point that this function is abstract
    def showScheduleOfDay(self, frame, day):
        pass
    @abstractmethod
    def showAccountInformation(self, frame):
        Label(frame, text=f"NAME: {self.getFirstName()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=1, column=1)
        Label(frame, text=f"SURNAME: {self.getLastName()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=2, column=1)
        Label(frame, text=f"ID: {self.getId()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=1, column=5)
        Label(frame, text=f"USER TYPE: {self.getType()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=2, column=5)
        Label(frame, text=f"E-MAIL: {self.getEmail()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=3, column=5)

    #ACCESSORS
    def getId(self):
         return self._current_user["id"]
    def getFirstName(self):
         return self._current_user["first_name"]
    def getLastName(self):
         return self._current_user["last_name"]
    def getType(self):
         return self._current_user["type"]
    def getEmail(self):
         return self._current_user["email"]

#----------------------------------STUDENT CLASS----------------------------------
class Student(User):
    #VARIABLES

    #CONSTRUCTOR
    def __init__(self, cursor, conn, id, first_name, last_name, type, email, class_):
            #load info about student
            super().__init__(cursor, conn) #WYWOŁANIE KONSTRUKTORA USER
            self._current_user = {
                "id": id,
                "first_name": first_name,
                "last_name": last_name,
                "type": type,
                "email": email,
                "class_": class_
            }
    #PUBLIC FUNCTIONS
    def showScheduleOfDay(self, frame, day):
        label = Label(frame, text=day, fg='#97ffff', bg='black', font=('tagoma', 8, 'bold'))
        label.update()
        label.place(x= 150 -label.winfo_reqwidth()/2, y=5)

        query = ("SELECT start_time, end_time, name, classroom, teacher "
                "FROM Lessons "
                "WHERE day_of_week = %s AND class_ = %s "
                "ORDER BY start_time")

        self.cursor.execute(query, (day, self._current_user["class_"]))
        lessons = self.cursor.fetchall()

        if lessons:
            for index, (start_time, end_time, name, classroom, teacher) in enumerate(lessons, 2):
                lb = Label(frame, text=f"{start_time} - {end_time} - {name} - {classroom} - {teacher}",  font=('tagoma', 8, 'bold'))
                lb.place(x=0, y = index * lb.winfo_reqheight())
        else:
            label1 = Label(frame, text="FREE", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold'))
            label1.place(x=50, y = 20)
        #ACCESSORS

    def showAccountInformation(self, frame):
        super().showAccountInformation(frame)

        Label(frame, text=f"CLASS: {self.getClass()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=3, column=1)
        Label(frame, text=f"SCHOOL REGISTER NUMBER: {self.getRegisterNumber()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=6, column=6)

    def getRegisterNumber(self):
        self.cursor.execute("SET @rank := 0;")
        query = """
            SELECT student_rank 
            FROM (
                SELECT id, @rank := @rank + 1 AS student_rank 
                FROM Users 
                WHERE class_ = %s 
                ORDER BY last_name ASC
            ) AS subquery 
            WHERE id = %s;
        """

        self.cursor.execute(query, (self.getClass(), self.getId()))
        return self.cursor.fetchone()[0]
    def getClass(self):
        return self._current_user["class_"]

#----------------------------------TEACHER CLASS----------------------------------
class Teacher(User):
    def __init__(self, cursor, conn,  id, first_name, last_name, type, email):
            
            #load info about student
            super().__init__(cursor, conn) #WYWOŁANIE KONSTRUKTORA USER
            self._current_user = {
                "id": id,
                "first_name": first_name,
                "last_name": last_name,
                "type": type,
                "email": email
            }
    def showScheduleOfDay(self, frame, day):
        label = Label(frame, text=day, fg='#97ffff', bg='black', font=('tagoma', 8, 'bold'))
        label.update()
        label.place(x= 150 -label.winfo_reqwidth()/2, y=5)
        
        teacher_name = str(self._current_user["first_name"] + " " + self._current_user["last_name"])
        
        query = ("SELECT start_time, end_time, name, classroom, class_ "
                "FROM Lessons "
                "WHERE day_of_week = %s AND teacher = %s "
                "ORDER BY start_time")

        self.cursor.execute(query, (day, teacher_name))
        lessons = self.cursor.fetchall()

        if len(lessons) != 0:
            for index, (start_time, end_time, name, classroom, class_) in enumerate(lessons, 2):
               lb = Label(frame, text=f"{start_time} - {end_time} {name} {classroom} {class_}", font=('tagoma', 8, 'bold'))
               lb.place(x=0, y = index * lb.winfo_reqheight())

        else:
            label1 = Label(frame, text="FREE", fg='#97ffff', bg='black', font=('tagoma', 15, 'bold'))
            label1.place(x=frame.winfo_width()/2 - label1.winfo_width()/2, y=frame.winfo_height()/2 - label1.winfo_height()/2)
    def showAccountInformation(self, frame):
         super().showAccountInformation(frame)
    def insertGrade(self, frame):
        #Tu coś takiego napisałem ale to i tak trzeba zmienić 
        #bo 
        student_label = Label(frame, text='Student ID:')
        student_entry = Entry(frame, width=30)
        student_label.grid(row=0, column=0)
        student_entry.grid(row=0, column=1)

        # Choosing subject
        subject_label = Label(frame, text='Subject ID:')
        subject_entry = Entry(frame, width=30)
        subject_label.grid(row=1, column=0)
        subject_entry.grid(row=1, column=1)

        # Inputting grade
        grade_label = Label(frame, text='Grade (1-6):')
        grade_entry = Entry(frame, width=30)
        grade_label.grid(row=2, column=0)
        grade_entry.grid(row=2, column=1)

        def add_grade():
            student_id = student_entry.get()
            subject_id = subject_entry.get()
            grade = grade_entry.get()

            try:
                self.cursor.execute("INSERT INTO Grades (student_id, subject_id, grade) VALUES (%s, %s, %s)",
                            (student_id, subject_id, grade))
                self.conn.commit()
                info_str = "Grade added successfully!"
                color = "green"
            except mysql.connector.Error as err:
                info_str = f"Error: {err}"
                color = "red"
            
            info_label = Label(frame, text=info_str, fg=color)
            info_label.grid(row=5, column=0, columnspan=2)

        add_btn = Button(frame, text="Add Grade", command=add_grade, cursor="hand2")
        add_btn.grid(row=4, column=0, columnspan=2, pady=10, padx=10, ipadx=30)
#----------------------------------TEACHER CLASS----------------------------------
class HeadTeacher(User):
    def __init__(self, cursor, conn, id, first_name, last_name, type, email):
        #load info about student
        self.teacher = Teacher(cursor, id, first_name, last_name, type, email) #Create teacher variable to use some teacher's functions
        super().__init__(cursor, conn) #WYWOŁANIE KONSTRUKTORA USER
        self._current_user = {
            "id": id,
            "first_name": first_name,
            "last_name": last_name,
            "type": type,
            "email": email
        }
    def showScheduleOfDay(self, frame, day):
         self.teacher.showScheduleOfDay(frame, day)