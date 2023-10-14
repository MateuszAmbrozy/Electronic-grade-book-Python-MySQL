from abc import ABC, abstractmethod
class User(ABC):
   
   #VARIABLES
    _curent_user = None #Dictionary

    #PRIVATE FUNCTIONS


   #CONSTRUCTOR AND DESTRUCTOR
    @abstractmethod
    def __init__(self):
        pass
    def __del__(self):
        print("delete User class")
    #PUBLIC FUNCTIONS
    @abstractmethod
    def showScheduleOfDay(self, frame, day):
        pass

class Student(User):
    #VARIABLES

    #PRIVATE FUNCTIONS
    def __init__(self, id, first_name, last_name, type, email, class_):
            #load info about student
            current_user = {
                "id: ": id,
                "first_name": first_name,
                "last_name": last_name,
                "type": type,
                "email": email,
                "class_": class_
            }
    #CONSTRUCTOR AND DESTRUCOR

    #PUBLIC FUNCTIONS
    def showScheduleOfDay(self, frame, day):
        print(f"typ: ", User::current_user["type"])
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
