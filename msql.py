import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import sys
import datetime
import random
from Users import User, Student, Teacher, HeadTeacher



STUDENT = "STUDENT"
TEACHER = "TEACHER"
HEADTEACHER = "HEADTEACHER"

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
        global user, frames, notebook
        cursor.execute("SELECT * FROM Users WHERE email=%s", (email,))
        data = cursor.fetchone()
        
        if data and check_password_hash(data[3], password):
            root.destroy()
            mainApplication(data)
        else:
            messagebox.showinfo("Failure", "Login Failure!")

    
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

def luckyNumber(luckyNumberFrame):
    lNumber = Label(luckyNumberFrame, text=f"Today lucky number is \n {random.randint(1, 30)}")
    lNumber.place(x=luckyNumberFrame.winfo_width()/2 - lNumber.winfo_width()/2, y=0)

def mainApplication(data):
    global new_root, notebook, frames, user, cursor, conn
    new_root = Tk()
    new_root.geometry('600x600')

    notebook = ttk.Notebook(new_root)
    notebook.pack(pady=10, expand=True)
    frames = {
        "main": Frame(notebook, width=600, height=600),
        "account": Frame(notebook, width=600, height=600),
        "plan": Frame(notebook, width=600, height=600),
    }

    for frame in frames.values():
        frame.pack(fill='both', expand=True)
    for k, v in frames.items():
        notebook.add(v, text=k)

    scheduleFrame = Frame(frames["main"], borderwidth=2, relief="groove", bg='lightgray')
    scheduleFrame.place(x=10, y=50, width=300, height=200)

    inforamtionFrame = Frame(frames["main"], borderwidth=2, relief="groove", bg='lightgray')
    inforamtionFrame.place(x=10, y=280, width=200, height=100)

    print(f"checking data type: {data[4]}")

    if data[4] == STUDENT:
        user = Student(cursor, frames, notebook, conn, data[0], data[1],data[2],data[4],data[5],data[6]) #cursor, id ,first_name, last_name, type, email, class_
    elif data[4] == TEACHER:
        user = Teacher(cursor, frames,notebook, conn, data[0], data[1],data[2],data[4],data[5]) #cursor, id ,first_name, last_name, type, email
    elif data[4] == HEADTEACHER:    
        user = HeadTeacher(cursor, frames,notebook, conn, data[0], data[1],data[2],data[4],data[5])
    else:
        print("ERRRORRRRRRRRRRRRRRRRRRR")
        return


    user.showScheduleOfDay(scheduleFrame, datetime.datetime.now().strftime('%A'))
    user.showAccountInformation(frames["account"])
    user.showScheduleOfWeek(frames["plan"])

    luckyNumber(frames["main"])

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

new_root = None
user = None
frames = None
notebook = None

cursor = conn.cursor()
conn.commit() 

#TKINTER
root = Tk()
root.geometry('600x600')

loginWindow()

root.mainloop()

#conn.commit()
cursor.close()
conn.close()