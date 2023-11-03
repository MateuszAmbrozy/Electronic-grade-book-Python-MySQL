from abc import ABC, abstractmethod
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
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

    @abstractmethod #point that this function is abstract
    def showOneStudentAttendance(self, frame):
        pass
    
    def showScheduleOfWeek(self, master_frame):
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        frame_height = (600 - 20)/5
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


            self.showScheduleOfDay(second_frame, day)

            second_frame.update_idletasks()
            canva.config(scrollregion=canva.bbox("all"))
  
    def showAccountInformation(self, frame):
        Label(frame, text=f"NAME: {self.getFirstName()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=1, column=1)
        Label(frame, text=f"SURNAME: {self.getLastName()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=2, column=1)
        Label(frame, text=f"ID: {self.getId()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=1, column=5)
        Label(frame, text=f"USER TYPE: {self.getType()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=2, column=5)
        Label(frame, text=f"E-MAIL: {self.getEmail()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=3, column=5)
        #To jest pomocnicza funkcja do 
    def combobox(self, frame, txt, column_, row_, qry, *conditionals):
        Label(frame, text=txt).grid(column=column_, row=row_, padx=10, pady=0)
        selected_variable = StringVar()
        cmbox = ttk.Combobox(frame, width=17, textvariable=selected_variable)

        # Funkcja do aktualizacji wartości zmiennej StringVar
        def on_combobox_select(event):
            selected_variable.set(cmbox.get())

        cmbox.bind("<<ComboboxSelected>>", on_combobox_select)

        try:
            if conditionals:  # Jeśli istnieją jakiekolwiek warunki
                self.cursor.execute(qry, conditionals)  # używamy * przed conditionals
            else:
                self.cursor.execute(qry)  # Jeśli nie ma warunków, po prostu wykonaj zapytanie
            names = self.cursor.fetchall()
            for name in names:
                value_to_add = ' '.join(str(item) for item in name) if len(name) > 1 else str(name[0])
                if value_to_add not in cmbox['values']:
                    cmbox['values'] = (*cmbox['values'], value_to_add)
        except mysql.connector.Error as err:
            messagebox.showinfo("ERROR", "ERROR COMBOBOX QUERY")

        cmbox.grid(column=column_ + 1, row=row_, pady=10)
        cmbox.current()
        return selected_variable
    def sortby(self, tree, col, descending):
        """sort tree contents when a column header is clicked on"""
        # Grab values to sort
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        
        # If the data to be sorted is numeric change to float
        try:
            data = [(float(val), key) for val, key in data]
        except ValueError:
            pass  # If not numeric, keep it as text

        # Reorder data
        data.sort(reverse=descending)
        for indx, item in enumerate(data):
            tree.move(item[1], '', indx)
        
        # Switch the heading so it will sort in the opposite direction
        tree.heading(col, command=lambda col=col: self.sortby(tree, col, int(not descending)))

    def show_attendance_in_table(self, frame, subject, first_name, last_name):
        print(str(subject), first_name, last_name)
        query = """
        SELECT A.date, A.status, A.class_
        FROM Attendance A
        JOIN Users U ON A.student_id = U.id
        WHERE A.subject_name = %s
        AND U.first_name = %s
        AND U.last_name = %s
        """

        try:
            self.cursor.execute(query, (str(subject), first_name, last_name))
            users = self.cursor.fetchall()

            columns = ("DATE", "STATUS", "CLASS")
            tree = ttk.Treeview(frame, columns=columns, show='headings')

            # Defining column headings
            for col in columns:
                tree.heading(col, text=col, command=lambda _col=col: self.sortby(tree, _col, 0))
                tree.column(col, width=100, anchor='center')

            # Adding data to treeview
            for (date, status, class_) in users:
                tree.insert('', 'end', values=(date, status, class_))

            # Binding function to treeview row select
            def on_item_select(event):
                for selected_item in tree.selection():
                    item = tree.item(selected_item)
                    record = item['values']

            tree.bind('<<TreeviewSelect>>', on_item_select)

            tree.grid(row=0, column=0, sticky='nsew')

            # Adding scrollbar
            scrollbar = ttk.Scrollbar(frame, orient=VERTICAL, command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            scrollbar.grid(row=0, column=1, sticky='ns')

        except mysql.connector.Error as err:
            messagebox.showinfo("ERROR", "Error in SQL Query: " + str(err))

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
            self.frames["Show Attendance"] = ttk.Frame(notebook, width=600, height=600)
            self.frames["Show Attendance"].pack(fill='both', expand=True)
            notebook.add(frames["Show Attendance"], text = "Show Attendance")

            self.showOneStudentAttendance(self.frames["Show Attendance"])
 
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
            label1.pack(pady=3)
        #ACCESSORS
    def showAccountInformation(self, frame):
        super().showAccountInformation(frame)

        Label(frame, text=f"CLASS: {self.getClass()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=3, column=1)
        Label(frame, text=f"SCHOOL REGISTER NUMBER: {self.getRegisterNumber()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=6, column=6)

    def showOneStudentAttendance(self, frame): 

        attendanceFrame = Frame(frame, width=400, height=400)
        attendanceFrame.place(x=220, y=20)

        Label(frame, text="SELECT SUBJECT").grid(column=1, row=1, padx=10, pady=0)
        selected_variable = StringVar()
        cmbox = ttk.Combobox(frame, width=17, textvariable=selected_variable)

        # Funkcja do aktualizacji wartości zmiennej StringVar
        def on_combobox_select(event):
            selected_variable = cmbox.get()
            self.show_attendance_in_table(attendanceFrame, selected_variable, self.getFirstName(), self.getLastName())
            
        cmbox.bind("<<ComboboxSelected>>", on_combobox_select)

        try:
            self.cursor.execute("SELECT name FROM Lessons WHERE class_ = %s",
                                 (self.getClass(),))  # używamy * przed conditionals
            names = self.cursor.fetchall()
            for name in names:
                value_to_add = ' '.join(str(item) for item in name) if len(name) > 1 else str(name[0])
                if value_to_add not in cmbox['values']:
                    cmbox['values'] = (*cmbox['values'], value_to_add)
        except mysql.connector.Error as err:
            messagebox.showinfo("ERROR", "ERROR COMBOBOX QUERY")

        cmbox.grid(column=1 + 1, row=1, pady=10)
        cmbox.current()
        
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

            self.frames["Show Attendance"] = ttk.Frame(notebook, width=600, height=600)
            self.frames["Show Attendance"].pack(fill='both', expand=True)
            notebook.add(frames["Show Attendance"], text = "Show Attendance")

            self.takeAttendance()
            self.showOneStudentAttendance(self.frames["Show Attendance"])

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
            label1.pack(pady=3)

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
            selected_class = classes.get()
            teacher = str(self.getFirstName() + " " + self.getLastName())

            m=StringVar()
            subjects = ttk.Combobox(self.frames["Attendance"], width = 27, textvariable = m)
            subjects.grid(column = 2, row = 5, padx=100, pady=0)
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
        

        classes.grid(column = 1, row = 5, padx=20, pady=50) 
        classes.current()

    def showOneStudentAttendance(self, frame):
        attendanceFrame = Frame(frame, width=400, height=400)
        attendanceFrame.grid(column=1, row=7, padx=10, pady=10)

        Label(frame, text="SELECT CLASS").grid(column=1, row=1, padx=10, pady=0)
        selected_class = StringVar()
        cmbox = ttk.Combobox(frame, width=17, textvariable=selected_class)

        # Funkcja do aktualizacji wartości zmiennej StringVar
        def on_combobox_select(event):
            selected_class = cmbox.get()
            selected_name = self.combobox(frame, "SELECT First name", 1, 2, "SELECT first_name FROM Users WHERE class_ = %s", selected_class)
            select_surename = self.combobox(frame, "SELECT LAST NAME", 1, 3, "SELECT last_name FROM Users WHERE class_ = %s", selected_class)
            selected_subject = self.combobox(frame, "SELECT SUBJECT", 1, 4, "SELECT name FROM Lessons WHERE class_ = %s", selected_class)


            confirm_btn = Button(frame, text = "SHOW",
                                command=lambda: self.show_attendance_in_table(attendanceFrame, selected_subject.get(), selected_name.get(), select_surename.get()),
                                cursor="hand2")
            confirm_btn.grid(column=1, row=5, padx=0, pady=10)

        cmbox.bind("<<ComboboxSelected>>", on_combobox_select)

        try:
            self.cursor.execute("SELECT name FROM Classes")
            names = self.cursor.fetchall()
            for name in names:
                value_to_add = ' '.join(str(item) for item in name) if len(name) > 1 else str(name[0])
                if value_to_add not in cmbox['values']:
                    cmbox['values'] = (*cmbox['values'], value_to_add)
        except mysql.connector.Error as err:
            messagebox.showinfo("ERROR", "ERROR COMBOBOX QUERY")

        cmbox.grid(column=1 + 1, row=1, pady=10)
        cmbox.current()


                
#----------------------------------TEACHER CLASS----------------------------------
class HeadTeacher(Teacher):
    def __init__(self, cursor, frames, notebook, conn, id, first_name, last_name, type, email):
        super().__init__(cursor, frames, notebook, conn, id, first_name, last_name, type, email) #WYWOŁANIE KONSTRUKTORA TEACHER
        self.frames["Menage users"] = ttk.Frame(notebook, width=600, height=600)
        self.frames["Menage users"].pack(fill='both', expand=True)
        notebook.add(frames["Menage users"], text = "Menage users")
        self.menageUsers(frames["Menage users"])

        self.frames["Modify lesson plan"] = ttk.Frame(notebook, width=600, height=600)
        self.frames["Modify lesson plan"].pack(fill='both', expand=True)
        notebook.add(frames["Modify lesson plan"], text = "Modify lesson plan")
        self.modifyLessonPlan(frames["Modify lesson plan"])
        

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
                tree.heading(col, text=col, command=lambda _col=col: self.sortby(tree, _col, 0))
                tree.column(col, width=100, anchor='center')

            # Adding data to treeview
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
        show_users_btn.place(x=frame.winfo_reqwidth()*3/4 - show_users_btn.winfo_reqwidth()/2, y=0)

        
        reset_password_btn = Button(frame, text="Reset Password", command=lambda: self.resetPassword(frame), cursor="hand2")
        reset_password_btn.place(x=frame.winfo_reqwidth()/4 - show_users_btn.winfo_reqwidth()/2, y=0)

        self.removeUser(removingUserFrame)
        self.registerUser(addingUserFrame)

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
        
    def registerUser(self, frame):
        first_name_label = Label(frame, text='FIRST NAME: ')
        first_name_label_tb = Entry(frame, width=30)
        first_name_label.pack(pady=3)
        first_name_label_tb.pack(pady=3)

        last_name_label= Label(frame, text='LAST NAME: ')
        last_name_label_tb = Entry(frame, width=30)
        last_name_label.pack(pady=3)
        last_name_label_tb.pack(pady=3)

        password_label1 = Label(frame, text='PASSWORD: ')
        password_label_tb1 = Entry(frame,show = "*", width=30)
        password_label1.pack(pady=3)
        password_label_tb1.pack(pady=3)
        
        password_label2 = Label(frame, text=' CONFIRM PASSWORD: ')
        password_label_tb2 = Entry(frame,show = "*", width=30)
        password_label2.pack(pady=3)
        password_label_tb2.pack(pady=3)

        type_label = Label(frame, text='ACCOUNT TYPE(1-Student, 2-Teacher, 3-Principal): ')
        type_tb = Entry(frame, width=30)
        type_label.pack(pady=3)
        type_tb.pack(pady=3)

        email_label = Label(frame, text='EMIAL: ')
        email_tb = Entry(frame, width=30)
        email_label.pack(pady=3)
        email_tb.pack(pady=3)

        class_label = Label(frame, text='CLASS: ')
        class_tb = Entry(frame, width=30)
        class_label.pack(pady=3)
        class_tb.pack(pady=3)

        def confirmRegisteration():
            if password_label_tb1.get() == password_label_tb2.get():
                info_str = "Registeration successfull"
                color = "green"
                hashed_password = generate_password_hash(password_label_tb1.get())
                self.cursor.execute("INSERT INTO Users (first_name, last_name, password, type, email, class_) VALUES (%s, %s, %s, %s, %s, %s)",
                            (first_name_label_tb.get(), last_name_label_tb.get(), hashed_password, type_tb.get(), email_tb.get(), class_tb.get()))
                self.conn.commit()
            else:
                info_str = "Registeration error"                                                                           
                color = "red"

            info = Label(frame, text=info_str, fg=color)
            info.pack(pady=3)

        register_btn = Button(frame, text="REGISTER",
                        command = confirmRegisteration,
                        cursor="hand2")
        register_btn.pack(pady=3)     

    def resetPassword(self, frame):
        top = Toplevel(frame)
        
        id_label = Label(top, text='ID')
        id_entry = Entry(top, width=30)
        id_label.pack(pady=3)
        id_entry.pack(pady=3)

        name_label = Label(top, text='Name')
        name_entry = Entry(top, width=30)
        name_label.pack(pady=3)
        name_entry.pack(pady=3)

        last_name_label = Label(top, text='Last Name')
        last_name_entry = Entry(top, width=30)
        last_name_label.pack(pady=3)
        last_name_entry.pack(pady=3)

        new_password_label = Label(top, text='Enter new password')
        new_password_entry = Entry(top, width=30)
        new_password_label.pack(pady=3)
        new_password_entry.pack(pady=3)

        commit_password_label = Label(top, text='Enter new password')
        commit_password_entry = Entry(top, width=30)
        commit_password_label.pack(pady=3)
        commit_password_entry.pack(pady=3)
        def update_password():
            # Hash the password
            if new_password_entry.get() == commit_password_entry.get():
                hashed_password = generate_password_hash(new_password_entry.get())
                try:
                    update_query = """
                    UPDATE Users SET password = %s WHERE id = %s AND first_name = %s AND last_name = %s
                    """
                    self.cursor.execute(update_query, (hashed_password, id_entry.get(), name_entry.get(), last_name_entry.get()))
                    self.conn.commit()
                    print(f"Password for User {id_entry.get()} has been updated!")
                    messagebox.showinfo("Success", "Password has been updated successfully!")
                except mysql.connector.Error as err:
                    messagebox.showerror("Database Error", f"Error updating password: {err}")

        update_button = Button(top, text='Update Password', command=update_password)
        update_button.pack(pady=3)

    def modifyLessonPlan(self, frame):
        addingLessonFrame = Frame(frame, bd=1, relief="solid")
        addingLessonFrame.place(x=0, y=30, width=frame.winfo_reqwidth()/2, height=frame.winfo_reqheight())
        
        adding_label = Label(addingLessonFrame, text="Adding Lesson", font=('tagoma', 12, 'bold'))
        adding_label.grid(row= 0,pady=20)  # Ustawiamy napis "Adding Lesson" na górze ramki
        
        removingLessonFrame = Frame(frame, bd=1, relief="solid")
        removingLessonFrame.place(x=frame.winfo_reqwidth()/2, y=30, width=frame.winfo_reqwidth()/2, height=frame.winfo_reqheight())

        removing_label = Label(removingLessonFrame, text="Delete Lesson", font=('tagoma', 12, 'bold'))
        removing_label.grid(row=0, pady=20)  # Ustawiamy napis "Lesson User" na górze ramki
        self.addingLesson(addingLessonFrame)
        self.removingLesson(removingLessonFrame)

        show_all_lessons_btn = Button(frame, text="Show all lessons", command=lambda: self.showAllLessons(frame), cursor="hand2")
        show_all_lessons_btn.place(x=frame.winfo_reqwidth()/4, y=0)

        def removingAllLessons():
            top = Toplevel(frame)
            password_label = Label(top, text='ENTER PASSWORD TO DELETE ALL LESSONS: ')
            password_tb = Entry(top, show = "*", width=40)
            password_label.grid(row=1, column=0, padx=20)
            password_tb.grid(row=1, column=1, padx=20)

            def checkPassword():
                self.cursor.execute("SELECT password FROM Users WHERE email=%s", (self.getEmail(),))
                pwd = self.cursor.fetchone()[0]
                
                if check_password_hash(pwd, password_tb.get()):
                    try:
                        # Użycie metod .get() na zmiennych StringVar
                        self.cursor.execute("DELETE FROM Lessons")
                        self.conn.commit()
                        messagebox.showinfo("SUCCESS", "Deleted lesson")

                    except mysql.connector.Error as err:
                        messagebox.showinfo("ERROR", "Error")

            confirm = Button(top, text='DELETE', command=checkPassword, cursor="hand2")  # using lambda to execute function utilizing the textbox entries
            confirm.grid(row=2, column=1, columnspan=1, pady=10, padx=10, ipadx=50)
            


        delete_all_lessons_btn = Button(frame, text="Delete all lessons", command=removingAllLessons, cursor="hand2")
        delete_all_lessons_btn.place(x=frame.winfo_reqwidth()*3/4, y=0)
    def addingLesson(self, frame):
        # Tworzenie zmiennych StringVar na poziomie klasy
        selected_class_var = StringVar()
        selected_subject_var = StringVar()
        selected_teacher_var = StringVar()
        selected_start_time_var = StringVar()
        selected_end_time_var = StringVar()
        selected_day_var = StringVar()
        selected_classroom_var = StringVar()

        # Przesyłanie zmiennych StringVar do funkcji combobox
        selected_class_var = self.combobox(frame, "CLASS", 0, 1, "SELECT name FROM Classes")
        selected_subject_var = self.combobox(frame, "SUBJECTS", 0, 2, "SELECT name FROM Subjects")
        selected_teacher_var = self.combobox(frame, "TEACHERS", 0, 3, "SELECT first_name, last_name FROM Users WHERE type != 'STUDENT'")
        selected_start_time_var = self.combobox(frame, "LESSONS START TIMES", 0, 4, "SELECT start_time FROM LessonTimes")
        selected_end_time_var = self.combobox(frame, "LESSONS END TIMES", 0, 5, "SELECT end_time FROM LessonTimes")
        selected_day_var = self.combobox(frame, "DAYS", 0, 6, "SELECT day_name FROM Weekdays")
        selected_classroom_var = self.combobox(frame, "CLASSROOM", 0, 7, "SELECT room_number FROM Classrooms")

        def commitAdding():
            try:
                # Użycie metod .get() na zmiennych StringVar
                self.cursor.execute(
                    "INSERT INTO Lessons (name, classroom, class_, day_of_week, teacher, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (
                        selected_subject_var.get(),
                        selected_classroom_var.get(),
                        selected_class_var.get(),
                        selected_day_var.get(),
                        selected_teacher_var.get(),
                        selected_start_time_var.get(),
                        selected_end_time_var.get()
                    )
                )
                self.conn.commit()
                messagebox.showinfo("SUCCESS", "Added lesson")

            except mysql.connector.Error as err:
                messagebox.showinfo("ERROR", "Could not add lesson")

        commitButton = Button(frame, text="commit", command=commitAdding, cursor="hand2")
        commitButton.grid(column=1, row=8, padx=10, pady=10)
    def removingLesson(self, frame):
        selected_class_var = StringVar()
        selected_subject_var = StringVar()
        selected_teacher_var = StringVar()
        selected_start_time_var = StringVar()
        selected_end_time_var = StringVar()
        selected_day_var = StringVar()
        selected_classroom_var = StringVar()

        # Przesyłanie zmiennych StringVar do funkcji combobox
        selected_class_var = self.combobox(frame, "CLASS", 0, 1, "SELECT class_ FROM Lessons")
        selected_subject_var = self.combobox(frame, "SUBJECTS", 0, 2, "SELECT name FROM Lessons")
        selected_teacher_var = self.combobox(frame, "TEACHERS", 0, 3, "SELECT teacher FROM Lessons")
        selected_start_time_var = self.combobox(frame, "LESSONS START TIMES", 0, 4, "SELECT start_time FROM Lessons")
        selected_end_time_var = self.combobox(frame, "LESSONS END TIMES", 0, 5, "SELECT end_time FROM Lessons")
        selected_day_var = self.combobox(frame, "DAYS", 0, 6, "SELECT day_of_week FROM Lessons")
        selected_classroom_var = self.combobox(frame, "CLASSROOM", 0, 7, "SELECT classroom FROM Lessons")
        def commitAdding():
            try:
                # Użycie metod .get() na zmiennych StringVar
                self.cursor.execute(
                    """
                    DELETE FROM Lessons WHERE 
                        name = %s AND
                        classroom = %s AND
                        class_ = %s AND
                        day_of_week = %s AND
                        teacher = %s AND
                        start_time = %s AND
                        end_time = %s
                    """,
                    (
                        selected_subject_var.get(),
                        selected_classroom_var.get(),
                        selected_class_var.get(),
                        selected_day_var.get(),
                        selected_teacher_var.get(),
                        selected_start_time_var.get(),
                        selected_end_time_var.get()
                    )
                )
                self.conn.commit()
                messagebox.showinfo("SUCCESS", "Added lesson")

            except mysql.connector.Error as err:
                messagebox.showinfo("ERROR", "Could not add lesson")

        commitButton = Button(frame, text="commit", command=commitAdding, cursor="hand2")
        commitButton.grid(column=1, row=8, padx=10, pady=10)

    def showAllLessons(self, frame):
                top = Toplevel(frame)
                self.cursor.execute("SELECT id, name, classroom, class_, day_of_week, teacher, start_time, end_time from Lessons")
                users = self.cursor.fetchall()

                container = Frame(top)
                container.pack(fill='both', expand=True)

                columns = ('ID', 'SUBJECT', 'CLASSROOM', 'CLASS', 'DAY_OF_WEEK', 'TEACHER', 'START', 'END')
                tree = ttk.Treeview(container, columns=columns, show='headings')

                # Defining column headings
                for col in columns:
                    tree.heading(col, text=col, command=lambda _col=col: self.sortby(tree, _col, 0))
                    tree.column(col, width=100, anchor='center')

                # Adding data to treeview
                for (id, subject, classroom, class_, day_of_week, teacher, start_time, end_time) in users:
                    tree.insert('', 'end', values=(id, subject, classroom, class_, day_of_week, teacher, start_time, end_time))

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