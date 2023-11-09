
from tkinter import *
from PIL import Image, ImageTk

root = Tk()
root.title("LOGIN WINDOW")
root.geometry('925x500+300+200')     
root.configure(bg="#fff")
root.resizable(False, False)
img = Image.open('D:\All\PROGRAMING\Python Programs\mySQL+Python\login.png')
pythonImage = ImageTk.PhotoImage(img)
Label(root, image=pythonImage).pack()

root.mainloop()