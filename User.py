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
