import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime


def create_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Создание таблицы пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Таблица финансовых целей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0,
            creation_date TEXT NOT NULL,
            target_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Таблица напоминаний
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Таблица транзакций
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()


# === Окно входа и регистрации ===
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
        window.destroy()
    except sqlite3.IntegrityError:
        messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует!")
    finally:
        conn.close()


def login():
    login = login_entry.get()
    password = password_entry.get()

    if not login or not password:
        messagebox.showerror("Ошибка", "Заполните все поля!")
        return

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE login = ? AND password = ?", (login, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        messagebox.showinfo("Успех", "Вход выполнен успешно!")
        window.destroy()
        FinanceAssistantApp(user)
    else:
        messagebox.showerror("Ошибка", "Неверный логин или пароль!")


class FinanceAssistantApp(tk.Tk):
    def __init__(self, user):
        super().__init__()
        self.title("Финансовый помощник")
        self.geometry("800x600")
        self.user = user

        # Создание интерфейса
        self.create_main_interface()

    def create_main_interface(self):
        # Верхний фрейм с приветствием и значком пользователя
        top_frame = tk.Frame(self, bg="lightblue")
        top_frame.pack(fill=tk.X)

        user_icon = tk.Label(top_frame, text="👤", font=("Arial", 24), bg="lightblue")
        user_icon.pack(side=tk.LEFT, padx=10)

        user_label = tk.Label(top_frame, text=f"Добро пожаловать, {self.user[1]}!", font=("Arial", 16), bg="lightblue")
        user_label.pack(side=tk.LEFT)

        # Основной интерфейс с вкладками
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладки
        self.home_page = tk.Frame(notebook)
        self.transactions_page = tk.Frame(notebook)
        self.goals_page = tk.Frame(notebook)
        self.reminders_page = tk.Frame(notebook)

        notebook.add(self.home_page, text="Главная")
        notebook.add(self.transactions_page, text="Транзакции")
        notebook.add(self.goals_page, text="Цели")
        notebook.add(self.reminders_page, text="Напоминания")

        # Настройка вкладок
        self.setup_home_page()
        self.setup_transactions_page()
        self.setup_goals_page()
        self.setup_reminders_page()

    def setup_home_page(self):
        tk.Label(self.home_page, text="Общая информация", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.home_page, text="Здесь отображаются баланс и графики.", font=("Arial", 12)).pack()

        # Кнопки для внесения новых данных
        tk.Button(self.home_page, text="Добавить транзакцию", command=self.add_transaction_window).pack(pady=10)

    def setup_transactions_page(self):
        tk.Label(self.transactions_page, text="История транзакций", font=("Arial", 16)).pack(pady=10)
        self.transactions_tree = ttk.Treeview(self.transactions_page, columns=("category", "amount", "date"), show="headings")
        self.transactions_tree.heading("category", text="Категория")
        self.transactions_tree.heading("amount", text="Сумма")
        self.transactions_tree.heading("date", text="Дата")
        self.transactions_tree.pack(fill=tk.BOTH, expand=True)
        self.update_transactions_list()

    def update_transactions_list(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, amount, date FROM transactions WHERE user_id = ?
        """, (self.user[0],))
        transactions = cursor.fetchall()
        conn.close()

        for row in self.transactions_tree.get_children():
            self.transactions_tree.delete(row)

        for transaction in transactions:
            self.transactions_tree.insert("", tk.END, values=transaction)

    def add_transaction_window(self):
        add_window = tk.Toplevel(self)
        add_window.title("Добавить транзакцию")
        add_window.geometry("300x300")

        tk.Label(add_window, text="Категория:").pack(pady=5)
        category_entry = tk.Entry(add_window)
        category_entry.pack(pady=5)

        tk.Label(add_window, text="Сумма:").pack(pady=5)
        amount_entry = tk.Entry(add_window)
        amount_entry.pack(pady=5)

        def save_transaction():
            category = category_entry.get()
            amount = amount_entry.get()

            if not category or not amount:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return

            try:
                amount = float(amount)
            except ValueError:
                messagebox.showerror("Ошибка", "Сумма должна быть числом!")
                return

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (user_id, category, amount, date) VALUES (?, ?, ?, ?)
            """, (self.user[0], category, amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            conn.close()

            messagebox.showinfo("Успех", "Транзакция добавлена!")
            add_window.destroy()
            self.update_transactions_list()

        tk.Button(add_window, text="Сохранить", command=save_transaction).pack(pady=10)

    def setup_goals_page(self):
        tk.Label(self.goals_page, text="Финансовые цели", font=("Arial", 16)).pack(pady=10)

        self.goals_frame = tk.Frame(self.goals_page)
        self.goals_frame.pack(fill=tk.BOTH, expand=True)
        self.update_goals_list()

        tk.Button(self.goals_page, text="Добавить новую цель", command=self.add_goal_window).pack(pady=10)

    def setup_reminders_page(self):
        tk.Label(self.reminders_page, text="Напоминания", font=("Arial", 16)).pack(pady=10)

        self.reminders_list = tk.Listbox(self.reminders_page)
        self.reminders_list.pack(fill=tk.BOTH, expand=True)

        tk.Button(self.reminders_page, text="Добавить напоминание", command=self.add_reminder_window).pack(pady=10)

    def add_reminder_window(self):
        add_window = tk.Toplevel(self)
        add_window.title("Добавить напоминание")
        add_window.geometry("300x200")

        tk.Label(add_window, text="Название:").pack(pady=5)
        title_entry = tk.Entry(add_window)
        title_entry.pack(pady=5)

        tk.Label(add_window, text="Дата (ГГГГ-ММ-ДД):").pack(pady=5)
        date_entry = tk.Entry(add_window)
        date_entry.pack(pady=5)

        tk.Label(add_window, text="Время (ЧЧ:ММ):").pack(pady=5)
        time_entry = tk.Entry(add_window)
        time_entry.pack(pady=5)

        def save_reminder():
            title = title_entry.get()
            date = date_entry.get()
            time = time_entry.get()

            if not title or not date or not time:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reminders (user_id, title, date, time) VALUES (?, ?, ?, ?)
            """, (self.user[0], title, date, time))
            conn.commit()
            conn.close()

            messagebox.showinfo("Успех", "Напоминание добавлено!")
            add_window.destroy()

        tk.Button(add_window, text="Сохранить", command=save_reminder).pack(pady=10)


def login():
    login = login_entry.get()
    password = password_entry.get()

    if not login or not password:
        messagebox.showerror("Ошибка", "Заполните все поля!")
        return

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE login = ? AND password = ?", (login, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        messagebox.showinfo("Успех", "Вход выполнен успешно!")
        window.destroy()
        app = FinanceAssistantApp(user)
        app.mainloop()
    else:
        messagebox.showerror("Ошибка", "Неверный логин или пароль!")


create_db()

window = tk.Tk()
window.title("Вход/Регистрация")

login_label = tk.Label(window, text="Логин:")
login_label.grid(row=0, column=0, padx=5, pady=5)
login_entry = tk.Entry(window)
login_entry.grid(row=0, column=1, padx=5, pady=5)

password_label = tk.Label(window, text="Пароль:")
password_label.grid(row=1, column=0, padx=5, pady=5)
password_entry = tk.Entry(window, show="*")
password_entry.grid(row=1, column=1, padx=5, pady=5)

confirm_password_label = tk.Label(window, text="Подтверждение пароля:")
confirm_password_label.grid(row=2, column=0, padx=5, pady=5)
confirm_password_entry = tk.Entry(window, show="*")
confirm_password_entry.grid(row=2, column=1, padx=5, pady=5)

login_button = tk.Button(window, text="Вход", command=login)
login_button.grid(row=3, column=0, padx=5, pady=10)

register_button = tk.Button(window, text="Регистрация", command=register)
register_button.grid(row=3, column=1, padx=5, pady=10)

window.mainloop()