# import sqlite3
# from tkinter import ttk
# import tkinter as tk
# DB_NAME = "sqlite_db.db"

# with sqlite3.connect(DB_NAME) as sqlite_conn:
#     sql_request = """CREATE TABLE IF NOT EXISTS categories (
#         category_name text PRIMETY KEY,
#         count integer
#     );"""
#     sqlite_conn.execute(sql_request)

# connect = sqlite3.connect('expenses.db')
# cursor = connect.cursor() # курсор позволяет отправлять sql запросы и получать данные
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS expenses (
#         LOGIN TEXT PRIMARY KEY,
#         PASSWORD TEXT,
#         date TEXT,
#         category TEXT,
#         amount REAL)
# ''')
# # cursor.execute('INSERT INTO data (Category_name, money_spent) VALUES')
# connect.commit()

# def add_expense():
#     date_str = date_entry.get()
#     category = category_entry.get()
#     amount_str = amount_entry.get()

#     try:
#         amount = float(amount_str)
#         #Basic input validation
#         if amount <= 0:
#             raise ValueError("Amount must be positive")
#         cursor.execute("INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)", (date_str, category, amount))
#         connect.commit()
#         print("Expenses были успешно добавлены!") #Success feedback - replace with GUI feedback
#         #clear input fields after adding
#         date_entry.delete(0, tk.END)
#         category_entry.delete(0, tk.END)
#         amount_entry.delete(0, tk.END)

#     except ValueError as e:
#         print(f"Error: {e}") #Error feedback - replace with GUI feedback
#     except sqlite3.Error as e:
#         print(f"Database error: {e}")

# root = tk.Tk()
# root.title("Expense Tracker")

# #Input fields
# date_label = ttk.Label(root, text="Date (YYYY-MM-DD):")
# date_label.pack(pady=5)
# date_entry = ttk.Entry(root)
# date_entry.pack(pady=5)

# category_label = ttk.Label(root, text="Category:")
# category_label.pack(pady=5)
# category_entry = ttk.Entry(root)
# category_entry.pack(pady=5)

# amount_label = ttk.Label(root, text="Amount:")
# amount_label.pack(pady=5)
# amount_entry = ttk.Entry(root)
# amount_entry.pack(pady=5)


# add_button = ttk.Button(root, text="Add Expense", command=add_expense)
# add_button.pack(pady=10)

# root.mainloop()
# connect.close()

from tkinter import *
import tkinter as tk
from tkinter import ttk
import sqlite3

def register_user():
    username = user.get()
    password = code.get()

    if not username or not password:
        error_label.config(text="Please enter both username and password.")
        return

    try:
        #Check if the username already exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            error_label.config(text="Username already exists. Please choose a different one.")
            return


        #Hash the password (crucial for security!)  See notes below.
        #Replace this with a proper hashing function

        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        success_label.config(text="Registration successful!")
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)

    except sqlite3.Error as e:
        error_label.config(text=f"Database error: {e}")

#Database setup
conn = sqlite3.connect('finance_helper1.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
''')
conn.commit()


root = tk.Tk()
root.title('Finance Helper Login')
root.geometry('925x500+300+200')
root.configure(bg="#fff")
root.resizable(False,False)

img = PhotoImage(file='login.png')
Label(root, image=img, bg='white').place(x=50,y=50)

frame=Frame(root,width=350,height=350,bg='white')
frame.place(x=480, y=70)

heading = Label(frame, text='Sign in', fg='#57a1f8', bg='white', font=('Microsoft YaHei UI Light',23,'bold'))
heading.place(x=100, y =5)

####--------------------------------------------

def on_enter(e):
    user.delete(0, 'end')
def on_leave(e):
    if user.get() == '':
        user.insert(0, 'Username')
user = Entry(frame, width=25, fg='black', border = 0, bg='white',font=('Microsoft YaHei UI Light',11))
user.place(x=30,y=80)
user.insert(0, 'Username')
user.bind("<FocusIn>", on_enter)
user.bind("<FocusOut>", on_leave)

Frame(frame,width=295,height=2,bg='black').place(x=25,y=107)

####------------------------------------------------------
def on_enter(e):
    code.delete(0, 'end')
def on_leave(e):
    if code.get() == '':
        code.insert(0, 'Password')

code = Entry(frame, width=25, fg='black', border=0, bg='white', font=('Microsoft YaHei UI Light',11))
code.place(x=30,y=150)
code.insert(0, 'Password')
code.bind("<FocusIn>", on_enter)
code.bind("<FocusOut>", on_leave)

Frame(frame,width=295,height=2,bg='black').place(x=25,y=177)
####-----------------------------------------------------------
Button(frame, width=39,pady=7,text='Sign in', bg= '#57a1f8', fg='white', border=0).place(x=35,y=204)
label=Label(frame, text="Don't have an account?",fg='black',bg = 'white', font=('Microsoft YaHei UI Light',9))
label.place(x=75,y=270)

sign_up = Button(frame, width=6, text='Sign up', border=0,bg='white',fg="#57a1f8")
sign_up.place(x=215,y=270)


# root.title("Finance Helper Registration")


# root.geometry('575x812')
# root.resizable(width=False, height=False)
# root.configure(background='black')


# register_label = tk.Label(root, text="Регистрация пользователя", font="Arial 18 bold", foreground='white', background='black')
# register_label.pack()

# username_label = tk.Label(root, text="Имя пользователя", font="Arial 11 bold", background='black', foreground='white')
# username_label.pack(padx=10,pady=50)

# username_entry = tk.Entry(root, background='black', foreground='white', font='Arial 12')
# username_entry.pack()



root.mainloop()
conn.close()
