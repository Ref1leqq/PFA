import json
from datetime import datetime
import random
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext
import hashlib

# База данных SQLite
database_name = "bank_accounts.db"

# Шифрование паролей
def hash_password(password):
    """Хэширует пароль с использованием SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

# Создание таблицы в базе данных (если ее еще нет)
def create_table():
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_number TEXT PRIMARY KEY,
            password TEXT,
            balance REAL,
            transactions TEXT
        )
    """)
    conn.commit()
    conn.close()

create_table()

class Account:
    def __init__(self, account_number, password, initial_balance=0):
        self.balance = initial_balance
        self.transactions = []
        self.account_number = account_number
        self.password = password

    def deposit(self, amount):
        try:
            amount = float(amount)
            if amount > 0:
                self.balance += amount
                self.transactions.append({
                    "type": "Депозит",
                    "amount": amount,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                self.update_account_data()
                messagebox.showinfo("Успех", f"Успешно внесено {amount} на счет {self.account_number}.")
            else:
                messagebox.showerror("Ошибка", "Сумма вклада должна быть больше 0.")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму вклада.")

    def withdraw(self, amount):
        try:
            amount = float(amount)
            if amount > 0 and amount <= self.balance:
                self.balance -= amount
                self.transactions.append({
                    "type": "Снятие",
                    "amount": amount,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                self.update_account_data()
                messagebox.showinfo("Успех", f"Успешно снято {amount} со счета {self.account_number}.")
            elif amount > self.balance:
                messagebox.showerror("Ошибка", f"Недостаточно средств на счету {self.account_number}.")
            else:
                messagebox.showerror("Ошибка", "Сумма снятия должна быть больше 0.")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму снятия.")

    def transfer(self, amount, recipient_account_number):
        try:
            amount = float(amount)
            if amount > 0 and amount <= self.balance:
                if validate_account_number(recipient_account_number):
                    self.balance -= amount
                    self.transactions.append({
                        "type": "Перевод",
                        "amount": amount,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "recipient": recipient_account_number
                    })
                    self.update_account_data()

                    # Обновление данных получателя
                    conn = sqlite3.connect(database_name)
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        UPDATE accounts
                        SET balance = balance + ?,
                        transactions = transactions || ?
                        WHERE account_number = ?
                        """,
                        (
                            amount,
                            json.dumps(
                                [
                                    {
                                        "type": "Поступление",
                                        "amount": amount,
                                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        "sender": self.account_number,
                                    }
                                ]
                            ),
                            recipient_account_number,
                        )
                    )
                    conn.commit()
                    conn.close()

                    messagebox.showinfo(
                        "Успех",
                        f"Успешно переведено {amount} со счета {self.account_number} на счет {recipient_account_number}."
                    )
                else:
                    messagebox.showerror("Ошибка", "Некорректный номер счета получателя.")
            elif amount > self.balance:
                messagebox.showerror("Ошибка", f"Недостаточно средств на счету {self.account_number}.")
            else:
                messagebox.showerror("Ошибка", "Сумма перевода должна быть больше 0.")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму перевода.")

    def get_balance(self):
        return self.balance

    def get_transactions(self):
        return self.transactions

    def print_statement(self):
        print(f"Выписка по счету {self.account_number}:")
        print("-" * 20)
        for transaction in self.transactions:
            print(
                f"{transaction['date']}  {transaction['type']}  {transaction['amount']}"
            )
        print("-" * 20)
        print(f"Текущий баланс: {self.balance}")

    def update_account_data(self):
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE accounts
            SET balance = ?,
            transactions = ?
            WHERE account_number = ?
            """,
            (self.balance, json.dumps(self.transactions), self.account_number),
        )
        conn.commit()
        conn.close()
def create_account():
    account_number = str(random.randint(1000000000, 9999999999))
    password = password_entry.get()
    while True:
        confirm_password = confirm_password_entry.get()
        if password == confirm_password:
            hashed_password = hash_password(password)  # Шифруем пароль перед сохранением
            break
        else:
            messagebox.showerror("Ошибка", "Пароли не совпадают. Попробуйте снова.")
            return
    account = Account(account_number, hashed_password)
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO accounts (account_number, password, balance, transactions)
        VALUES (?, ?, ?, ?)
        """,
        (account_number, hashed_password, account.balance, json.dumps(account.transactions)),
    )
    conn.commit()
    conn.close()
    messagebox.showinfo("Успех", f"Новый счет создан. Номер счета: {account_number}")
    create_account_window.destroy()
def load_account_data(account_number):
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT password, balance, transactions
        FROM accounts
        WHERE account_number = ?
        """,
        (account_number,),
    )
    result = cursor.fetchone()
    conn.close()
    if result:
        password, balance, transactions = result
        account = Account(account_number, password, balance)
        account.transactions = json.loads(transactions)
        return account
    else:
        messagebox.showerror("Ошибка", f"Счет с номером {account_number} не найден.")
        return None

def login():
    account_number = account_number_entry.get()
    account = load_account_data(account_number)
    if account:
        attempts = 3
        while attempts > 0:
            password = password_entry.get()
            if hash_password(password) == account.password:  # Сравниваем хэши
                messagebox.showinfo("Успех", f"Вход выполнен успешно. Добро пожаловать, {account_number}!")
                login_window.destroy()
                open_main_window(account)
                return
            else:
                attempts -= 1
                messagebox.showerror(
                    "Ошибка", f"Неверный пароль. Осталось попыток: {attempts}"
                )
        messagebox.showerror("Ошибка", "Слишком много попыток. Доступ заблокирован.")
        return None
    else:
        return None
def open_main_window(account):
    global main_window
    main_window = tk.Tk()
    main_window.title("Банковское Приложение")

    # Информация о счете
    account_info_label = tk.Label(
        main_window, text=f"Номер счета: {account.account_number}"
    )
    account_info_label.pack()

    balance_label = tk.Label(
        main_window, text=f"Текущий баланс: {account.get_balance()}"
    )
    balance_label.pack()

    # Кнопки действий
    def deposit_action():
        amount = get_amount_from_entry(deposit_entry)
        if amount is not None:
            account.deposit(amount)
            balance_label.config(text=f"Текущий баланс: {account.get_balance()}")
            deposit_entry.delete(0, tk.END)

    def withdraw_action():
        amount = get_amount_from_entry(withdraw_entry)
        if amount is not None:
            account.withdraw(amount)
            balance_label.config(text=f"Текущий баланс: {account.get_balance()}")
            withdraw_entry.delete(0, tk.END)

    def transfer_action():
        recipient_account_number = recipient_account_entry.get()
        amount = get_amount_from_entry(transfer_amount_entry)
        if amount is not None:
            account.transfer(amount, recipient_account_number)
            balance_label.config(text=f"Текущий баланс: {account.get_balance()}")
            recipient_account_entry.delete(0, tk.END)
            transfer_amount_entry.delete(0, tk.END)

    def print_statement_action():
        statement_window = tk.Toplevel(main_window)
        statement_window.title("Выписка по счету")
        statement_text = scrolledtext.ScrolledText(statement_window, wrap=tk.WORD)
        statement_text.pack()
        statement_text.insert(tk.END, f"Выписка по счету {account.account_number}:\n")
        statement_text.insert(tk.END, "-" * 20 + "\n")
        for transaction in account.transactions:
            statement_text.insert(
                tk.END,
                f"{transaction['date']}  {transaction['type']}  {transaction['amount']}\n",
            )
        statement_text.insert(tk.END, "-" * 20 + "\n")
        statement_text.insert(tk.END, f"Текущий баланс: {account.balance}")

    def change_password_action():
        change_password_window = tk.Toplevel(main_window)
        change_password_window.title("Изменить пароль")

        current_password_label = tk.Label(change_password_window, text="Текущий пароль:")
        current_password_label.pack()
        current_password_entry = tk.Entry(change_password_window, show="*")
        current_password_entry.pack()

        new_password_label = tk.Label(change_password_window, text="Новый пароль:")
        new_password_label.pack()
        new_password_entry = tk.Entry(change_password_window, show="*")
        new_password_entry.pack()

        confirm_password_label = tk.Label(change_password_window, text="Подтвердить новый пароль:")
        confirm_password_label.pack()
        confirm_password_entry = tk.Entry(change_password_window, show="*")
        confirm_password_entry.pack()

        def change_password():
            current_password = current_password_entry.get()
            new_password = new_password_entry.get()
            confirm_password = confirm_password_entry.get()

            if hash_password(current_password) == account.password:
                if new_password == confirm_password:
                    hashed_new_password = hash_password(new_password)
                    account.password = hashed_new_password
                    account.update_account_data()
                    messagebox.showinfo("Успех", "Пароль успешно изменен!")
                    change_password_window.destroy()
                else:
                    messagebox.showerror("Ошибка", "Новые пароли не совпадают.")
            else:
                messagebox.showerror("Ошибка", "Неверный текущий пароль.")

        change_button = tk.Button(change_password_window, text="Изменить", command=change_password)
        change_button.pack()

    deposit_button = tk.Button(main_window, text="Внести средства", command=deposit_action)
    deposit_button.pack()
    deposit_entry = tk.Entry(main_window)
    deposit_entry.pack()

    withdraw_button = tk.Button(main_window, text="Снять средства", command=withdraw_action)
    withdraw_button.pack()
    withdraw_entry = tk.Entry(main_window)
    withdraw_entry.pack()

    transfer_button = tk.Button(main_window, text="Перевести средства", command=transfer_action)
    transfer_button.pack()
    recipient_account_label = tk.Label(main_window, text="Номер счета получателя:")
    recipient_account_label.pack()
    recipient_account_entry = tk.Entry(main_window)
    recipient_account_entry.pack()
    transfer_amount_label = tk.Label(main_window, text="Сумма перевода:")
    transfer_amount_label.pack()
    transfer_amount_entry = tk.Entry(main_window)
    transfer_amount_entry.pack()

    statement_button = tk.Button(main_window, text="Выписка", command=print_statement_action)
    statement_button.pack()

    change_password_button = tk.Button(main_window, text="Изменить пароль", command=change_password_action)
    change_password_button.pack()

    main_window.mainloop()
# Окно входа
def create_login_window():
    global login_window, account_number_entry, password_entry
    login_window = tk.Tk()
    login_window.title("Вход в Банк")

    account_number_label = tk.Label(login_window, text="Номер счета:")
    account_number_label.pack()
    account_number_entry = tk.Entry(login_window)
    account_number_entry.pack()

    password_label = tk.Label(login_window, text="Пароль:")
    password_label.pack()
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack()

    login_button = tk.Button(
        login_window, text="Войти", command=login
    )
    login_button.pack()

    login_window.mainloop()
# Окно создания счета
def create_create_account_window():
    global create_account_window, password_entry, confirm_password_entry
    create_account_window = tk.Tk()
    create_account_window.title("Создать Счет")

    password_label = tk.Label(create_account_window, text="Пароль:")
    password_label.pack()
    password_entry = tk.Entry(create_account_window, show="*")
    password_entry.pack()

    confirm_password_label = tk.Label(create_account_window, text="Подтвердить пароль:")
    confirm_password_label.pack()
    confirm_password_entry = tk.Entry(create_account_window, show="*")
    confirm_password_entry.pack()

    create_button = tk.Button(
        create_account_window, text="Создать", command=create_account
    )
    create_button.pack()

    create_account_window.mainloop()

def get_amount_from_entry(entry):
    try:
        amount = float(entry.get())
        if amount <= 0:
            messagebox.showerror("Ошибка", "Сумма должна быть больше 0")
            return None
        return amount
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректную сумму")
        return None
def validate_account_number(account_number):
    if len(account_number) == 10 and account_number.isdigit():
        return True
    return False

def main():
    while True:
        print("---------------------")
        print("  БАНКОВСКОЕ ПРИЛОЖЕНИЕ  ")
        print("---------------------")
        choice = input("1. Создать новый счет\n2. Войти в существующий счет\n3. Выход\nВведите номер: ")

        if choice == "1":
            create_create_account_window()

        elif choice == "2":
            create_login_window()

        elif choice == "3":
            print("Выход из приложения.")
            break

        else:
            print("Неверный выбор.")

if __name__ == "__main__":
    main()
