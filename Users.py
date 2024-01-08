from abc import ABC, abstractmethod
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import datetime
import random
import os
from PIL import Image, ImageTk

class User(ABC):
   
   #CONSTRUCTOR 
    def __init__(self, root, cursor, conn, id, first_name, last_name, password, type, email, class_):
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True)
        self.frames = {
        "Main": Frame(self.notebook, width=600, height=600),
        "Account": Frame(self.notebook, width=600, height=600),
        "Schedule": Frame(self.notebook, width=600, height=600),
        "Messages": Frame(self.notebook, width=600, height=600),
        "Grades": Frame(self.notebook, width=600, height=600)
        }
        self._current_user = {
            "id": id,
            "first_name": first_name,
            "last_name": last_name,
            "password" : password,
            "type": type,
            "email": email,
            "class_": class_
        }

        for k, v in self.frames.items():
            v.pack(fill='both', expand=True)
            self.notebook.add(v, text=k)

        Frame(self.frames["Main"], width=self.frames["Main"].winfo_reqwidth(), height = 2, bg='black').place(x=0, y=50)
        sch_lb = Label(self.frames["Main"], text="Your schedule for today", fg='black', bg='grey', font=('Microsoft YaHei UI Light', 12, 'bold'))
        sch_lb.place(x=55, y=55)

        welcome_label = Label(
            self.frames["Main"],
            text=f" Welcome {self.getLastName()} {self.getLastName()}",
            font=("Helvetica", 16),  # Rozmiar i czcionka
            bg= "#4CAF50",    # Kolor tła
            fg="white"           # Kolor tekstu
        )
        welcome_label.place(x=self.frames["Main"].winfo_reqwidth()/2 - welcome_label.winfo_reqwidth()/2, y = 10)

        self.scheduleFrame = Frame(self.frames["Main"], borderwidth=2, relief="groove", bg='lightgray')
        self.scheduleFrame.place(x=30, y=80, width=300, height=200)

        inf_lb = Label(self.frames["Main"], text="Your last three messages", fg='black', bg='grey', font=('Microsoft YaHei UI Light', 12, 'bold'))
        inf_lb.place(x=55, y=300)

        inforamtionFrame = Frame(self.frames["Main"], borderwidth=2, relief="groove", bg='lightgray')
        inforamtionFrame.place(x=30, y=320, width=300, height=100)

        lNumber = Label(self.frames["Main"], text=f"Today lucky number is \n {random.randint(1, 30)}",
                     fg='yellow', bg='grey', font=('Microsoft YaHei UI Light', 12, 'bold'))
        lNumber.place(x=self.frames["Main"].winfo_reqwidth()/2 + 30, y=200)

        self.cursor = cursor
        self.conn = conn

        self.showScheduleOfDay(self.scheduleFrame, datetime.datetime.now().strftime('%A'))
        self.showAccountInformation(self.frames["Account"])
        self.showScheduleOfWeek(self.frames["Schedule"])
        self.showLast3Messages(inforamtionFrame)
        self.messaagesManager(self.frames["Messages"])

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

        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Images\\user.jpg')
        img = Image.open(file_path)
        img = img.resize((50, 50))
        self.PhotoImage = ImageTk.PhotoImage(img)
        Label(frame, image=self.PhotoImage).grid(row=1, column=0, padx=5, pady=5)

        Label(frame, text=f"NAME: {self.getFirstName()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=1, column=1, padx=5, pady=5)
        Label(frame, text=f"SURNAME: {self.getLastName()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=2, column=1, padx=5, pady=5)
        Label(frame, text=f"ID: {self.getId()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=1, column=5, padx=5, pady=5)
        Label(frame, text=f"USER TYPE: {self.getType()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=2, column=5, padx=5, pady=5)
        Label(frame, text=f"E-MAIL: {self.getEmail()}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=3, column=5, padx=5, pady=5)


        
        self.changePassword(frame)
        
    def combobox(self, frame, txt, column_, row_, qry, x=-255, y=-255, cmbox_width = 17, text_width = -255, *conditionals):
        if text_width != -255:
            l1=Label(frame, text=txt, width = text_width)
        else:
            l1=Label(frame, text=txt)

        if x!=-255 and y != 255:
            l1.place(x=x, y=y)
        else:
            l1.grid(column=column_, row=row_, padx=10, pady=0)
        selected_variable = StringVar()
        cmbox = ttk.Combobox(frame, width=cmbox_width, textvariable=selected_variable)

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

        if x!=-255 and y != 255:
            cmbox.place(x=x + l1.winfo_reqwidth(), y = y)
        else:
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
        WHERE A.subject = %s
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

    def writeMessage(self, frame):
        top = Toplevel(frame)

        # Tworzenie etykiet i pól tekstowych dla danych wiadomości
        receiver_email_label = Label(top, text="Email Odbiorcy:")
        receiver_email_label.pack()
        receiver_email_entry = Entry(top)
        receiver_email_entry.pack()

        topic_label = Label(top, text="Temat:")
        topic_label.pack()
        topic_entry = Entry(top)
        topic_entry.pack()

        message_text_label = Label(top, text="Treść Wiadomości:")
        message_text_label.pack()
        message_text_entry = Text(top, height=5, width=30)
        message_text_entry.pack()

        # Przycisk do wysyłania wiadomości
        def send():
            try:
                sender_email = self.getEmail()
                receiver_email = receiver_email_entry.get()
                topic = topic_entry.get()
                message_text = message_text_entry.get("1.0", "end-1c")  # Pobieramy treść wiadomości z pola tekstowego
                sent_date = datetime.datetime.now()
                insert_query = "INSERT INTO Messages (senderEmail, receiverEmail, topic, messageText, sendDate) VALUES (%s, %s, %s, %s, %s)"
                data = (sender_email, receiver_email, topic, message_text, sent_date)
                self.cursor.execute(insert_query, data)

                # Zatwierdzamy zmiany w bazie danych
                self.conn.commit()

                # Czyszczenie pól formularza
                receiver_email_entry.delete(0, "end")
                topic_entry.delete(0, "end")
                message_text_entry.delete("1.0", "end")

                # Dodaj kod obsługi potwierdzenia zapisu
                # Tutaj można dodać komunikat potwierdzający zapis wiadomości

            except mysql.connector.Error as e:
                print(f"Błąd podczas łączenia z bazą danych: {e}")

        send_button = Button(top, text="SEND", command=send, cursor="hand2")
        send_button.pack()

    def readMessage(self, frame):
        top = Toplevel(frame)
        top.title("Received Messages")

        # Pobierz wszystkie wiadomości użytkownika posortowane od najstarszej do najnowszej
        query = "SELECT id, senderEmail, topic, sendDate, messageText FROM Messages WHERE receiverEmail = %s ORDER BY sendDate ASC"
        data = (self.getEmail(),)

        try:
            self.cursor.execute(query, data)
            messages = self.cursor.fetchall()

            # Stwórz listę przycisków do wyświetlania wiadomości
            message_buttons = []

            canvas = Canvas(top)
            canvas.pack(side=LEFT, fill='both', expand=True)

            scrollbar = Scrollbar(top, command=canvas.yview)
            scrollbar.pack(side=RIGHT, fill=Y)

            canvas.configure(yscrollcommand=scrollbar.set)

            second_frame = Frame(canvas)
            canvas.create_window((0, 0), window=second_frame, anchor='nw')

            for message in messages:
                message_id, sender_email, topic, sent_date, message_text = message
                message_info = f"From: {sender_email}\nSubject: {topic}\nDate: {sent_date}"

                # Użyj funkcji lambda do przekazania argumentów do funkcji showMessageDetails
                message_button = Button(second_frame, text=message_info, cursor="hand2", command=lambda msg=message_text, sender=sender_email, subj=topic, date=sent_date: self.showMessageDetails(message_id, sender, subj, date, msg))
                message_button.pack(fill='x', padx=10, pady=5, expand=True)
                message_buttons.append(message_button)
            second_frame.grid_columnconfigure(0, weight=1)


            second_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))

        except mysql.connector.Error as e:
            print(f"Błąd podczas pobierania wiadomości: {e}")
            
    def showMessageDetails(self, message_id, sender_email, topic, sent_date, message_text):
        top = Toplevel()
        top.title("Message Details")

        details_text = f"From: {sender_email}\nSubject: {topic}\nDate: {sent_date}\n\nMessage:\n{message_text}"
        label = Label(top, text=details_text)
        label.pack(padx=10, pady=10)

    def messaagesManager(self, frame):
        write_message_btn = Button(frame, text="WRITE", command=lambda: self.writeMessage(frame),
                                    cursor="hand2", width=30, height=5)
        write_message_btn.place(x=frame.winfo_reqwidth()/2 - write_message_btn.winfo_reqwidth()/2, y=50)

        read_message_btn = Button(frame, text="READ", command=lambda: self.readMessage(frame),
                                    cursor="hand2", width=30, height=5)
        read_message_btn.place(x=frame.winfo_reqwidth()/2 - read_message_btn.winfo_reqwidth()/2, y=200)

    def changePassword(self, frame):

        old_password_label = Label(frame, text='Enter your password')
        old_password_entry = Entry(frame, show = "*", width=30)
        old_password_label.grid(row=5, column=1, padx=5, pady=5)
        old_password_entry.grid(row=5, column=2, padx=5, pady=5)

        new_password_label = Label(frame, text='Enter new password')
        new_password_entry = Entry(frame, show = "*", width=30)
        new_password_label.grid(row=6, column=1, padx=5, pady=5)
        new_password_entry.grid(row=6, column=2, padx=5, pady=5)

        commit_password_label = Label(frame, text='Confirm new password')
        commit_password_entry = Entry(frame, show = "*", width=30)
        commit_password_label.grid(row=7, column=1, padx=5, pady=5)
        commit_password_entry.grid(row=7, column=2, padx=5, pady=5)
        def update_password():
            # Hash the password
            print(new_password_entry.get(), commit_password_entry.get(), old_password_entry.get())
            if new_password_entry.get() == commit_password_entry.get() and check_password_hash(self._current_user["password"], old_password_entry.get()) :
                hashed_password = generate_password_hash(new_password_entry.get())
                try:
                    update_query = """
                    UPDATE Users SET password = %s WHERE id = %s
                    """
                    self.cursor.execute(update_query, (hashed_password, self.getId()))
                    self.conn.commit()
                    print(f"Password for User {self.getId()} has been updated!")
                    messagebox.showinfo("Success", "Password has been updated successfully!")
                except mysql.connector.Error as err:
                    messagebox.showerror("Database Error", f"Error updating password: {err}")

        update_button = Button(frame, text='Update Password',cursor="hand2", command=update_password)
        update_button.grid(row=8, column=1, padx=5, pady=5)

    def showLast3Messages(self, frame):
                # Pobierz wszystkie wiadomości użytkownika posortowane od najstarszej do najnowszej
        query = "SELECT id, senderEmail, topic, sendDate, messageText FROM Messages WHERE receiverEmail = %s ORDER BY sendDate ASC LIMIT 3"
        data = (self.getEmail(),)

        try:
            self.cursor.execute(query, data)
            messages = self.cursor.fetchall()

            # Stwórz listę przycisków do wyświetlania wiadomości
            message_buttons = []

            canvas = Canvas(frame)
            canvas.pack(side=LEFT, fill='both', expand=True)

            scrollbar = Scrollbar(frame, command=canvas.yview)
            scrollbar.pack(side=RIGHT, fill=Y)

            canvas.configure(yscrollcommand=scrollbar.set)

            second_frame = Frame(canvas)
            canvas.create_window((0, 0), window=second_frame, anchor='nw')

            for message in messages:
                message_id, sender_email, topic, sent_date, message_text = message
                message_info = f"From: {sender_email}\tSubject: {topic}\tDate: {sent_date}"

                # Użyj funkcji lambda do przekazania argumentów do funkcji showMessageDetails
                message_button = Button(second_frame, text=message_info, cursor="hand2",
                                         command=lambda msg=message_text, sender=sender_email, subj=topic,
                                         date=sent_date: self.showMessageDetails(message_id, sender, subj, date, msg))
                message_button.pack(fill='x', padx=10, pady=5, expand=True)
                message_buttons.append(message_button)
            second_frame.grid_columnconfigure(0, weight=1)


            second_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))

        except mysql.connector.Error as e:
            print(f"Błąd podczas pobierania wiadomości: {e}")
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

#----------------------------------TEACHER CLASS----------------------------------
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
                                current_date = datetime.datetime.now().strftime('%Y-%m-%d')
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
                                (row[0], row[3], self.teacher, selected_subject, datetime.now.strftime("%d/%m/%Y %H:%M:%S"), row[4]))
                                self.conn.commit()
                            except Exception as e:
                                messagebox.showinfo("Error", f"An error occurred: {str(e)}")
                            else:
                                print(row[0], row[3], self.teacher, selected_subject, datetime.now.strftime("%d/%m/%Y %H:%M:%S"), row[4])
                        
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
        
#----------------------------------TEACHER CLASS----------------------------------
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
                top = Toplevel(frame)
                self.cursor.execute("SELECT id, subject, classroom, class_, day_of_week, teacher, start_time, end_time from Lessons")
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