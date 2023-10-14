import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
from tkinter import *
from tkinter import ttk
import sys
import datetime


def loginWindow():
    
    root.title("LOGIN WINDOW")
    root.geometry("400x200")

    email_label = Label(root, text='EMAIL: ')
    email_tb = Entry(root, width=30)
    email_label.grid(row=0, column=0)
    email_tb.grid(row=0, column=1)

    password_label = Label(root, text='PASSWORD: ')
    password_tb = Entry(root, show = "*", width=30)
    password_label.grid(row=1, column=0)
    password_tb.grid(row=1, column=1)

    #HELPFUL FUNCTION TO BUTTON LOGIN
    def login(email, password):
        global current_user, logged_in
        cursor.execute("SELECT * FROM Users WHERE email=%s", (email,))
        data = cursor.fetchone()
        
        if data and check_password_hash(data[3], password):
            print(f'Login {data[1]}')
            
            current_user = {
                "id: ": data[0],
                "first_name": data[1],
                "last_name": data[2],
                "type": data[4],
                "email": data[5],
                "class_": data[6]
            }
            #root.deiconify() #Unhides the root window
            root.destroy()
            mainApplication()


        else:
            print('Błędny login lub hasło')

    
    #BUTTON TO LOGIN
    confirm = Button(root, text='Login', command=lambda: login(email_tb.get(), password_tb.get()), cursor="hand2")  # using lambda to execute function utilizing the textbox entries
    confirm.grid(row=2, column=1, columnspan=1, pady=10, padx=10, ipadx=50)

    #HELPFUL FUNCTION TO CLOSE WINDOW
    def cancel():
        root.destroy() #Removes the hidden root window
        sys.exit() #Ends the script

    #CANCEL BTN
    cancel_btn = Button(root, text='Cancel', command=cancel, cursor="hand2")  # using lambda to execute function utilizing the textbox entries
    cancel_btn.grid(row=2, column=0, columnspan=1, pady=5, padx=5, ipadx=50)
 

    register_btn = Button(root, text="click here to register",
                        command = register,
                       bg=root.cget("bg"), fg='black',
                       padx=10, pady=5, relief=FLAT, cursor="hand2")
    register_btn.grid(row=3, column=0, columnspan=1, pady=5, padx=5, ipadx=25)
################################    REGISTER FUNC   #########################################################3
def register():
    top = Toplevel(root)
    top.geometry("500x500")
    top.title()

    first_name_label = Label(top, text='FIRST NAME: ')
    first_name_label_tb = Entry(top, width=30)
    first_name_label.grid(row=0, column=0)
    first_name_label_tb.grid(row=0, column=1)

    last_name_label= Label(top, text='LAST NAME: ')
    last_name_label_tb = Entry(top, width=30)
    last_name_label.grid(row=1, column=0)
    last_name_label_tb.grid(row=1, column=1)

    password_label1 = Label(top, text='PASSWORD: ')
    password_label_tb1 = Entry(top,show = "*", width=30)
    password_label1.grid(row=2, column=0)
    password_label_tb1.grid(row=2, column=1)
    
    password_label2 = Label(top, text=' CONFIRM PASSWORD: ')
    password_label_tb2 = Entry(top,show = "*", width=30)
    password_label2.grid(row=3, column=0)
    password_label_tb2.grid(row=3, column=1)

    type_label = Label(top, text='ACCOUNT TYPE(1-Student, 2-Teacher, 3-Principal): ')
    type_tb = Entry(top, width=30)
    type_label.grid(row=4, column=0)
    type_tb.grid(row=4, column=1)

    email_label = Label(top, text='EMIAL: ')
    email_tb = Entry(top, width=30)
    email_label.grid(row=5, column=0)
    email_tb.grid(row=5, column=1)

    class_label = Label(top, text='CLASS: ')
    class_tb = Entry(top, width=30)
    class_label.grid(row=6, column=0)
    class_tb.grid(row=6, column=1)

    def confirmRegisteration():
        if password_label_tb1.get() == password_label_tb2.get():
            info_str = "Registeration successfull"
            color = "green"
            hashed_password = generate_password_hash(password_label_tb1.get())
            cursor.execute("INSERT INTO Users (first_name, last_name, password, type, email, class_) VALUES (%s, %s, %s, %s, %s, %s)",
                        (first_name_label_tb.get(), last_name_label_tb.get(), hashed_password, type_tb.get(), email_tb.get(), class_tb.get()))
            conn.commit()
        else:
            info_str = "Registeration error"                                                                           
            color = "red"

        info = Label(top, text=info_str, fg=color)
        info.grid(row=8, column=0) 

    register_btn = Button(top, text="REGISTER",
                       command = confirmRegisteration,
                       bg=root.cget("bg"), fg='black', 
                       padx=10, pady=5)
    register_btn.grid(row=7, column=0, columnspan=2, pady=5, padx=5, ipadx=50)      

def exhibitionGrades():
    top = Toplevel(new_root)
    top.geometry("400x300")
    top.title("Add Grades")

    # Choosing student
    student_label = Label(top, text='Student ID:')
    student_entry = Entry(top, width=30)
    student_label.grid(row=0, column=0)
    student_entry.grid(row=0, column=1)

    # Choosing subject
    subject_label = Label(top, text='Subject ID:')
    subject_entry = Entry(top, width=30)
    subject_label.grid(row=1, column=0)
    subject_entry.grid(row=1, column=1)

    # Inputting grade
    grade_label = Label(top, text='Grade (1-6):')
    grade_entry = Entry(top, width=30)
    grade_label.grid(row=2, column=0)
    grade_entry.grid(row=2, column=1)

    def add_grade():
        student_id = student_entry.get()
        subject_id = subject_entry.get()
        grade = grade_entry.get()

        try:
            cursor.execute("INSERT INTO Grades (student_id, subject_id, grade) VALUES (%s, %s, %s)",
                           (student_id, subject_id, grade))
            conn.commit()
            info_str = "Grade added successfully!"
            color = "green"
        except mysql.connector.Error as err:
            info_str = f"Error: {err}"
            color = "red"
        
        info_label = Label(top, text=info_str, fg=color)
        info_label.grid(row=5, column=0, columnspan=2)

    add_btn = Button(top, text="Add Grade", command=add_grade, cursor="hand2")
    add_btn.grid(row=4, column=0, columnspan=2, pady=10, padx=10, ipadx=30)

def showScheduleOfDay(frame, day):
    print(f"typ: ", current_user["type"])
    if current_user["type"] == str("STUDENT"):
        label = Label(frame, text=day, fg='#97ffff', bg='black', font=('tagoma', 8, 'bold'))
        label.place(x=10, y = 10)
        
        label1 = Label(frame, text="FREE", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold'))
        label1.place(x=50, y = 20)

        print("You are Student")

        query = ("SELECT start_time, end_time, name, classroom, teacher, class_ "
                "FROM Lessons "
                "WHERE day_of_week = %s AND class_ = %s "
                "ORDER BY start_time")

        cursor.execute(query, (day, current_user["class_"]))
        lessons = cursor.fetchall()
        print(lessons)
        #if not lessons:


        for index, (start_time, end_time, name, classroom, teacher, class_) in enumerate(lessons):
            print(f"tatat\n {index} \n")
            label2 = Label(frame, text=f"start: {start_time} - end: {end_time}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=index, column=0)
            label3 =Label(frame, text=f"Name {name}", fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=index, column=1)
            label4 =Label(frame, text=str(classroom), fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=index, column=2)
            label5 =Label(frame, text=teacher, fg='#97ffff', bg='black', font=('tagoma', 8, 'bold')).grid(row=index, column=3)

    elif(current_user["type"] == str("TEACHER")):
        teacher_name = str(current_user["first_name"] + " " + current_user["last_name"])

        query = ("SELECT start_time, end_time, name, classroom, class_ "
                "FROM Lessons "
                "WHERE day_of_week = %s AND teacher = %s "
                "ORDER BY start_time")

        cursor.execute(query, (day, teacher_name))
        lessons = cursor.fetchall()

        for index, (start_time, end_time, name, classroom,teacher, class_) in enumerate(lessons):
            Label(frame, text=f"start: {start_time} - end: {end_time}", font=('tagoma', 3, 'bold')).grid(row=index, column=0)
            Label(frame, text=name, font=('tagoma', 3, 'bold')).grid(row=index, column=1)
            Label(frame, text=str(classroom), font=('tagoma', 3, 'bold')).grid(row=index, column=2)
            Label(frame, text=class_, font=('tagoma', 3, 'bold')).grid(row=index, column=3)
    else:
        print("ani nauczyciel aniuczen")
    

def mainApplication():
    global new_root
    new_root = Tk()
    new_root.geometry('600x600')
    notebook = ttk.Notebook(new_root)
    notebook.pack(pady=10, expand=True)

    frames = {
        "main": ttk.Frame(notebook, width=600, height=600),
        "account": ttk.Frame(notebook, width=600, height=600),
        "plan": ttk.Frame(notebook, width=600, height=600),
    }

    scheduleFrame = Frame(frames["main"], borderwidth=2, relief="groove", bg='green')
    scheduleFrame.place(x=10, y=50, width=400, height=200)

    canvas = Canvas(scheduleFrame, width=200, height=200, bg='green', bd=0, highlightthickness=0)
    #canvas.pack(fill='both', expand=True)

    for frame in frames.values():
        frame.pack(fill='both', expand=True)

    for k, v in frames.items():
        notebook.add(v, text=k)

    label = Label(frames["main"], text="Hello " + current_user["first_name"], fg='#97ffff', bg='black', font=('tagoma', 8, 'bold'))
    label.place(x=100, y = 10)
    showScheduleOfDay(scheduleFrame, datetime.datetime.now().strftime('%A'))

    day_label = Label(scheduleFrame, text=datetime.datetime.now().strftime('%A'), fg='#97ffff', bg='black', font=('tagoma', 8, 'bold'))
    canvas.create_window(100, 10, anchor='n', window=day_label)

    new_root.mainloop()

# ... Koniec definicji

#MYSQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="python"
)   
if conn.is_connected():
    print("Successfully connected")
current_user = None
logged_in = False
new_root = None

cursor = conn.cursor()
conn.commit() 

#TKINTER
root = Tk()
root.geometry('600x600')

loginWindow()

root.mainloop()

conn.commit()