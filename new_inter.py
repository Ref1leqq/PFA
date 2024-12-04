import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# === Создание базы данных ===
def create_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Таблица транзакций
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            type TEXT NOT NULL,  -- "income" или "expense"
            date TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Таблица напоминаний
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            reminder_date TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
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
        open_main_window(user)
    else:
        messagebox.showerror("Ошибка", "Неверный логин или пароль!")


# === Основной интерфейс ===
def open_main_window(user):
    main_window = tk.Tk()
    main_window.title("Финансовый помощник")
    main_window.geometry("800x600")

    user_id = user[0]

    # Баланс
    def calculate_balance():
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(amount) FROM transactions
            WHERE user_id = ? AND type = 'income'
        """, (user_id,))
        income = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT SUM(amount) FROM transactions
            WHERE user_id = ? AND type = 'expense'
        """, (user_id,))
        expenses = cursor.fetchone()[0] or 0

        conn.close()
        return income - expenses

    balance = calculate_balance()

    tk.Label(main_window, text=f"Добро пожаловать, {user[1]}!", font=("Arial", 16)).pack(pady=10)
    tk.Label(main_window, text=f"Текущий баланс: {balance:.2f} руб.", font=("Arial", 14)).pack(pady=10)

    # График расходов
    #def plot_expenses():
    #    conn = sqlite3.connect('users.db')
    #    cursor = conn.cursor()
    #    cursor.execute("""
    #        SELECT category, SUM(amount) FROM transactions
    #        WHERE user_id = ? AND type = 'expense'
    #        GROUP BY category
    #    """, (user_id,))
    #    data = cursor.fetchall()
    #    conn.close()

    #    categories = [row[0] for row in data]
    #    amounts = [row[1] for row in data]

    #    fig, ax = plt.subplots()
    #    ax.bar(categories, amounts, color='skyblue')
    #    ax.set_title("Расходы по категориям")
    #    ax.set_ylabel("Сумма, руб.")
    #    ax.set_xlabel("Категории")

    #    canvas = FigureCanvasTkAgg(fig, main_window)
    #    canvas.get_tk_widget().pack()

    #plot_expenses()

    # Кнопки
    def add_transaction():
        def save_transaction():
            amount = float(amount_entry.get())
            category = category_entry.get()
            trans_type = type_var.get()

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (user_id, amount, category, type, date)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, amount, category, trans_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()

            messagebox.showinfo("Успех", "Транзакция добавлена!")
            trans_window.destroy()

        trans_window = tk.Toplevel(main_window)
        trans_window.title("Добавить транзакцию")

        tk.Label(trans_window, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        amount_entry = tk.Entry(trans_window)
        amount_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(trans_window, text="Категория:").grid(row=1, column=0, padx=5, pady=5)
        category_entry = tk.Entry(trans_window)
        category_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(trans_window, text="Тип:").grid(row=2, column=0, padx=5, pady=5)
        type_var = tk.StringVar(value="expense")
        tk.Radiobutton(trans_window, text="Расход", variable=type_var, value="expense").grid(row=2, column=1)
        tk.Radiobutton(trans_window, text="Доход", variable=type_var, value="income").grid(row=2, column=2)

        tk.Button(trans_window, text="Сохранить", command=save_transaction).grid(row=3, column=0, columnspan=2, pady=10)

    tk.Button(main_window, text="Добавить транзакцию", command=add_transaction).pack(pady=10)

# === Основной интерфейс ===
class MainApp(tk.Tk):
    def __init__(self, user):
        super().__init__()
        self.title("Финансовый помощник")
        self.geometry("900x700")
        self.user = user

        # Создание вкладок
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Главная страница
        self.main_page = tk.Frame(self.notebook)
        self.notebook.add(self.main_page, text="Главная")
        self.setup_main_page()

        # Вкладка "Расходы"
        self.expenses_page = tk.Frame(self.notebook)
        self.notebook.add(self.expenses_page, text="Расходы")
        self.setup_expenses_page()

        # Вкладка "Транзакции"
        self.transactions_page = tk.Frame(self.notebook)
        self.notebook.add(self.transactions_page, text="Транзакции")
        self.setup_transactions_page()

        # Вкладка "Напоминания"
        self.reminders_page = tk.Frame(self.notebook)
        self.notebook.add(self.reminders_page, text="Напоминания")
        self.setup_reminders_page()

        # Вкладка "Цели"
        self.goals_page = tk.Frame(self.notebook)
        self.notebook.add(self.goals_page, text="Цели")
        self.setup_goals_page()

    def setup_main_page(self):
        tk.Label(self.main_page, text=f"Добро пожаловать, {self.user[1]}!", font=("Arial", 16)).pack(pady=10)

        # Значок пользователя
        user_icon = tk.PhotoImage(file="user_icon.png")  # Добавьте подходящий значок
        tk.Label(self.main_page, image=user_icon).pack()
        self.mainloop()  # Не забываем удерживать изображение

    def setup_expenses_page(self):
        tk.Label(self.expenses_page, text="Построить диаграмму расходов:", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.expenses_page, text="Вывести диаграмму", command=self.plot_expenses).pack()

    def plot_expenses(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, SUM(amount) FROM transactions
            WHERE user_id = ? AND type = 'expense'
            GROUP BY category
        """, (self.user[0],))
        data = cursor.fetchall()
        conn.close()

        categories = [row[0] for row in data]
        amounts = [row[1] for row in data]

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(categories, amounts, color='skyblue')
        ax.set_title("Расходы по категориям")
        ax.set_ylabel("Сумма")
        ax.set_xlabel("Категории")

        canvas = FigureCanvasTkAgg(fig, self.expenses_page)
        canvas.get_tk_widget().pack()

    def setup_transactions_page(self):
        tk.Label(self.transactions_page, text="Список транзакций:", font=("Arial", 14)).pack(pady=10)
        transactions_table = ttk.Treeview(self.transactions_page, columns=("amount", "category", "type", "date"), show="headings")
        transactions_table.pack(fill=tk.BOTH, expand=True)
        transactions_table.heading("amount", text="Сумма")
        transactions_table.heading("category", text="Категория")
        transactions_table.heading("type", text="Тип")
        transactions_table.heading("date", text="Дата")

        # Получение данных из базы
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT amount, category, type, date FROM transactions WHERE user_id = ?
        """, (self.user[0],))
        for row in cursor.fetchall():
            transactions_table.insert("", tk.END, values=row)
        conn.close()

    def setup_reminders_page(self):
        tk.Label(self.reminders_page, text="Список напоминаний:", font=("Arial", 14)).pack(pady=10)

        reminders_table = ttk.Treeview(self.reminders_page, columns=("message", "reminder_date", "show_on_main"), show="headings")
        reminders_table.pack(fill=tk.BOTH, expand=True)
        reminders_table.heading("message", text="Сообщение")
        reminders_table.heading("reminder_date", text="Дата")
        reminders_table.heading("show_on_main", text="На главной")

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT message, reminder_date, show_on_main FROM reminders WHERE user_id = ?
        """, (self.user[0],))
        for row in cursor.fetchall():
            reminders_table.insert("", tk.END, values=row)
        conn.close()

    def setup_goals_page(self):
        tk.Label(self.goals_page, text="Финансовые цели:", font=("Arial", 14)).pack(pady=10)

        # Список целей
        self.goals_frame = tk.Frame(self.goals_page)
        self.goals_frame.pack(fill=tk.BOTH, expand=True)

        self.update_goals_list()

        # Кнопка для добавления новой цели
        tk.Button(self.goals_page, text="Добавить новую цель", command=self.add_goal_window).pack(pady=10)

    def update_goals_list(self):
        # Очистка текущего списка целей
        for widget in self.goals_frame.winfo_children():
            widget.destroy()

        # Получение данных о целях из базы
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, description, target_amount, current_amount, creation_date, target_date 
            FROM goals WHERE user_id = ?
        """, (self.user[0],))
        goals = cursor.fetchall()
        conn.close()

        for goal in goals:
            goal_id, title, description, target_amount, current_amount, creation_date, target_date = goal

            # Заголовок цели
            goal_frame = tk.Frame(self.goals_frame, bd=2, relief=tk.SOLID, padx=10, pady=5)
            goal_frame.pack(fill=tk.X, pady=5)

            tk.Label(goal_frame, text=title, font=("Arial", 12, "bold")).pack(anchor=tk.W)
            tk.Label(goal_frame, text=f"Описание: {description or 'Нет описания'}", font=("Arial", 10)).pack(anchor=tk.W)
            tk.Label(goal_frame, text=f"Целевая сумма: {target_amount}, Накоплено: {current_amount}", font=("Arial", 10)).pack(anchor=tk.W)
            tk.Label(goal_frame, text=f"Дата создания: {creation_date}, К сроку: {target_date}", font=("Arial", 10)).pack(anchor=tk.W)

            # Шкала прогресса
            progress = current_amount / target_amount if target_amount else 0
            progress_bar = ttk.Progressbar(goal_frame, value=progress * 100, maximum=100)
            progress_bar.pack(fill=tk.X, pady=5)

            # Кнопка для редактирования цели
            tk.Button(goal_frame, text="Редактировать", command=lambda g_id=goal_id: self.edit_goal_window(g_id)).pack(anchor=tk.E)

    def add_goal_window(self):
        # Окно для добавления новой цели
        new_goal_window = tk.Toplevel(self)
        new_goal_window.title("Добавить новую цель")
        new_goal_window.geometry("400x300")

        tk.Label(new_goal_window, text="Название цели:").pack(pady=5)
        title_entry = tk.Entry(new_goal_window)
        title_entry.pack(pady=5)

        tk.Label(new_goal_window, text="Описание цели (необязательно):").pack(pady=5)
        description_entry = tk.Entry(new_goal_window)
        description_entry.pack(pady=5)

        tk.Label(new_goal_window, text="Целевая сумма:").pack(pady=5)
        target_amount_entry = tk.Entry(new_goal_window)
        target_amount_entry.pack(pady=5)

        tk.Label(new_goal_window, text="Дата завершения (ГГГГ-ММ-ДД):").pack(pady=5)
        target_date_entry = tk.Entry(new_goal_window)
        target_date_entry.pack(pady=5)

        def save_goal():
            title = title_entry.get()
            description = description_entry.get()
            target_amount = target_amount_entry.get()
            target_date = target_date_entry.get()
            creation_date = datetime.now().strftime('%Y-%m-%d')

            if not title or not target_amount or not target_date:
                messagebox.showerror("Ошибка", "Заполните все обязательные поля!")
                return

            try:
                target_amount = float(target_amount)
            except ValueError:
                messagebox.showerror("Ошибка", "Целевая сумма должна быть числом!")
                return

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO goals (user_id, title, description, target_amount, current_amount, creation_date, target_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (self.user[0], title, description, target_amount, 0, creation_date, target_date))
            conn.commit()
            conn.close()

            messagebox.showinfo("Успех", "Цель успешно добавлена!")
            new_goal_window.destroy()
            self.update_goals_list()

        tk.Button(new_goal_window, text="Сохранить", command=save_goal).pack(pady=10)

    def edit_goal_window(self, goal_id):
        # Окно для редактирования цели
        edit_goal_window = tk.Toplevel(self)
        edit_goal_window.title("Редактировать цель")
        edit_goal_window.geometry("400x300")

        # Получение данных о цели
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, description, target_amount, current_amount, target_date 
            FROM goals WHERE id = ?
        """, (goal_id,))
        goal = cursor.fetchone()
        conn.close()

        if not goal:
            messagebox.showerror("Ошибка", "Цель не найдена!")
            edit_goal_window.destroy()
            return

        title, description, target_amount, current_amount, target_date = goal

        tk.Label(edit_goal_window, text="Название цели:").pack(pady=5)
        title_entry = tk.Entry(edit_goal_window)
        title_entry.insert(0, title)
        title_entry.pack(pady=5)

        tk.Label(edit_goal_window, text="Описание цели:").pack(pady=5)
        description_entry = tk.Entry(edit_goal_window)
        description_entry.insert(0, description or "")
        description_entry.pack(pady=5)

        tk.Label(edit_goal_window, text="Целевая сумма:").pack(pady=5)
        target_amount_entry = tk.Entry(edit_goal_window)
        target_amount_entry.insert(0, target_amount)
        target_amount_entry.pack(pady=5)

        tk.Label(edit_goal_window, text="Текущая сумма:").pack(pady=5)
        current_amount_entry = tk.Entry(edit_goal_window)
        current_amount_entry.insert(0, current_amount)
        current_amount_entry.pack(pady=5)

        tk.Label(edit_goal_window, text="Дата завершения (ГГГГ-ММ-ДД):").pack(pady=5)
        target_date_entry = tk.Entry(edit_goal_window)
        target_date_entry.insert(0, target_date)
        target_date_entry.pack(pady=5)

        def save_changes():
            new_title = title_entry.get()
            new_description = description_entry.get()
            new_target_amount = target_amount_entry.get()
            new_current_amount = current_amount_entry.get()
            new_target_date = target_date_entry.get()

            if not new_title or not new_target_amount or not new_target_date:
                messagebox.showerror("Ошибка", "Заполните все обязательные поля!")
                return

            try:
                new_target_amount = float(new_target_amount)
                new_current_amount = float(new_current_amount)
            except ValueError:
                messagebox.showerror("Ошибка", "Суммы должны быть числами!")
                return

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE goals
                SET title = ?, description = ?, target_amount = ?, current_amount = ?, target_date = ?
                WHERE id = ?
            """, (new_title, new_description, new_target_amount, new_current_amount, new_target_date, goal_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Успех", "Цель успешно обновлена!")
            edit_goal_window.destroy()
            self.update_goals_list()

        tk.Button(edit_goal_window, text="Сохранить изменения", command=save_changes).pack(pady=10)


# === Запуск приложения ===
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

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# === Функции для работы с базой данных ===
def create_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Таблица транзакций
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            type TEXT NOT NULL,  -- "income" или "expense"
            date TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Таблица напоминаний
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            reminder_date TEXT NOT NULL,
            show_on_main INTEGER NOT NULL DEFAULT 1, -- 1 = отображать, 0 = не отображать
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Таблица целей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            target_amount REAL NOT NULL,
            current_amount REAL NOT NULL DEFAULT 0,
            creation_date TEXT NOT NULL,
            target_date TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()



