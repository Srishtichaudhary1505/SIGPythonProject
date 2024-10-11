import json
import os
import pandas as pd

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    @staticmethod
    def load_users(filename='users.json'):
        if not os.path.exists(filename):
            return {}
        with open(filename, 'r') as f:
            return json.load(f)

    @staticmethod
    def save_user(user, filename='users.json'):
        users = User.load_users(filename)
        users[user.username] = user.password
        with open(filename, 'w') as f:
            json.dump(users, f)

    @classmethod
    def register(cls, username, password):
        users = cls.load_users()
        if username in users:
            print("Username already exists.")
            return None
        user = cls(username, password)
        cls.save_user(user)
        print("Registration successful.")
        return user

    @classmethod
    def login(cls, username, password):
        users = cls.load_users()
        if username in users and users[username] == password:
            print("Login successful.")
            return cls(username, password)
        print("Invalid credentials.")
        return None

class FinanceRecord:
    def __init__(self, description, amount, category, date):
        self.description = description
        self.amount = amount
        self.category = category
        self.date = date


class FinanceManager:
    def __init__(self, user):
        self.user = user
        self.records = self.load_finances()

    def load_finances(self, filename='finances.json'):
        if not os.path.exists(filename):
            return []
        with open(filename, 'r') as f:
            data = json.load(f)
            return [FinanceRecord(**record) for record in data.get(self.user.username, [])]

    def save_finances(self, filename='finances.json'):
        data = {}
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
        data[self.user.username] = [record.__dict__ for record in self.records]
        with open(filename, 'w') as f:
            json.dump(data, f)

    def add_record(self, record):
        self.records.append(record)
        self.save_finances()

    def delete_record(self, index):
        if 0 <= index < len(self.records):
            del self.records[index]
            self.save_finances()

    def update_record(self, index, new_record):
        if 0 <= index < len(self.records):
            self.records[index] = new_record
            self.save_finances()


class FinanceReport:
    def __init__(self, finance_manager):
        self.finance_manager = finance_manager

    def generate_report(self):
        df = pd.DataFrame([record.__dict__ for record in self.finance_manager.records])
        if df.empty:
            print("No records available.")
            return

        total_income = df[df['amount'] > 0]['amount'].sum()
        total_expenses = df[df['amount'] < 0]['amount'].sum()

        print(f"Total Income: {total_income:.2f}")
        print(f"Total Expenses: {total_expenses:.2f}")

        spending_distribution = df.groupby('category')['amount'].sum()
        print("\nSpending Distribution by Category:\n", spending_distribution)

        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        monthly_trends = df.resample('M').sum()
        print("\nMonthly Trends:\n", monthly_trends)


def main():
    while True:
        action = input("Choose an action: [register, login, exit]: ").strip().lower()
        if action == "register":
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            User.register(username, password)
        elif action == "login":
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            user = User.login(username, password)
            if user:
                finance_manager = FinanceManager(user)
                report = FinanceReport(finance_manager)

                while True:
                    command = input("Choose a command: [add, delete, update, report, logout]: ").strip().lower()
                    if command == "add":
                        description = input("Description: ").strip()
                        amount = float(input("Amount: "))
                        category = input("Category: ").strip()
                        date = input("Date (YYYY-MM-DD): ").strip()
                        record = FinanceRecord(description, amount, category, date)
                        finance_manager.add_record(record)
                    elif command == "delete":
                        index = int(input("Record index to delete: "))
                        finance_manager.delete_record(index)
                    elif command == "update":
                        index = int(input("Record index to update: "))
                        description = input("New Description: ").strip()
                        amount = float(input("New Amount: "))
                        category = input("New Category: ").strip()
                        date = input("New Date (YYYY-MM-DD): ").strip()
                        new_record = FinanceRecord(description, amount, category, date)
                        finance_manager.update_record(index, new_record)
                    elif command == "report":
                        report.generate_report()
                    elif command == "logout":
                        break
        elif action == "exit":
            break

if __name__ == "__main__":
    main()
