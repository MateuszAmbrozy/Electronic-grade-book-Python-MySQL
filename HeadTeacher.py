from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from Teacher import Teacher

class HeadTeacher(Teacher):
    def __init__(self, root, cursor, conn, id, first_name, last_name, password, type, email):
        super().__init__(root, cursor, conn, id, first_name, last_name, password, type, email) #WYWOŁANIE KONSTRUKTORA TEACHER
        self.frames["Menage users"] = ttk.Frame(self.notebook, width=600, height=600)
        self.frames["Menage users"].pack(fill='both', expand=True)
        self.notebook.add(self.frames["Menage users"], text = "Menage users")
        self.menageUsers(self.frames["Menage users"])

        self.frames["Modify lesson plan"] = ttk.Frame(self.notebook, width=600, height=600)
        self.frames["Modify lesson plan"].pack(fill='both', expand=True)
        self.notebook.add(self.frames["Modify lesson plan"], text = "Modify lesson plan")
        self.modifyLessonPlan(self.frames["Modify lesson plan"])
        
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
                    self.conn.start_transaction()
                    self.cursor.execute("SELECT email FROM Users WHERE id = %s", (id_entry.get(),))
                    user_email = self.cursor.fetchone()

                    self.cursor.execute("DELETE FROM Messages WHERE senderEmail = %s OR receiverEmail = %s", (user_email[0], user_email[0]))

                    self.cursor.execute("DELETE FROM Grades WHERE student_id = %s", (id_entry.get(),))

                    self.cursor.execute("DELETE FROM Attendance WHERE student_id = %s", (id_entry.get(),))

                        
                    self.cursor.execute("DELETE FROM Users WHERE id = %s AND first_name = %s AND last_name = %s",
                        (id_entry.get(), name_entry.get(), last_name_entry.get()))
                    self.conn.commit()
                   
                    messagebox.showinfo("Success", "Delete successfull!")
            except mysql.connector.Error as err:
                    self.conn.rollback()
                    messagebox.showinfo("Failure", f"Delete failure! {err}")

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
            first_name_value = first_name_label_tb.get()
            last_name_value = last_name_label_tb.get()
            password_value1 = password_label_tb1.get()
            password_value2 = password_label_tb2.get()
            type_value = type_tb.get()
            email_value = email_tb.get()
            class_value = class_tb.get()

    # Sprawdź, czy którykolwiek z pól (oprócz 'class') jest pusty
            
            if ((password_value1 == password_value2) and
                (all([first_name_value, last_name_value, password_value1, password_value2, type_value, email_value]))):
                info_str = "Registeration successfull"
                color = "green"
                hashed_password = generate_password_hash(password_value1)
                self.cursor.execute("INSERT INTO Users (first_name, last_name, password, type, email, class_) VALUES (%s, %s, %s, %s, %s, %s)",
                            (first_name_value,last_name_value, hashed_password, type_value, email_value, class_value))
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

        update_button = Button(top, text='Update Password', command=update_password, cursor="hand2")
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
        selected_building_var = StringVar()

        # Przesyłanie zmiennych StringVar do funkcji combobox
        selected_class_var = self.combobox(frame=frame, txt="CLASS", column_=0, row_=1, qry="SELECT name FROM Classes")
        selected_subject_var = self.combobox(frame=frame, txt="SUBJECTS", column_=0, row_=2, qry="SELECT name FROM Subjects")
        selected_teacher_var = self.combobox(frame=frame, txt="TEACHERS", column_=0, row_=3, qry="SELECT first_name, last_name FROM Users WHERE type != 'STUDENT'")
        selected_start_time_var = self.combobox(frame=frame, txt="LESSONS START TIMES", column_=0, row_=4, qry="SELECT start_time FROM LessonTimes")
        selected_end_time_var = self.combobox(frame=frame, txt="LESSONS END TIMES", column_=0, row_=5, qry="SELECT end_time FROM LessonTimes")
        selected_day_var = self.combobox(frame=frame, txt="DAYS", column_=0, row_=6, qry="SELECT day_name FROM Weekdays")
        selected_classroom_var = self.combobox(frame, "CLASSROOM", 0, 8, "SELECT room_number FROM Classrooms WHERE building = %s", -255, -255, 17, -255, "Arts Building")
        # selected_building_var = self.combobox(frame, "BUILDING", 0, 7, "SELECT building FROM Classrooms")
        

        Label(frame, text="BUILDING").grid(column=0, row=7, padx=10, pady=0)
        cmbox = ttk.Combobox(frame, width=17, textvariable=selected_building_var)

        # Funkcja do aktualizacji wartości zmiennej StringVar
        def on_combobox_select(event):
            nonlocal selected_classroom_var
            selected_building_var.set(cmbox.get())
            selected_classroom_var = self.combobox(frame, "CLASSROOM", 0, 8, "SELECT room_number FROM Classrooms WHERE building = %s", -255, -255, 17, -255, selected_building_var.get())

        cmbox.bind("<<ComboboxSelected>>", on_combobox_select)

        try:
            self.cursor.execute("SELECT building FROM Classrooms")
            names = self.cursor.fetchall()
            for name in names:
                value_to_add = ' '.join(str(item) for item in name) if len(name) > 1 else str(name[0])
                if value_to_add not in cmbox['values']:
                    cmbox['values'] = (*cmbox['values'], value_to_add)
        except mysql.connector.Error as err:
            messagebox.showinfo("ERROR", "ERROR COMBOBOX QUERY")

        cmbox.grid(column=1, row=7, pady=10)
        cmbox.current()
       

        def commitAdding(): 
            try:
                self.cursor.execute(
                    "INSERT INTO Lessons (subject, classroom, building, class_, day_of_week, teacher, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        selected_subject_var.get(),
                        selected_classroom_var.get(),
                        selected_building_var.get(),
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
                error_message = f"Error: {err}"
                print(error_message)
                messagebox.showinfo("ERROR", error_message)

        commitButton = Button(frame, text="commit", command=commitAdding, cursor="hand2")
        commitButton.grid(column=1, row=9, padx=10, pady=10)
        
    def removingLesson(self, frame):
        selected_class_var = StringVar()
        selected_subject_var = StringVar()
        selected_teacher_var = StringVar()
        selected_start_time_var = StringVar()
        selected_end_time_var = StringVar()
        selected_day_var = StringVar()
        selected_classroom_var = StringVar()
        selected_building_var = StringVar()

        # Przesyłanie zmiennych StringVar do funkcji combobox
        selected_class_var = self.combobox(frame, "CLASS", 0, 1, "SELECT class_ FROM Lessons")
        selected_subject_var = self.combobox(frame, "SUBJECTS", 0, 2, "SELECT subject FROM Lessons")
        selected_teacher_var = self.combobox(frame, "TEACHERS", 0, 3, "SELECT teacher FROM Lessons")
        selected_start_time_var = self.combobox(frame, "LESSONS START TIMES", 0, 4, "SELECT start_time FROM Lessons")
        selected_end_time_var = self.combobox(frame, "LESSONS END TIMES", 0, 5, "SELECT end_time FROM Lessons")
        selected_day_var = self.combobox(frame, "DAYS", 0, 6, "SELECT day_of_week FROM Lessons")
        selected_building_var = self.combobox(frame, "BUILDING", 0, 7, "SELECT building FROM Lessons")
        selected_classroom_var = self.combobox(frame, "CLASSROOM", 0, 8, "SELECT classroom FROM Lessons")

        def commitAdding():
            try:
                # Użycie metod .get() na zmiennych StringVar
                self.cursor.execute(
                    """
                    DELETE FROM Lessons WHERE 
                        subject = %s AND
                        classroom = %s AND
                        building = %s AND
                        class_ = %s AND
                        day_of_week = %s AND
                        teacher = %s AND
                        start_time = %s AND
                        end_time = %s
                    """,
                    (
                        selected_subject_var.get(),
                        selected_classroom_var.get(),
                        selected_building_var.get(),
                        selected_class_var.get(),
                        selected_day_var.get(),
                        selected_teacher_var.get(),
                        selected_start_time_var.get(),
                        selected_end_time_var.get()
                    )
                )
                self.conn.commit()
                messagebox.showinfo("SUCCESS", "Removed lesson")

            except mysql.connector.Error as err:
                messagebox.showinfo("ERROR", f"Could not remove lesson: {err}")

        commitButton = Button(frame, text="commit", command=commitAdding, cursor="hand2")
        commitButton.grid(column=1, row=9, padx=10, pady=10)

    def showAllLessons(self, frame):
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