import mysql.connector
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from User import User
import datetime

class Teacher(User):
    def __init__(self, root, cursor, conn, id, first_name, last_name, password, type, email):
            #load info about student
            # self._current_user = {
            #     "id": id,
            #     "first_name": first_name,
            #     "last_name": last_name,
            #     "type": type,
            #     "email": email
            # }
            super().__init__(root, cursor, conn, id, first_name, last_name, password, type, email, class_ = "") #WYWOŁANIE KONSTRUKTORA USER

            self.frames["Attendance"] = ttk.Frame(self.notebook, width=600, height=600)
            self.frames["Attendance"].pack(fill='both', expand=True)
            self.notebook.add(self.frames["Attendance"], text = "Attendance")

            self.frames["Show Attendance"] = ttk.Frame(self.notebook, width=600, height=600)
            self.frames["Show Attendance"].pack(fill='both', expand=True)
            self.notebook.add(self.frames["Show Attendance"], text = "Show Attendance")


            #Kolejna ramka (ta u góry) dla ocen:
            # self.frames["Grades"] = ttk.Frame(self.notebook, width=600, height=600)
            # self.frames["Grades"].pack(fill='both', expand=True)
            # self.notebook.add(self.frames["Grades"], text = "Grades")

            self.teacher = str(self.getFirstName() + " " + self.getLastName())

            self.takeAttendance()
            self.showOneStudentAttendance()
            self.insertGrade()

    def showScheduleOfDay(self, frame, day):        
        teacher_name = str(self._current_user["first_name"] + " " + self._current_user["last_name"])
        label = Label(frame, text=day, fg='#97ffff', bg='black', font=('tagoma', 8, 'bold'))
        label.pack(pady=5)

        query = ("SELECT start_time, end_time, subject, classroom, class_ "
                "FROM Lessons "
                "WHERE day_of_week = %s AND teacher = %s "
                "ORDER BY start_time")

        self.cursor.execute(query, (day, teacher_name))
        lessons = self.cursor.fetchall()

        if len(lessons) != 0:
            for index, (start_time, end_time, name, classroom, class_) in enumerate(lessons):
                lb = Label(frame, text=f"{start_time} - {end_time} {name} {classroom} {class_}", font=('tagoma', 8, 'bold'))
                lb.pack(pady=2)

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

    def modifyAttendance(self):
        top = Toplevel(self.frames["Attendance"])
        top.title("Modify Attendance")

        date_label = Label(top, text='Select Date (YYYY-MM-DD):')
        date_label.grid(row=0, column=0)
        date_entry = Entry(top, width=30)
        date_entry.grid(row=0, column=1)

        student_id_label = Label(top, text='Enter student\'s id')
        student_id_label.grid(row=1, column=0)
        student_id_entry = Entry(top, width=30)
        student_id_entry.grid(row=1, column=1)

        status_label = Label(top, text='Enter status(PRESENT/LATE/ABSENT)')
        status_label.grid(row=2, column=0)
        status_entry = Entry(top, width=30)
        status_entry.grid(row=2, column=1)

        selected_start_time_var = self.combobox(top, "LESSONS START TIMES", 3, 0, "SELECT start_time FROM LessonTimes")

        def saveChanges():
            try:
                self.cursor.execute("UPDATE Attendance SET status = %s WHERE student_id = %s AND date = %s AND start_time = %s",
                                    (status_entry.get(), student_id_entry.get(), date_entry.get(), selected_start_time_var.get()))
                self.conn.commit()
                messagebox.showinfo("Success", "Changes saved successfully!")
            except mysql.connector.Error as err:
                messagebox.showinfo("ERROR", "ERROR COMBOBOX QUERY")

        change_btn = Button(top, text = "CONFIRM MODIFY",
            command=saveChanges, cursor="hand2",
            width=15, height=3, font='Helvetica, 15', bg='#0052cc', fg='#ffffff',)
        change_btn.grid(row=2, column=2, padx=5)
        
    def takeAttendance(self):
        n = StringVar() 
        #attendance_frame_middle = self.frames["Attendance"].winfo_reqwidth/2

        class_label = Label(self.frames["Attendance"], text = "SELECT CLASS", width=40)
        class_label.place(x=15, y = 15)
        classes = ttk.Combobox(self.frames["Attendance"], width = 30, textvariable = n) 
        classes.place(x=15 + class_label.winfo_reqwidth() , y=15)
        classes.current()

        m=StringVar()
        subject_label = Label(self.frames["Attendance"], text = "SELECT SUBJECT", width=40)
        subject_label.place(x=15, y=50)
        subjects = ttk.Combobox(self.frames["Attendance"], width = 30, textvariable = m)
        subjects.place(x=15 + class_label.winfo_reqwidth(), y = 50)


        selected_start_time_var = self.combobox(frame=self.frames["Attendance"], txt = "LESSONS START TIMES",
                                                row_=0, column_ = 0, x=15, y=85, cmbox_width=30, text_width=40,
                                                qry="SELECT 1")
        
        selected_end_time_var = self.combobox(frame = self.frames["Attendance"], txt="LESSONS END TIMES",
                                              row_=0, column_ = 0, x=15, y=120, cmbox_width=30, text_width=40,
                                              qry="SELECT 1")

        #FUNCTION ANSWERS FOR 1ST COMBOBOX --CLASSES
        def on_class_selected(event):
            selected_class = classes.get()

            #FUNCTION ANSWERS FOR 2nd COMBOBOX SUBJECTS
            def showStudents(event):
                selected_subject = subjects.get()


                
                selected_start_time_var = self.combobox(
                    self.frames["Attendance"],
                    "LESSONS START TIMES",
                    0,
                    0,
                    "SELECT start_time FROM Lessons WHERE subject = %s and teacher = %s",
                    15,
                    85,
                    30,
                    40,
                    selected_subject,
                    str(self.getFirstName() + " " + self.getLastName()))
                
                selected_end_time_var = self.combobox(
                    self.frames["Attendance"],
                    "LESSONS END TIMES",
                    0,
                    0,
                    "SELECT end_time FROM Lessons WHERE subject = %s and teacher = %s",
                    15,
                    120,
                    30,
                    40,
                    selected_subject,
                    str(self.getFirstName() + " " + self.getLastName()))

                attendance_vars = []
                self.cursor.execute("SELECT id, first_name, last_name FROM Users WHERE class_ = %s", (selected_class,))
                students = self.cursor.fetchall()

                usersTableFrame = Frame(self.frames["Attendance"], bd=1, relief="solid", width=500, height=300)
                #usersTableFrame.grid_propagate(0)  # Zapobiega dostosowywaniu wymiarów do zawartości
                usersTableFrame.place(x=10, y=150)

                canva = Canvas(usersTableFrame, width=500, height=300)
                canva.pack(side=LEFT, fill=BOTH, expand=True)

                scrollbar = Scrollbar(usersTableFrame, orient=VERTICAL, command=canva.yview)
                scrollbar.pack(side=RIGHT, fill=Y)

                canva.configure(yscrollcommand=scrollbar.set)
                frame = Frame(canva)
                canva.create_window((0, 0), window=frame, anchor="nw")

                ttk.Label(frame, text="Name").grid(row=0, column=0, padx=10)
                ttk.Label(frame, text="Last Name").grid(row=0, column=1, padx=30)
                ttk.Label(frame, text="Attendance").grid(row=0, column=3, padx=20)


                for index, (student_id, first_name, last_name) in enumerate(students, start = 1):
                    l1= ttk.Label(frame, text=first_name)
                    l1.grid(row=index, column = 0)
                    l2= ttk.Label(frame, text=last_name)
                    l2.grid(row=index, column = 1)

                    # Attendance radio buttons
                    attendance = StringVar()
                    
                    rb3 = ttk.Radiobutton(frame, text="Present", variable=attendance, value="PRESENT")
                    rb3.grid(row=index, column=2,padx=(0, 3), sticky="w")  # "Late" w środku
                    
                    rb4 = ttk.Radiobutton(frame, text="Late", variable=attendance, value="LATE")
                    rb4.grid(row=index, column=3, padx=(0, 3), sticky="n")  # "Present" na prawo od "Late"
                    
                    rb5 = ttk.Radiobutton(frame, text="Absent", variable=attendance, value="ABSENT")
                    rb5.grid(row=index, column=4, padx=(3, 0), sticky="e")  # "Absent" na lewo od "Late"
                    attendance_vars.append(attendance)
                canva.config(scrollregion=canva.bbox("all"))

                def saveAttendance():
                                    
                    try:
                        with self.conn.cursor() as cursor:
                            empty_entries = [var for var in attendance_vars if not var.get()]
                            if not empty_entries and len(selected_end_time_var.get()) > 0 and len(selected_start_time_var.get()) > 0:
                                current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                for index, (student_id, _, _) in enumerate(students):
                                    self.cursor.execute("""INSERT INTO Attendance(student_id, date, start_time, end_time,
                                                        status, subject, class_) VALUES(%s, %s, %s,%s, %s, %s, %s)""",
                                                        (student_id, current_date, selected_start_time_var.get(), selected_end_time_var.get(),
                                                        attendance_vars[index].get(), selected_subject, selected_class))
                                self.conn.commit()

                                def clear_and_redraw():
                                    # Usuwanie wszystkich widgetów w ramce
                                    for widget in self.frames["Attendance"].winfo_children():
                                        widget.destroy()
                                    self.takeAttendance()

                                messagebox.showinfo("Success", "Attendance results saved successfully!")

                                # Czyszczenie i przerysowanie zawartości ramki
                                clear_and_redraw()
                    except Exception as e:
                        messagebox.showinfo("Error", f"An error occurred: {str(e)}")





                b1 = Button(self.frames["Attendance"], text = "SAVE",
                            command=saveAttendance, cursor="hand2",
                            width=15, height=3, font='Helvetica, 15', bg='#0052cc', fg='#ffffff',)
                b1.place(x=self.frames["Attendance"].winfo_reqwidth()/2 - b1.winfo_reqwidth()/2, y = 480)
                
                b2 = Button(self.frames["Attendance"], text = "MODIFY",
                            command=self.modifyAttendance, cursor="hand2",
                            width=10, height=3, font='Helvetica, 15', bg='#0052cc', fg='#ffffff',)
                b2.place(x=5, y = 480)
            subjects.bind("<<ComboboxSelected>>", showStudents)

            self.cursor.execute("SELECT subject FROM Lessons WHERE class_ = %s and teacher = %s",
            (selected_class, self.teacher))
            subject_names = self.cursor.fetchall()
            subject_values = list(set([s_name[0] for s_name in subject_names]))
            subjects.configure(values=subject_values)

        classes.bind("<<ComboboxSelected>>", on_class_selected)
        
        self.cursor.execute("SELECT name FROM Classes")
        names = self.cursor.fetchall()

        for name in names:
            if name[0] not in classes['values']:
                classes['values'] = (*classes['values'], name[0])
        
    def showGradesOfClass(self):
        n = StringVar() 

        top = Toplevel(self.frames["Grades"])
        top.geometry('580x400')
        top.resizable(width=False, height=False)

        Label(top, text = "SELECT CLASS").pack()
        classes = ttk.Combobox(top, width = 10, textvariable = n) 
        classes.pack()
        classes.current()

        
        m=StringVar()
        Label(top, text = "SELECT SUBJECT").pack()
        subjects = ttk.Combobox(top, width = 27, textvariable = m)

        

        def on_class_selected(event):
            selected_class = classes.get()
            

            subjects.pack()
            self.cursor.execute("SELECT id, first_name, last_name FROM Users WHERE class_ = %s", (selected_class,))
            students = self.cursor.fetchall()

            


            def on_subject_selected(event):
                selected_subject = subjects.get()

                #----------TREEEEEEEEEE---------------
                container = Frame(top)
                container.pack(fill='both', expand=True)

                columns = ('ID', 'First Name', 'Last Name', "Grade", "Average")
                tree = ttk.Treeview(container, columns=columns, show='headings')
                tree.grid(row=0, column=0, sticky='nsew')
                tree.column('#1', width=20) #id
                tree.column('#2', width=150) #name
                tree.column('#3', width=150) #surname
                tree.column('#4', width=100)  #grades
                tree.column('#5', width=50)  #average

                

                scrollbar = ttk.Scrollbar(container, orient=VERTICAL, command=tree.yview)
                tree.configure(yscroll=scrollbar.set)
                scrollbar.grid(row=0, column=1, sticky='ns')

                for col in columns:
                    tree.heading(col, text=col, command=lambda _col=col: self.sortby(tree, _col, 0))
                    tree.column(col, anchor='center')
                for index, (id, first_name, last_name) in enumerate(students, start=0):
                    self.cursor.execute("SELECT grade, grades_weight FROM Grades WHERE teacher = %s AND subject = %s AND student_id=%s", (self.teacher, selected_subject, id))
                    grades_for_student = self.cursor.fetchall()

                    # Tworzymy listę ocen jako stringi (możesz dostosować to zależnie od struktury danych, jaką chcesz użyć)
                    grades_as_strings = [f"{grade}" for grade, _ in grades_for_student]

                    if grades_for_student:
                        grades_sum = sum(grade for grade, _ in grades_for_student)
                        average = grades_sum / len(grades_for_student)
                    else:
                        average = "No grades available"

                    # Tworzymy jedną wartość dla kolumny 'grades', łącząc oceny za pomocą przecinków
                    grades_column_value = ", ".join(grades_as_strings)

                    # Teraz możemy wstawić wiersz do drzewa (o ile masz dostęp do drzewa, co zakładam na podstawie poprzedniego kodu)
                    tree.insert(parent='', index='end', values=(id, first_name, last_name, grades_column_value, average))
            
            subjects.bind("<<ComboboxSelected>>", on_subject_selected)

            self.cursor.execute("SELECT subject FROM Lessons WHERE class_ = %s and teacher = %s",
            (selected_class, self.teacher))
            subject_names = self.cursor.fetchall()
            subject_values = list(set([s_name[0] for s_name in subject_names]))
            subjects.configure(values=subject_values)
            

        classes.bind("<<ComboboxSelected>>", on_class_selected)
        self.cursor.execute("SELECT name FROM Classes")
        names = self.cursor.fetchall()

        for name in names:
            if name[0] not in classes['values']:
                classes['values'] = (*classes['values'], name[0])

    def removeGrade(self):
        frame_width = 600
        frame_height = 600
        selected_iid = None
        removed_ids_grades = []
        top = Toplevel(self.frames["Grades"])
        top.title("Remove grade")
        top.geometry(f"{frame_width}x{frame_height}")
        top.resizable(width=False, height=False)

        m=StringVar()
        n=StringVar()
        class_label = Label(top, text = "SELECT CLASS")
        class_label.place(x=frame_width/2 - class_label.winfo_reqwidth() - 15, y=10)
        classes = ttk.Combobox(top, width = 27, textvariable = n,) 
        classes.place(x = frame_width/2, y=10)
        classes.current()


        last_name_label = Label(top, text = "SELECT LAST NAME", width = 30)
        last_name_label.place(x=frame_width/2 - last_name_label.winfo_reqwidth() - 15, y=130)
        last_names = ttk.Combobox(top, width = 27, textvariable = n)
        last_names.place(x = frame_width/2, y=130)



        first_name_cmbox = self.combobox(top, "SELECT FIRST NAME", 0, 0, "SELECT 1",
                                        60, 90, 27, 30)
        
        subject_cmbox = self.combobox(top, "SELECT SUBJECT", 0, 0, "SELECT 1",
                                        60, 50, 27, 30)

        def on_class_selected(event):
            selected_class = classes.get()
            print("Class: ", selected_class)
            first_name_cmbox = self.combobox(top, "SELECT FIRST NAME", 0, 0, "SELECT first_name from Users WHERE class_ = %s",
                                            60, 90, 27, 30, selected_class)
            
            
            subject_cmbox = self.combobox(top, "SELECT SUBJECT", 0, 0, "SELECT subject FROM Lessons WHERE class_ = %s and teacher = %s",
                                            60, 50, 27, 30, selected_class, self.teacher)
            
            container = Frame(top, width=frame_width-30, height=frame_height/2)
            container.place(x=15, y = 200)

            
            def on_last_name_selected(event):
                selected_last_name=last_names.get()

                print("First name: ", first_name_cmbox.get())
                print("Last name: ", selected_last_name)
                print("Subject: ", subject_cmbox.get())
                self.cursor.execute("SELECT id FROM Users WHERE class_ = %s AND first_name = %s AND last_name = %s", (selected_class, first_name_cmbox.get(), selected_last_name))
                result = self.cursor.fetchone()
                if result:
                    student_id = result[0]
                    self.cursor.fetchall()

                    self.cursor.execute("SELECT id, grade, grades_weight, date FROM Grades WHERE teacher = %s AND subject = %s AND student_id=%s", (self.teacher, subject_cmbox.get(), student_id))
                    grades = self.cursor.fetchall()

                for widget in container.winfo_children():
                    widget.destroy()
                columns = ('Grade id', 'ID', "Grade", "Grades's weight", "Date")
                tree = ttk.Treeview(container, columns=columns, show='headings')
                tree.grid(row=0, column=0, sticky='nsew')

                #----------TREEEEEEEEEE---------------
                tree.column('#1', width=1) #grade ID
                tree.column('#2', width=40) #ID
                tree.column('#3', width=200) #Grade
                tree.column('#4', width=150) #grade's weight
                tree.column('#5', width=150) #date
                
                scrollbar = ttk.Scrollbar(container, orient=VERTICAL, command=tree.yview)
                tree.configure(yscroll=scrollbar.set)
                scrollbar.grid(row=0, column=1, sticky='ns')


                #zaznaczenie row któego się klikneło 2krotknie i możliwość usunięcia go
                def on_double_click(event):
                    nonlocal selected_iid
                    region_clicked = tree.identify_region(event.x, event.y)
                    if region_clicked == "cell":
                        selected_iid = tree.focus()
                        print(selected_iid)



                
                #porównanie tego co jest aktualnie w drzewie i danych z grades które do niego weszły i na tej podstawie usunięcie tej oceny z bazy danych
                def save():
                    for id in removed_ids_grades:
                        self.cursor.execute("DELETE FROM Grades WHERE id = %s", (id,))
                        self.conn.commit()
                        print("grade removed")

                #usunięcie zaznaczonego rzędu
                def remove():
                    nonlocal selected_iid
                    print(selected_iid)
                    print("Remove button clicked")
                    if selected_iid is not None:
                        removed_ids_grades.append(tree.item(selected_iid, "values")[0])
                        tree.delete(selected_iid)


                tree.bind("<Double-1>", on_double_click)

                for col in columns:
                    tree.heading(col, text=col, command=lambda _col=col: self.sortby(tree, _col, 0))
                    tree.column(col, anchor='center')

                for (id, grade, grades_weight, date) in grades:
                    tree.insert(parent='', index='end', values=(id, student_id, grade, grades_weight, date))

                #SAVE AND REMOVE BTNS
                save_btn = Button(top, text = "SAVE AND CLOSE", cursor="hand2", command=save,
                    width=15, height=3, font='Helvetica, 15', bg='#0052cc', fg='#ffffff')
                save_btn.place(x=frame_width - save_btn.winfo_reqwidth() - 5, y=frame_height-60)

                remove_grade_btn = Button(top, text = "REMOVE", cursor="hand2", command=remove,
                    width=15, height=3, font='Helvetica, 15', bg='#0052cc', fg='#ffffff')
                remove_grade_btn.place(x=5, y = frame_height-60)

            ################    on_last_name_selected   END     ##############################

            last_names.bind("<<ComboboxSelected>>", on_last_name_selected)
            self.cursor.execute("SELECT last_name from Users WHERE class_ = %s", (selected_class, ))
            last_names_names = self.cursor.fetchall()
            last_names_values = list(set([s_name[0] for s_name in last_names_names]))
            last_names.configure(values=last_names_values)
        ################    on_class_selected   END     ##############################   


        classes.bind("<<ComboboxSelected>>", on_class_selected)
        self.cursor.execute("SELECT name FROM Classes")
        names = self.cursor.fetchall()

        for name in names:
            if name[0] not in classes['values']:
                classes['values'] = (*classes['values'], name[0])

    def insertGrade(self):

        grades_frame_middle = self.frames["Grades"].winfo_reqwidth()/2

        show_grades_btn = Button(self.frames["Grades"], text = "SHOW GRADES", cursor="hand2", command=self.showGradesOfClass,
            width=15, height=3, font='Helvetica, 15', bg='#0052cc', fg='#ffffff')
        show_grades_btn.place(x=grades_frame_middle*2 - show_grades_btn.winfo_reqwidth() - 5, y=400)


        remove_grade_btn = Button(self.frames["Grades"], text = "REMOVE GRADES", cursor="hand2", command=self.removeGrade,
            width=15, height=3, font='Helvetica, 15', bg='#0052cc', fg='#ffffff')
        remove_grade_btn.place(x=5, y = 400)
        n = StringVar() 

        class_label = Label(self.frames["Grades"], text = "SELECT CLASS")
        class_label.place(x=grades_frame_middle - class_label.winfo_reqwidth(), y=10)
        classes = ttk.Combobox(self.frames["Grades"], width = 10, textvariable = n) 
        classes.place(x = grades_frame_middle + 15, y=10)
        classes.current()



        m=StringVar()
        subject_label = Label(self.frames["Grades"], text = "SELECT SUBJECT")
        subject_label.place(x=grades_frame_middle - subject_label.winfo_reqwidth(), y=50)
        subjects = ttk.Combobox(self.frames["Grades"], width = 27, textvariable = m)
        subjects.place(x = grades_frame_middle + 15, y=50)


        def on_class_selected(event):
            selected_class = classes.get()

            container = Frame(self.frames["Grades"], width=grades_frame_middle*2, height=300)
            container.place(x=grades_frame_middle - container.winfo_reqwidth()/2 + 15, y = 100)

            self.cursor.execute("SELECT id, first_name, last_name FROM Users WHERE class_ = %s", (selected_class,))
            students = self.cursor.fetchall()

            def on_subject_selected(event):
                selected_subject = subjects.get()

                for widget in container.winfo_children():
                    widget.destroy()
                columns = ('ID', 'First Name', 'Last Name', "Grade", "Grades's weight")
                tree = ttk.Treeview(container, columns=columns, show='headings')
                tree.grid(row=0, column=0, sticky='nsew')




                #----------TREEEEEEEEEE---------------
                tree.column('#1', width=20)
                tree.column('#2', width=150) 
                tree.column('#3', width=150) 
                tree.column('#4', width=100) 
                tree.column('#5', width=100) 
                

                scrollbar = ttk.Scrollbar(container, orient=VERTICAL, command=tree.yview)
                tree.configure(yscroll=scrollbar.set)
                scrollbar.grid(row=0, column=1, sticky='ns')

                def on_double_click(event):
                    #Identify the region
                    region_clicked = tree.identify_region(event.x, event.y)
                    #identify the column
                    col_clicked = tree.identify_column(event.x)

                    #Only intrested on column 4, 5 (Grades and grade's weight)
                    if region_clicked == "cell" and col_clicked in ("#4", "#5"):
                        #Identify which item was clicked
                        
                        selected_iid = tree.focus()
                        selected_values = tree.item(selected_iid)
                        #print("Double-click in column:", col_clicked, " and row: ", selected_iid, " selected values: ", selected_values.get("values")[int(col_clicked[1:]) - 1])

                        column_box = tree.bbox(selected_iid, col_clicked)
                        entry_edit = ttk.Entry(self.frames["Grades"])

                        #Record the column index and iid
                        entry_edit.editing_column_index = col_clicked
                        entry_edit.editing_item_iid = selected_iid

                        entry_edit.insert(0, selected_values.get("values")[int(col_clicked[1:]) - 1])
                        entry_edit.select_range(0, END)
                        entry_edit.focus()

                        def on_focus_out(event):
                            event.widget.destroy()
                        def on_enter_pressed(event):
                            new_text = event.widget.get()
                            selected_iid = event.widget.editing_item_iid
                            col_clicked = event.widget.editing_column_index

                            if col_clicked == -1:
                                tree.item(selected_iid, text=new_text)
                            else:   
                                current_values = tree.item(selected_iid).get("values")
                                current_values[int(col_clicked[1:]) - 1] = new_text
                                tree.item(selected_iid, values=current_values)

                            event.widget.destroy()

                        entry_edit.bind("<FocusOut>", on_focus_out)
                        entry_edit.bind("<Return>", on_enter_pressed)

                        entry_edit.place(x=column_box[0], y=column_box[1] + container.winfo_y(), width=column_box[2], height=column_box[3])

                def save():
                    for row_id in tree.get_children():
                        row = tree.item(row_id)["values"]
                        if row[3] != "Enter grade" and row[4] != "Enter grades's weight":
                            try:
                                self.cursor.execute("""INSERT INTO Grades (student_id, grade, teacher, subject, date, grades_weight)     VALUES (%s, %s, %s, %s, %s, %s)""",
                                (row[0], row[3], self.teacher, selected_subject, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), row[4]))
                                self.conn.commit()
                            except Exception as e:
                                messagebox.showinfo("Error", f"An error occurred: {str(e)}")
                            else:
                                print(row[0], row[3], self.teacher, selected_subject, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), row[4])
                        
                tree.bind("<Double-1>", on_double_click)

                

                for col in columns:
                    tree.heading(col, text=col, command=lambda _col=col: self.sortby(tree, _col, 0))
                    tree.column(col, anchor='center')

                for (id, first_name, last_name) in students:
                    grade = Entry(self.frames["Grades"])
                    tree.insert(parent='', index='end', values=(id, first_name, last_name, "Enter grade", "Enter grades's weight"))




                b1 = Button(self.frames["Grades"], text = "SAVE", cursor="hand2", command=save,
                            width=15, height=3, font='Helvetica, 15', bg='#0052cc', fg='#ffffff',)
                b1.place(x=self.frames["Grades"].winfo_width()/2 - b1.winfo_reqwidth()/2, y = 400)
                

                
                
            subjects.bind("<<ComboboxSelected>>", on_subject_selected)

            self.cursor.execute("SELECT subject FROM Lessons WHERE class_ = %s and teacher = %s",
            (selected_class, self.teacher))
            subject_names = self.cursor.fetchall()
            subject_values = list(set([s_name[0] for s_name in subject_names]))
            subjects.configure(values=subject_values)

        classes.bind("<<ComboboxSelected>>", on_class_selected)
        self.cursor.execute("SELECT name FROM Classes")
        names = self.cursor.fetchall()

        for name in names:
            if name[0] not in classes['values']:
                classes['values'] = (*classes['values'], name[0])

    def showOneStudentAttendance(self):
        attendanceFrame = Frame(self.frames["Show Attendance"], width=400, height=400)
        attendanceFrame.grid(column=1, row=7, padx=10, pady=10)

        Label(self.frames["Show Attendance"], text="SELECT CLASS").grid(column=1, row=1, padx=10, pady=0)
        selected_class = StringVar()
        cmbox = ttk.Combobox(self.frames["Show Attendance"], width=17, textvariable=selected_class)
        cmbox.current()

        selected_class = "1B"
        selected_name = self.combobox(self.frames["Show Attendance"], "SELECT First name", 1, 2, "SELECT first_name FROM Users WHERE class_ = %s", -255, -255, 17, -255, selected_class)
        select_surename = self.combobox(self.frames["Show Attendance"], "SELECT LAST NAME", 1, 3, "SELECT last_name FROM Users WHERE class_ = %s", -255, -255, 17, -255, selected_class)
        selected_subject = self.combobox(self.frames["Show Attendance"], "SELECT SUBJECT", 1, 4, "SELECT subject FROM Lessons WHERE class_ = %s", -255, -255, 17, -255, selected_class)

        # Funkcja do aktualizacji wartości zmiennej StringVar
        def on_combobox_select(event):
            selected_class = cmbox.get()
            selected_name = self.combobox(self.frames["Show Attendance"], "SELECT First name", 1, 2, "SELECT first_name FROM Users WHERE class_ = %s", -255, -255, 17, -255, selected_class)
            select_surename = self.combobox(self.frames["Show Attendance"], "SELECT LAST NAME", 1, 3, "SELECT last_name FROM Users WHERE class_ = %s", -255, -255, 17, -255, selected_class)
            selected_subject = self.combobox(self.frames["Show Attendance"], "SELECT SUBJECT", 1, 4, "SELECT subject FROM Lessons WHERE class_ = %s", -255, -255, 17, -255, selected_class)


            confirm_btn = Button(self.frames["Show Attendance"], text = "SHOW",
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
       