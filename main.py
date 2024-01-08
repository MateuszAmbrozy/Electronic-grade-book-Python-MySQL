import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
from tkinter import *
import os
import sys
#from Users import Student, Teacher, HeadTeacher
from Student import Student
from Teacher import Teacher
from HeadTeacher import HeadTeacher
from PIL import Image, ImageTk
from tkinter import messagebox
import json


STUDENT = "STUDENT"
TEACHER = "TEACHER"
HEADTEACHER = "HEADTEACHER"

def loginWindow():
    frame=Frame(loginingRoot, width=350, height=350, bg='white')
    frame.place(x=480, y=70)
    heading_label= Label(frame, text='Sign in', fg='#57a1f8', bg='white', font=('Microsoft YaHei UI Light', 23, 'bold'))
    heading_label.place(x=100, y=5)
    ###########################################################################################################
    def on_enter(event):
        user.delete(0, 'end')
    def on_leave(event):
        name=user.get()
        if name == '':
            user.insert(0, 'Username')

    user = Entry(frame, width=27, fg='black', border=0, bg='white', font=('Microsoft YaHei UI Light', 11))
    user.place(x=30, y=80)
    user.insert(0, 'Username')
    user.bind('<FocusIn>', on_enter)
    user.bind('<FocusOut>', on_leave)

    Frame(frame, width=295, height = 2, bg='black').place(x=27, y=107)
    ###########################################################################################################
    def on_enter(event):
        code.delete(0, 'end')
    def on_leave(event):
        name=code.get() 
        if name == '':
            code.insert(0, 'Password')

    code = Entry(frame, width=27, fg='black', border=0, bg='white', show="*", font=('Microsoft YaHei UI Light', 11))
    code.place(x=30, y=150)
    code.insert(0, 'Password')
    code.bind('<FocusIn>', on_enter)
    code.bind('<FocusOut>', on_leave)
    
    Frame(frame, width=295, height = 2, bg='black').place(x=25, y=177)
    ##########################################################################################################

    def login(email, password):
        global user
        try:
            cursor.execute("SELECT * FROM Users WHERE email=%s", (email,))
            data = cursor.fetchone()
            
            if data and check_password_hash(data[3], password):
                loginingRoot.destroy()
                mainApplication(data)
            else:
                messagebox.showinfo("Failure", "Login Failure!")
        except mysql.connector.Error as err:
            messagebox.showinfo("ERROR", "ERROR COMBOBOX QUERY")
                        ##|##
    Button(frame, width = 39, pady=7, text='Sign in', command = lambda: login(user.get(), code.get()), cursor = "hand2", bg='#57a1f8', fg='white', border=0).place(x=25, y=204)
 
    label=Label(frame, text = "Dont't have an account?", fg='black', bg='white', font=('Microsoft YaHei UI Light', 9))
    label.place(x=75, y=270)

    sign_up= Button(frame, width=6, text='Sign up', command = register, border=0, bg='white', cursor='hand2', fg='#57a1f8')
    sign_up.place(x=215, y=270)
    # register_btn = Button(loginingRoot, text="click here to register",
    #                     command = register,
    #                    bg=loginingRoot.cget("bg"), fg='black',
    #                    padx=10, pady=5, relief=FLAT, cursor="hand2")
    # register_btn.grid(row=3, column=0, columnspan=1, pady=5, padx=5, ipadx=25)
################################    REGISTER FUNC   #########################################################3
def register():
    top = Toplevel(loginingRoot)
    top.title("Register")

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
                       bg=loginingRoot.cget("bg"), fg='black', 
                       padx=10, pady=5)
    register_btn.grid(row=7, column=0, columnspan=2, pady=5, padx=5, ipadx=50)      

def mainApplication(data):
    global root, user, cursor, conn
    root = Tk()
    root.geometry('600x600')
    root.resizable(False,False)

    if data[4] == STUDENT:
        user = Student(root, cursor, conn, data[0], data[1],data[2], data[3], data[4],data[5],data[6]) #cursor, id ,first_name, last_name, type, email, class_
    elif data[4] == TEACHER:
        user = Teacher(root, cursor, conn, data[0], data[1],data[2],data[3],data[4],data[5]) #cursor, id ,first_name, last_name, type, email
    elif data[4] == HEADTEACHER:    
        user = HeadTeacher(root, cursor, conn, data[0], data[1],data[2],data[3],data[4],data[5])
    else:
        print("EROR")
        return

    root.mainloop()

# ... Koniec definicji
if __name__ == "__main__":
    #MYSQL
    try:
        file = open('config.json', 'r')
        configData = json.load(file)
        conn = mysql.connector.connect(username=configData['user'], password=configData['pass'], host=configData['host'], database=configData['database'], port = configData['port'], autocommit = True)
        
    except mysql.connector.Error as err:
        print(f"Could not open database: {err}")
        sys.exit()

    
    if conn.is_connected():
        print("Successfully connected")

    root = None
    user = None

    cursor = conn.cursor()
    conn.commit() 

    # with open("script_to_create_db.sql", "r") as file:
    #     sql_script = file.read()
    #     cursor.execute(sql_script)

    #TKINTER
    loginingRoot = Tk()
    loginingRoot.title("LOGIN WINDOW")
    loginingRoot.geometry('925x500+300+200')     
    loginingRoot.configure(bg="#fff")
    loginingRoot.resizable(False, False)
    loginWindow()
    def imgShow(path):
        img = Image.open(path)
        PhotoImage = ImageTk.PhotoImage(img)
        return PhotoImage

    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Images\\login.png')
    pic = imgShow(file_path)
    Label(loginingRoot, image=pic).place(x=50, y=50)
    loginingRoot.mainloop()

    #conn.commit()
    cursor.close()
    conn.close()    