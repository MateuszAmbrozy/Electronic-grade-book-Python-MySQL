from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from User import User

class Student(User):
    def __init__(self, root, cursor, conn, id, first_name, last_name, password, type, email, class_):
            #load info about student
            # self._current_user = {
            #     "id": id,
            #     "first_name": first_name,
            #     "last_name": last_name,
            #     "password" : password,
            #     "type": type,
            #     "email": email,
            #     "class_": class_
            # }
            super().__init__(root, cursor, conn, id, first_name, last_name, password, type, email, class_) #WYWOŁANIE KONSTRUKTORA USER

            self.frames["Attendance"] = ttk.Frame(self.notebook, width=600, height=600)
            self.frames["Attendance"].pack(fill='both', expand=True)
            self.notebook.add(self.frames["Attendance"], text = "Attendance")
            self.frames["Attendance"]

            self.showOneStudentAttendance()
            self.showGrades()
 
    def showScheduleOfDay(self, frame, day):
        frame.update_idletasks()
        label = Label(frame, text=day, fg='#97ffff', bg='black', font=('tagoma', 8, 'bold'))
        label.pack(pady=5)  # Używaj pack zamiast place

       
        query = ("SELECT start_time, end_time, subject, classroom, building, teacher "
                "FROM Lessons "
                "WHERE day_of_week = %s AND class_ = %s "
                "ORDER BY start_time")

        self.cursor.execute(query, (day, self._current_user["class_"]))
        lessons = self.cursor.fetchall()

        if len(lessons) != 0:
            for index, (start_time, end_time, name, classroom, building, teacher) in enumerate(lessons):
                lb = Label(frame, text=f"{start_time} - {end_time} {name} {building},{classroom} {teacher}", font=('tagoma', 8, 'bold'))
                lb.pack(pady=2)  # Używaj pack zamiast place
        else:
            label1 = Label(frame, text="FREE", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold'))
            label1.pack(pady=3)
        #ACCESSORS

    def showAccountInformation(self, frame):
        super().showAccountInformation(frame)

        Label(frame, text=f"CLASS: {self.getClass()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=3, column=1, padx=5, pady=5)
        Label(frame, text=f"SCHOOL REGISTER NUMBER: {self.getRegisterNumber()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=4, column=1, padx=5, pady=5)
        
    def showOneStudentAttendance(self): 

        attendanceFrame = Frame(self.frames["Attendance"], width=400, height=400)
        attendanceFrame.place(x=self.frames["Attendance"].winfo_reqwidth()/2 - attendanceFrame.winfo_reqwidth()/2, y=100)


        l1 = Label(self.frames["Attendance"], text="SELECT SUBJECT")
        l1.place(x=self.frames["Attendance"].winfo_reqwidth()/2 - l1.winfo_reqwidth()/2 - 15, y = 30)
        selected_variable = StringVar()
        cmbox = ttk.Combobox(self.frames["Attendance"], width=17, textvariable=selected_variable)
        cmbox.place(x=self.frames["Attendance"].winfo_reqwidth()/2 + l1.winfo_reqwidth()/2, y = 30)


        # Funkcja do aktualizacji wartości zmiennej StringVar
        def on_combobox_select(event):
            selected_variable = cmbox.get()
            self.show_attendance_in_table(attendanceFrame, selected_variable, self.getFirstName(), self.getLastName())
            
        cmbox.bind("<<ComboboxSelected>>", on_combobox_select)

        try:
            self.cursor.execute("SELECT subject FROM Lessons WHERE class_ = %s",
                                 (self.getClass(),))  # używamy * przed conditionals
            names = self.cursor.fetchall()
            for name in names:
                value_to_add = ' '.join(str(item) for item in name) if len(name) > 1 else str(name[0])
                if value_to_add not in cmbox['values']:
                    cmbox['values'] = (*cmbox['values'], value_to_add)
        except mysql.connector.Error as err:
            messagebox.showinfo("ERROR", "ERROR COMBOBOX QUERY")
        else:
            cmbox.current()
        
    def getRegisterNumber(self):
        try:
            self.conn.start_transaction()
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

            # Pobieramy wynik zapytania
            register_number = self.cursor.fetchone()[0]

            # Zatwierdzamy transakcję tylko jeśli nie było błędów
            self.conn.commit()

            return register_number

        except Exception as e:
            self.conn.rollback()  # Wycofujemy transakcję w przypadku błędu
            messagebox.showinfo("Error", f"An error occurred: {str(e)}")
            return None

    def showGrades(self):
        n = StringVar()
        subject_label = Label(self.frames["Grades"], text = "SELECT SUBJECT")
        subject_label.place(x=self.frames["Grades"].winfo_reqwidth()/2 - subject_label.winfo_reqwidth(), y=10)
        subjects = ttk.Combobox(self.frames["Grades"], width = 10, textvariable = n) 
        subjects.place(x = self.frames["Grades"].winfo_reqwidth()/2 + 15, y=10)
        subjects.current()

        container = Frame(self.frames["Grades"], width=self.frames["Grades"].winfo_reqwidth()/2*2, height=300)
        container.place(x= 15, y = 50)

        def on_subject_selected(event):
            selected_subject = subjects.get()


            self.cursor.execute("SELECT grade, grades_weight, date FROM Grades WHERE student_id=%s AND subject = %s", (self.getId(), selected_subject))
            grades = self.cursor.fetchall()

            for widget in container.winfo_children():
                    widget.destroy()
            columns = ('ID', "Grade", "Grades's weight", "Date")
            tree = ttk.Treeview(container, columns=columns, show='headings')
            tree.grid(row=0, column=0, sticky='nsew')


            #----------TREEEEEEEEEE---------------
            tree.column('#1', width=20) #ID
            tree.column('#2', width=100) #Grade
            tree.column('#3', width=100) #grade's weight
            tree.column('#4', width=100) #date
            
            scrollbar = ttk.Scrollbar(container, orient=VERTICAL, command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            scrollbar.grid(row=0, column=1, sticky='ns')
            for col in columns:
                tree.heading(col, text=col, command=lambda _col=col: self.sortby(tree, _col, 0))
                tree.column(col, anchor='center')

            for (grade, grades_weight, date) in grades:
                tree.insert(parent='', index='end', values=(self.getId(), grade, grades_weight, date))


        subjects.bind("<<ComboboxSelected>>", on_subject_selected)
        self.cursor.execute("SELECT name FROM Subjects")
        names = self.cursor.fetchall()

        for name in names:
            if name[0] not in subjects['values']:
                subjects['values'] = (*subjects['values'], name[0])

    def getClass(self):
        return self._current_user["class_"]