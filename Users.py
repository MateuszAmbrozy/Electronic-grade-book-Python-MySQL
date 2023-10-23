from abc import ABC, abstractmethod
import mysql.connector
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import sys
import datetime
class User(ABC):
   
   #CONSTRUCTOR
    def __init__(self, cursor, frames, notebook, conn):
        self._current_user = None
        self.cursor = cursor
        self.conn = conn
        self.frames = frames
        self.notebook = notebook


    #PUBLIC FUNCTIONS
    @abstractmethod #point that this function is abstract
    def showScheduleOfDay(self, frame, day):
        pass

    
    def showScheduleOfWeek(self, master_frame):
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        frame_height = 600/5
        frame_width = 600
        print("Height and width", frame_height, frame_width)

        for index, day in enumerate(days_of_week):
            day_frame = Frame(master_frame, bd=1, relief="solid")
            day_frame.place(x=0, y=index * frame_height, width=frame_width, height=frame_height)

            canva = Canvas(day_frame, height=frame_height - 20, width=frame_width - 20)  # Restrykcyjnie określamy wysokość i szerokość Canvas
            canva.pack(side=LEFT, fill=BOTH, expand=True)

            scrollbar = Scrollbar(day_frame, orient=VERTICAL, command=canva.yview)
            scrollbar.pack(side=RIGHT, fill=Y)

            canva.configure(yscrollcommand=scrollbar.set)

            second_frame = Frame(canva)
            canva.create_window((0, 0), window=second_frame, anchor="nw", width=frame_width - 20)  # Dodajemy width do create_window

            for i in range(50):  # To jest testowe dodawanie etykiet
                Label(second_frame, text=f"Test {i}").pack()

            self.showScheduleOfDay(second_frame, day)

            second_frame.update_idletasks()
            canva.config(scrollregion=canva.bbox("all"))



        
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
    #CONSTRUCTOR
    def __init__(self, cursor, frames, notebook, conn, id, first_name, last_name, type, email, class_):
            #load info about student
            super().__init__(cursor, frames, notebook, conn) #WYWOŁANIE KONSTRUKTORA USER
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
        frame.update_idletasks()
        label = Label(frame, text=day, fg='#97ffff', bg='black', font=('tagoma', 8, 'bold'))
        label.pack(pady=5)  # Używaj pack zamiast place

       
        query = ("SELECT start_time, end_time, name, classroom, teacher "
                "FROM Lessons "
                "WHERE day_of_week = %s AND class_ = %s "
                "ORDER BY start_time")

        self.cursor.execute(query, (day, self._current_user["class_"]))
        lessons = self.cursor.fetchall()

        if len(lessons) != 0:
            for index, (start_time, end_time, name, classroom, teacher) in enumerate(lessons):
                lb = Label(frame, text=f"{start_time} - {end_time} {name} {classroom} {teacher}", font=('tagoma', 8, 'bold'))
                lb.pack(pady=2)  # Używaj pack zamiast place
        else:
            label1 = Label(frame, text="FREE", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold'))
            label1.place(x = frame.winfo_width()/2 - label1.winfo_width()/2, y=frame.winfo_height()/2 - label1.winfo_height()/2)
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
    def __init__(self, cursor, frames, notebook, conn, id, first_name, last_name, type, email):
            
            #load info about student
            super().__init__(cursor, frames, notebook, conn) #WYWOŁANIE KONSTRUKTORA USER
            self._current_user = {
                "id": id,
                "first_name": first_name,
                "last_name": last_name,
                "type": type,
                "email": email
            }
            self.frames["Attendance"] = ttk.Frame(notebook, width=600, height=600)
            self.frames["Attendance"].pack(fill='both', expand=True)
            notebook.add(frames["Attendance"], text = "Attendance")
            self.takeAttendance()

    def showScheduleOfDay(self, frame, day):        
        teacher_name = str(self._current_user["first_name"] + " " + self._current_user["last_name"])
        label = Label(frame, text=day, fg='#97ffff', bg='black', font=('tagoma', 8, 'bold'))
        label.pack(pady=5)  # Używaj pack zamiast place

        query = ("SELECT start_time, end_time, name, classroom, class_ "
                "FROM Lessons "
                "WHERE day_of_week = %s AND teacher = %s "
                "ORDER BY start_time")

        self.cursor.execute(query, (day, teacher_name))
        lessons = self.cursor.fetchall()

        if len(lessons) != 0:
            for index, (start_time, end_time, name, classroom, class_) in enumerate(lessons):
                lb = Label(frame, text=f"{start_time} - {end_time} {name} {classroom} {class_}", font=('tagoma', 8, 'bold'))
                lb.pack(pady=2)  # Używaj pack zamiast place

        else:
            label1 = Label(frame, text="FREE", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold'))
            label1.place(x = frame.winfo_width()/2 - label1.winfo_width()/2, y=frame.winfo_height()/2 - label1.winfo_height()/2)

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
    def takeAttendance(self):
        n = StringVar() 
        classes = ttk.Combobox(self.frames["Attendance"], width = 27, textvariable = n) 

        #FUNCTION ANSWERS FOR 1ST COMBOBOX --CLASSES
        def on_class_selected(event):
            # style = ttk.Style()
            # style.configure('TLabel', padding=5)
            # style.configure('TRadiobutton', padding=5)
            selected_class = classes.get()
            teacher = str(self.getFirstName() + " " + self.getLastName())
            m=StringVar()
            subjects = ttk.Combobox(self.frames["Attendance"], width = 27, textvariable = m)
            subjects.place(x=200, y=0) 
            #FUNCTION ANSWERS FOR 2ST COMBOBOX SUBJECTS
            def showStudents(event):
                selected_subject = subjects.get()
                attendance_vars = []
                self.cursor.execute("SELECT id, first_name, last_name FROM Users WHERE class_ = %s", (selected_class,))
                students = self.cursor.fetchall()

                ttk.Label(self.frames["Attendance"], text="Name").place(x=0, y=100)
                ttk.Label(self.frames["Attendance"], text="Last Name").place(x=100, y=100)
                ttk.Label(self.frames["Attendance"], text="Attendance").place(x=200, y=100)

                for index, (student_id, first_name, last_name) in enumerate(students, start = 1):
                    l1= ttk.Label(self.frames["Attendance"], text=first_name)
                    l1.place(x= 0, y = index * l1.winfo_reqheight() + 120)
                    l2= ttk.Label(self.frames["Attendance"], text=last_name)
                    l2.place(x = 100, y = index * l2.winfo_reqheight() + 120)

                    # Attendance radio buttons
                    attendance = StringVar()
                    rb3=ttk.Radiobutton(self.frames["Attendance"], text="Present", variable=attendance, value="PRESENT")
                    rb3.place(x = 200, y = index * rb3.winfo_reqheight() + 120)
                    rb4=ttk.Radiobutton(self.frames["Attendance"], text="Late", variable=attendance, value="LATE")
                    rb4.place(x = 250, y = index * rb4.winfo_reqheight() + 120)
                    rb5=ttk.Radiobutton(self.frames["Attendance"], text="Absent", variable=attendance, value="ABSENT")
                    rb5.place(x = 300, y = index * rb5.winfo_reqheight() + 120)
                    attendance_vars.append(attendance)

                def saveAttendance():
                    
                    empty_entries = [var for var in attendance_vars if not var.get()]
                    if (not empty_entries):
                        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
                        for index, (student_id, _, _) in enumerate(students):
                            self.cursor.execute("INSERT INTO Attendance (student_id, date, status, subject_name, class_) VALUES(%s, %s, %s, %s, %s)",
                            (student_id, current_date, attendance_vars[index].get(), selected_subject, selected_class))
                        self.conn.commit()
                        def clear_and_redraw():
                            # Usuwanie wszystkich widgetów w ramce
                            for widget in self.frames["Attendance"].winfo_children():
                                widget.destroy()
                            
                                self.takeAttendance()

                        messagebox.showinfo("Success", "Attendance results saved successfully!")

                        # Czyszczenie i przerysowanie zawartości ramki
                        clear_and_redraw()
                    else:
                        messagebox.showinfo("Error", "Some Attendances are empty!")

                b1 = Button(self.frames["Attendance"], text = "SAVE",
                            command=saveAttendance, cursor="hand2")
                b1.place(x=400, y=400)
                
            subjects.bind("<<ComboboxSelected>>", showStudents)

            self.cursor.execute("SELECT name FROM Lessons WHERE class_ = %s and teacher = %s",
            (selected_class, teacher))
            subject_names = self.cursor.fetchall()
            subject_values = list(set([s_name[0] for s_name in subject_names]))
            subjects.configure(values=subject_values)

        classes.bind("<<ComboboxSelected>>", on_class_selected)
        
        self.cursor.execute("SELECT name FROM Classes")
        names = self.cursor.fetchall()

        for name in names:
            if name[0] not in classes['values']:
                classes['values'] = (*classes['values'], name[0])
        

        classes.grid(column = 1, row = 5) 
        classes.current()

                
#----------------------------------TEACHER CLASS----------------------------------
class HeadTeacher(Teacher):
    def __init__(self, cursor, frames, notebook, conn, id, first_name, last_name, type, email):
        super().__init__(cursor, frames, notebook, conn, id, first_name, last_name, type, email) #WYWOŁANIE KONSTRUKTORA TEACHER
        self.frames["Menage users"] = ttk.Frame(notebook, width=600, height=600)
        self.frames["Menage users"].pack(fill='both', expand=True)
        notebook.add(frames["Menage users"], text = "Menage users")
        self.menageUsers(frames["Menage users"])

    def menageUsers(self, frame):
        addingUserFrame = Frame(frame, bd=1, relief="solid")
        addingUserFrame.place(x=0, y=30, width=frame.winfo_reqwidth()/2, height=frame.winfo_reqheight())
        
        adding_label = Label(addingUserFrame, text="Adding Users", font=('tagoma', 12, 'bold'))
        adding_label.pack(pady=20)  # Ustawiamy napis "Adding Users" na górze ramki
        
        removingUserFrame = Frame(frame, bd=1, relief="solid")
        removingUserFrame.place(x=frame.winfo_reqwidth()/2, y=30, width=frame.winfo_reqwidth()/2, height=frame.winfo_reqheight())

        removing_label = Label(removingUserFrame, text="Delete User", font=('tagoma', 12, 'bold'))
        removing_label.pack(pady=20)  # Ustawiamy napis "Delete User" na górze ramki

        def showAllUsers():
            top = Toplevel(frame)
            self.cursor.execute("SELECT id, first_name, last_name, type, email, class_ FROM Users")
            users = self.cursor.fetchall()

            container = Frame(top)
            container.pack(fill='both', expand=True)

            columns = ('ID', 'First Name', 'Last Name', 'Type', 'Email', 'Class')
            tree = ttk.Treeview(container, columns=columns, show='headings')

            # Defining column headings
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100, anchor='center')

            # Adding data to treeview
            for i in range(50):
                for (id, first_name, last_name, type, email, class_) in users:
                    tree.insert('', 'end', values=(id, first_name, last_name, type, email, class_))

            # Binding function to treeview row select
            def on_item_select(event):
                for selected_item in tree.selection():
                    item = tree.item(selected_item)
                    record = item['values']
                    #showinfo(title='Information', message=', '.join(map(str, record)))

            tree.bind('<<TreeviewSelect>>', on_item_select)

            tree.grid(row=0, column=0, sticky='nsew')

            # Adding scrollbar
            scrollbar = ttk.Scrollbar(container, orient=VERTICAL, command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            scrollbar.grid(row=0, column=1, sticky='ns')

        show_users_btn = Button(frame, text="Show all Users", command=showAllUsers, cursor="hand2")
        show_users_btn.place(x=10, y=10)

        self.removeUser(removingUserFrame)

    def removeUser(self, frame):

        id_label = Label(frame, text='ID')
        id_entry = Entry(frame, width=30)
        id_label.pack(pady=3)
        id_entry.pack(pady=3)

        name_label = Label(frame, text='Name')
        name_entry = Entry(frame, width=30)
        name_label.pack(pady=3)
        name_entry.pack(pady=3)

        last_name_label = Label(frame, text='Last Name')
        last_name_entry = Entry(frame, width=30)
        last_name_label.pack(pady=3)
        last_name_entry.pack(pady=3)

        def delete():
            try:
                    self.cursor.execute("DELETE FROM Users WHERE id = %s AND first_name = %s AND last_name = %s",
                                (id_entry.get(), name_entry.get(), last_name_entry.get()))
                    self.conn.commit()
                    messagebox.showinfo("Success", "Delete successfull!")
            except mysql.connector.Error as err:
                    messagebox.showinfo("Failure", "Delete failure!")

        show_users_btn = Button(frame, text="Delete user", command=delete, cursor="hand2")
        show_users_btn.pack(pady=3)
        





