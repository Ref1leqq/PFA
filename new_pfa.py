import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

def create_db_and_tables():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

def register():
    login = login_entry.get()
    password = password_entry.get()
    confirm_password = confirm_password_entry.get()

    if not login or not password or not confirm_password:
        messagebox.showerror("Ошибка", "Заполните все поля!")
        return

    if password != confirm_password:
        messagebox.showerror("Ошибка", "Пароли не совпадают!")
        return

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (login, password) VALUES (?, ?)", (login, password))
        conn.commit()
        messagebox.showinfo("Успех", "Регистрация прошла успешно!")
        login_window.destroy()
    except sqlite3.IntegrityError:
        messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует!")
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка", f"Ошибка базы данных: {e}")
    finally:
        conn.close()

def login(login_window):
    login = login_entry.get()
    password = password_entry.get()

    if not login or not password:
        messagebox.showerror("Ошибка", "Заполните все поля!")
        return

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE login = ? AND password = ?", (login, password))
        user = cursor.fetchone()
        if user:
            show_main_window(login, login_window)
            login_window.destroy()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка", f"Ошибка базы данных: {e}")
    finally:
        conn.close()

def show_main_window(current_user, login_window):
    main_window = tk.Toplevel(login_window)
    main_window.title("Главное окно")

    def update_balance():
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(amount) FROM transactions")
            balance = cursor.fetchone()[0] or 0
            balance_label.config(text=f"Баланс: {balance}")
            conn.close()
        except sqlite3.Error as e:
            print(f"Ошибка получения баланса: {e}")
            balance_label.config(text="Ошибка баланса")

    def plot_transactions(start_date, end_date):
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT date, amount FROM transactions WHERE date BETWEEN ? AND ?", (start_date, end_date))
            data = cursor.fetchall()
            conn.close()

            if not data:
                messagebox.showinfo("Информация", "Нет данных для указанного периода.")
                return

            dates = [datetime.datetime.strptime(row[0], '%Y-%m-%d').date() for row in data]
            amounts = [row[1] for row in data]

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(dates, amounts)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            plt.gcf().autofmt_xdate()
            plt.xlabel('Дата')
            plt.ylabel('Сумма')
            plt.title('График трат')
            plt.grid(True)
            plt.show()
        except sqlite3.Error as e:
            print(f"Ошибка построения графика: {e}")
            messagebox.showerror("Ошибка", f"Ошибка базы данных: {e}")

    def add_transaction():
        try:
            date_str = date_entry.get()
            amount_str = amount_entry.get()
            description = description_entry.get()

            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            amount = float(amount_str)

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO transactions (date, amount, description) VALUES (?, ?, ?)", (date_obj.strftime('%Y-%m-%d'), amount, description))
            conn.commit()
            messagebox.showinfo("Успех", "Транзакция добавлена!")
            update_balance()
            conn.close()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат даты или суммы.")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка базы данных: {e}")

    balance_label = ttk.Label(main_window, text="Загрузка...")
    balance_label.pack(pady=10)
    update_balance()

    plot_button = ttk.Button(main_window, text="Построить график (2023-01-01 - сегодня)",
                             command=lambda: plot_transactions(datetime.date(2023, 1, 1), datetime.date.today()))
    plot_button.pack(pady=5)

    # Элементы для добавления транзакций
    date_label = ttk.Label(main_window, text="Дата (YYYY-MM-DD):")
    date_label.pack(pady=2)
    date_entry = ttk.Entry(main_window)
    date_entry.pack(pady=2)

    amount_label = ttk.Label(main_window, text="Сумма:")
    amount_label.pack(pady=2)
    amount_entry = ttk.Entry(main_window)
    amount_entry.pack(pady=2)

    description_label = ttk.Label(main_window, text="Описание:")
    description_label.pack(pady=2)
    description_entry = ttk.Entry(main_window)
    description_entry.pack(pady=2)

    add_transaction_button = ttk.Button(main_window, text="Добавить транзакцию", command=add_transaction)
    add_transaction_button.pack(pady=10)

    main_window.mainloop()


create_db_and_tables()
login_window = tk.Tk()
login_window.title("Вход/Регистрация")

login_label = ttk.Label(login_window, text="Логин:")
login_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
login_entry = ttk.Entry(login_window)
login_entry.grid(row=0, column=1, padx=5, pady=5)

password_label = ttk.Label(login_window, text="Пароль:")
password_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
password_entry = ttk.Entry(login_window, show="*")
password_entry.grid(row=1, column=1, padx=5, pady=5)

login_button = ttk.Button(login_window, text="Вход", command=lambda: login(login_window))
login_button.grid(row=2, column=1, padx=5, pady=10)

register_button = ttk.Button(login_window, text="Регистрация", command=register)
register_button.grid(row=2, column=0, padx=5, pady=10)

login_window.mainloop()
