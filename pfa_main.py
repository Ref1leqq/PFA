import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import sqlite3
from datetime import datetime


def create_db():
    conn = sqlite3.connect('users.db') #подключение к базе данных
    cursor = conn.cursor() #создание курсора

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
            type TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()



class FinanceAssistantApp(tk.Tk):
    def __init__(self, user):
        super().__init__()
        self.title("Финансовый помощник")
        self.geometry("800x600")
        self.user = user
        icon = PhotoImage(file = "logo.png")
        self.iconphoto(False, icon)

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

        self.balance_label = tk.Label(self.home_page, text="Текущий баланс: 0.00 RUB", font=("Arial", 14))
        self.balance_label.pack(pady=10)

        self.earnings_label = tk.Label(self.home_page, text="Заработано: 0.00 RUB", font=("Arial", 12))
        self.earnings_label.pack(pady=5)

        self.expenses_label = tk.Label(self.home_page, text="Потрачено: 0.00 RUB", font=("Arial", 12))
        self.expenses_label.pack(pady=5)

        tk.Button(self.home_page, text="Добавить транзакцию", command=self.add_transaction_window).pack(pady=10)

        self.update_balance()

    def update_balance(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(CASE WHEN type = "Доход" THEN amount ELSE 0 END) as total_income,
                   SUM(CASE WHEN type = "Расход" THEN amount ELSE 0 END) as total_expense
            FROM transactions
            WHERE user_id = ?
        ''', (self.user[0],))
        result = cursor.fetchone()
        conn.close()

        total_income = result[0] if result[0] is not None else 0.0
        total_expense = result[1] if result[1] is not None else 0.0
        current_balance = total_income - total_expense

        self.balance_label.config(text=f"Текущий баланс: {current_balance:.2f} RUB")
        self.earnings_label.config(text=f"Заработано: {total_income:.2f} RUB")
        self.expenses_label.config(text=f"Потрачено: {total_expense:.2f} RUB")

    def setup_transactions_page(self):
        tk.Label(self.transactions_page, text="История транзакций", font=("Arial", 16)).pack(pady=10)
        self.transactions_tree = ttk.Treeview(self.transactions_page, columns=("category", "amount","type", "date"), show="headings")
        self.transactions_tree.heading("category", text="Категория")
        self.transactions_tree.heading("amount", text="Сумма")
        self.transactions_tree.heading("type", text="Тип")
        self.transactions_tree.heading("date", text="Дата")
        self.transactions_tree.pack(fill=tk.BOTH, expand=True)
        self.update_transactions_list()

    def update_transactions_list(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, amount, type, date FROM transactions WHERE user_id = ?
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
        add_window.geometry("300x400")  # Увеличиваем высоту окна для радиокнопок

        tk.Label(add_window, text="Тип транзакции:").pack(pady=5)

        transaction_type = tk.StringVar(value="Расход")  # Значение по умолчанию - "Расход"

        # Радиокнопки для выбора типа транзакции
        def update_categories():
            if transaction_type.get() == "Доход":
                combobox["values"] = []  # Убираем значения для выбора
                category_entry.config(state=tk.NORMAL)  # Разрешаем ввод
            else:
                combobox["values"] = ["Продукты", "Одежда", "Такси"]  # Категории для расхода
                category_entry.delete(0, tk.END)  # Очищаем пользовательский ввод
                category_entry.config(state=tk.DISABLED)  # Запрещаем ввод

        income_radiobutton = tk.Radiobutton(add_window, text="Доход", variable=transaction_type, value="Доход",
                                            command=update_categories)
        income_radiobutton.pack()
        expense_radiobutton = tk.Radiobutton(add_window, text="Расход", variable=transaction_type, value="Расход",
                                             command=update_categories)
        expense_radiobutton.pack()

        tk.Label(add_window, text="Категория:").pack(pady=5)

        # Поле выбора или ввода категории
        combobox = ttk.Combobox(add_window)
        combobox.pack(padx=6, pady=6)

        category_entry = tk.Entry(add_window, state=tk.DISABLED)  # Поле для пользовательского ввода категории дохода
        category_entry.pack(padx=6, pady=6)

        tk.Label(add_window, text="Сумма:").pack(pady=5)
        amount_entry = tk.Entry(add_window)
        amount_entry.pack(pady=5)

        def save_transaction():
            category = category_entry.get() if transaction_type.get() == "Доход" else combobox.get()
            amount = amount_entry.get()
            transaction_type_value = transaction_type.get()

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
                INSERT INTO transactions (user_id, category, amount, date, type) VALUES (?, ?, ?, ?, ?)
            """, (self.user[0], category, amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), transaction_type_value))
            conn.commit()
            conn.close()

            if transaction_type_value == "Доход":
                self.update_goal_progress(amount)

            messagebox.showinfo("Успех", "Транзакция добавлена!")
            add_window.destroy()
            self.update_transactions_list()
            self.update_balance()

        tk.Button(add_window, text="Сохранить", command=save_transaction).pack(pady=10)

    def setup_goals_page(self):
        tk.Label(self.goals_page, text="Финансовые цели", font=("Arial", 16)).pack(pady=10)

        self.goals_tree = ttk.Treeview(self.goals_page, columns=("title", "target_amount", "remaining"), show="headings")
        self.goals_tree.heading("title", text="Название")
        self.goals_tree.heading("target_amount", text="Цель (₽)")
        self.goals_tree.heading("remaining", text="Осталось времени")
        self.goals_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Button(self.goals_page, text="Добавить цель", command=self.add_goal_window).pack(pady=10)

        self.update_goals_list()

    def update_goals_list(self):
        for row in self.goals_tree.get_children():
            self.goals_tree.delete(row)

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, target_amount, current_amount, target_date
            FROM goals
            WHERE user_id = ?
        ''', (self.user[0],))
        goals = cursor.fetchall()
        conn.close()

        for goal_id, title, target_amount, current_amount, target_date in goals:
            remaining_days = (datetime.strptime(target_date, "%Y-%m-%d") - datetime.now()).days
            remaining_text = f"{remaining_days} дн." if remaining_days > 0 else "Срок истёк"

            # Если цель достигнута, добавляем отметку
            if current_amount >= target_amount:
                self.goals_tree.insert(
                    "",
                    tk.END,
                    values=(title, f"{current_amount}/{target_amount}", "Цель достигнута!"),
                    tags=("completed",)
                )
                delete_button = tk.Button(self.goals_page, text="Удалить",
                                          command=lambda gid=goal_id: self.delete_completed_goal(gid))
                delete_button.pack(pady=5)
            else:
                self.goals_tree.insert("", tk.END, values=(title, f"{current_amount}/{target_amount}", remaining_text))

    def add_goal_window(self):
        add_window = tk.Toplevel(self)
        add_window.title("Добавить цель")
        add_window.geometry("400x300")

        tk.Label(add_window, text="Название цели:").pack(pady=5)
        title_entry = tk.Entry(add_window)
        title_entry.pack(pady=5)

        tk.Label(add_window, text="Сумма цели (₽):").pack(pady=5)
        amount_entry = tk.Entry(add_window)
        amount_entry.pack(pady=5)

        tk.Label(add_window, text="Дата достижения (ГГГГ-ММ-ДД):").pack(pady=5)
        date_entry = tk.Entry(add_window)
        date_entry.pack(pady=5)

        def save_goal():
            title = title_entry.get()
            try:
                target_amount = float(amount_entry.get())
                target_date = datetime.strptime(date_entry.get(), "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные данные.")
                return

            if not title or target_amount <= 0 or target_date <= datetime.now().date():
                messagebox.showerror("Ошибка", "Некорректные данные цели.")
                return

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO goals (user_id, title, target_amount, creation_date, target_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.user[0], title, target_amount, datetime.now().strftime("%Y-%m-%d"), target_date))
            conn.commit()
            conn.close()

            messagebox.showinfo("Успех", "Цель добавлена.")
            add_window.destroy()
            self.update_goals_list()

        tk.Button(add_window, text="Сохранить", command=save_goal).pack(pady=10)

    def setup_reminders_page(self):
        tk.Label(self.reminders_page, text="Напоминания", font=("Arial", 16)).pack(pady=10)

        self.reminders_list = tk.Listbox(self.reminders_page)
        self.reminders_list.pack(fill=tk.BOTH, expand=True)

        tk.Button(self.reminders_page, text="Добавить напоминание", command=self.add_reminder_window).pack(pady=10)

    def add_reminder_window(self):
        add_window = tk.Toplevel(self)
        add_window.title("Добавить напоминание")
        add_window.geometry("300x300")
        add_window.resizable(False, False)

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

    def update_goal_progress(self, amount):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, current_amount, target_amount FROM goals WHERE user_id = ?
        ''', (self.user[0],))
        goals = cursor.fetchall()

        for goal_id, current_amount, target_amount in goals:
            new_amount = current_amount + amount

            if new_amount >= target_amount:
                cursor.execute('''
                    UPDATE goals SET current_amount = ?, target_amount = 0 WHERE id = ?
                ''', (target_amount, goal_id))
                messagebox.showinfo("Поздравляем!", f"Цель достигнута!")
            else:
                cursor.execute('''
                    UPDATE goals SET current_amount = ? WHERE id = ?
                ''', (new_amount, goal_id))

        conn.commit()
        conn.close()

        self.update_goals_list()

    def delete_completed_goal(self, goal_id):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Цель удалена.")
        self.update_goals_list()



def clear_text():
    login_entry.delete(0, 'end')
    password_entry.delete(0, 'end')
    confirm_password_entry.delete(0, 'end')

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
        clear_text()
    except sqlite3.IntegrityError:
        messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует!")
    finally:
        conn.close()


def login():
    login = login_entry.get()
    password = password_entry.get()
    confirm_password = confirm_password_entry.get()
    if not login or not password or not confirm_password:
        messagebox.showerror("Ошибка", "Заполните все поля!")
        return
    if password != confirm_password:
        messagebox.showerror("Ошибка", "Пароли не совпадают")
        return

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE login = ? AND password = ?", (login, password))
    user = cursor.fetchone()
    conn.close()

    if user and password == confirm_password:
        messagebox.showinfo("Успех", "Вход выполнен успешно!")
        window.destroy()
        app = FinanceAssistantApp(user)
        app.mainloop()
    else:
        messagebox.showerror("Ошибка", "Проверьте корректность введённых данных!")


create_db()

window = tk.Tk()
window.resizable(width=False, height=False)
window.title("Вход/Регистрация")
window.geometry("800x600")

icon = PhotoImage(file= "logo.png")
window.iconphoto(False, icon)

nameapp_label = tk.Label(window, text = "Finance Helper",fg="#57a1f8", font=('Microsoft Yahei UI Light',23,'bold'))
nameapp_label.place(relx=.5,anchor="n")
login_label = tk.Label(window, text="Логин:")
login_label.place(x=370,y=100)
login_entry = tk.Entry(window)
login_entry.place(x=300,y=130)

password_label = tk.Label(window, text="Пароль:")
password_label.place(x=367,y=180)
password_entry = tk.Entry(window, show="*")
password_entry.place(x=300, y = 210)

confirm_password_label = tk.Label(window, text="Подтверждение пароля:")
confirm_password_label.place(x=315, y = 260)
confirm_password_entry = tk.Entry(window, show="*")
confirm_password_entry.place(x=300, y = 290)

login_button = tk.Button(window, text="Вход", command=login)
login_button.place(x=300,y=320)

register_button = tk.Button(window, text="Регистрация", command=register)
register_button.place(x=375,y=320)

window.mainloop()
#1