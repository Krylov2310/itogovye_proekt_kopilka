from datetime import datetime, date
import json
import os
import platform

student = '\033[33mИтоговое задание\n"Копилка"\nСтудент Крылов Эдуард Васильевич\nДата: 26.11.2025г.\033[0m\n'


# Очистка консоли
def clear_screen():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')  # From Linux


class Goal:
    def __init__(self, name, target_amount, category, start_date=None):
        self.name = name
        self.target_amount = float(target_amount)
        self.current_balance = 0.0
        self.category = category
        self.status = 'активна'
        self.start_date = start_date or date.today()
        self.completion_date = None

    def add_funds(self, amount):
        if amount <= 0:
            raise ValueError('\033[31mСумма должна быть положительной!\033[0m')
        new_balance = self.current_balance + amount
        if new_balance >= self.target_amount:
            self.current_balance = self.target_amount
            self.status = 'выполнена'
            self.completion_date = date.today()
        else:
            self.current_balance = new_balance

    def withdraw_funds(self, amount):
        if amount <= 0:
            raise ValueError('\033[31mСумма должна быть положительной!\033[0m')
        if amount > self.current_balance:
            raise ValueError('\033[31mНедостаточно средств на балансе!\033[0m')
        self.current_balance -= amount

    def get_progress(self):
        return (self.current_balance / self.target_amount) * 100

    def change_status(self, new_status):
        valid_statuses = ['активна', 'выполнена', 'отменена']
        if new_status not in valid_statuses:
            raise ValueError(f'\033[31mСтатус должен быть одним из: \033[0m{valid_statuses}')
        self.status = new_status

    def to_dict(self):
        return {
            'name': self.name,
            'target_amount': self.target_amount,
            'current_balance': self.current_balance,
            'category': self.category,
            'status': self.status,
            'start_date': self.start_date.isoformat(),
            'completion_date': self.completion_date.isoformat() if self.completion_date else None
        }

    @classmethod
    def from_dict(cls, data):
        goal = cls(
            name=data['name'],
            target_amount=data['target_amount'],
            category=data['category'],
            start_date=datetime.fromisoformat(data['start_date']).date()
        )
        goal.current_balance = data['current_balance']
        goal.status = data['status']
        if data['completion_date']:
            goal.completion_date = datetime.fromisoformat(data['completion_date']).date()
        return goal


class GoalManager:
    def __init__(self, data_file='goals.json'):
        self.data_file = data_file
        self.goals = []
        self.categories = ['Работа', 'Здоровье', 'Образование', 'Путешествия', 'Дом', 'Другое']
        self.load_data()

    def add_goal(self, name, target_amount, category):
        if category not in self.categories:
            raise ValueError(f'\033[31mКатегория должна быть одной из: \033[0m{self.categories}')
        goal = Goal(name, target_amount, category)
        self.goals.append(goal)
        self.save_data()
        return goal

    def remove_goal(self, goal_name):
        for i, goal in enumerate(self.goals):
            if goal.name == goal_name:
                del self.goals[i]
                self.save_data()
                return True
        return False

    def find_goal(self, goal_name):
        for goal in self.goals:
            if goal.name == goal_name:
                return goal
        return None

    def get_all_goals(self):
        return self.goals

    def get_goals_by_category(self, category):
        return [goal for goal in self.goals if goal.category == category]

    def get_total_progress(self):
        if not self.goals:
            return 0.0
        total_target = sum(goal.target_amount for goal in self.goals)
        total_current = sum(goal.current_balance for goal in self.goals)
        return (total_current / total_target) * 100 if total_target > 0 else 0.0

    def save_data(self):
        data = {
            'categories': self.categories,
            'goals': [goal.to_dict() for goal in self.goals]
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        # Считываем данные
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.categories = data.get('categories', self.categories)
                self.goals = [Goal.from_dict(goal_data) for goal_data in data.get('goals', [])]
            except (json.JSONDecodeError, KeyError) as e:
                print(f'\033[31mОшибка при загрузке данных: {e}!\033[0m')
                self.goals = []

    def add_funds_to_goal(self, goal_name, amount):
        # Пополняем цель и сохраняем изменения
        goal = self.find_goal(goal_name)
        if not goal:
            raise ValueError('\033[31mЦель не найдена\033[0m')
        goal.add_funds(amount)
        self.save_data()

    def withdraw_from_goal(self, goal_name, amount):
        # Снимаем средства и сохраняем изменения
        goal = self.find_goal(goal_name)
        if not goal:
            raise ValueError('\033[31mЦель не найдена\033[0m')
        goal.withdraw_funds(amount)
        self.save_data()

    def update_goal_status(self, goal_name, new_status):
        # Изменяем статус и сохраняем
        goal = self.find_goal(goal_name)
        if not goal:
            raise ValueError('\033[31mЦель не найдена\033[0m')
        goal.change_status(new_status)
        self.save_data()


def print_goal(goal, progress):
    print('\033[33m=' * 30)
    print(f'\033[35mНазвание цели : \033[0m{goal.name}\n'
          f'\033[35mКатегория: \033[0m{goal.category}\n'
          f'\033[35mСумма цели: \033[0m{goal.target_amount:.2f}\n'
          f'\033[35mПополнение цели: \033[0m{goal.current_balance:.2f}\n'
          f'\033[35mПроцент исполнения: \033[0m({progress:.1f}%)\n'
          f'\033[35mДата начала цели: \033[0m{goal.start_date}\n'
          f'\033[35mДата окончания цели: \033[0m{goal.completion_date}\n'
          f'\033[35mСтатус цели: \033[0m{goal.status}\033[0m')


def main():
    manager = GoalManager()

    while True:
        print('\n\033[36m=== Управление целями ===\033[0m')
        print('\033[33m1. \033[0mДобавить цель')
        print('\033[33m2. \033[0mПросмотреть все цели')
        print('\033[33m3. \033[0mПросмотреть цели по категории')
        print('\033[33m4. \033[0mПополнить цель')
        print('\033[33m5. \033[0mСнять средства с цели')
        print('\033[33m6. \033[0mИзменить статус цели')
        print('\033[33m7. \033[0mУдалить цель')
        print('\033[33m8. \033[0mОбщий прогресс')
        print('\033[33m9. \033[0mВыход')

        choice = input('\033[34mВыберите действие (1-9): \033[0m').strip()
        print()
        # clear_screen()

        if choice == '1':
            name = input('\033[32mНазвание цели: \033[0m').strip()
            try:
                amount = float(input('\033[34mСумма для накопления: \033[0m'))
                category = input(f'\033[34mКатегория \033[0m({', '.join(manager.categories)}): ').strip()
                goal = manager.add_goal(name, amount, category)
                print(f'\033[32mЦель "{goal.name}" добавлена!\033[0m')
            except ValueError as e:
                print(f'\033[31mОшибка: {e}\033[0m')

        elif choice == '2':
            if not manager.get_all_goals():
                print('\033[31mНет целей!\033[0m')
            else:
                for goal in manager.get_all_goals():
                    progress = goal.get_progress()
                    print_goal(goal, progress)

        elif choice == '3':
            category = input(f'\033[34mКатегория ({', '.join(manager.categories)}): \033[0m').strip()
            goals = manager.get_goals_by_category(category)
            if not goals:
                print('\033[31mНет целей в этой категории!\033[0m')
            else:
                for goal in goals:
                    progress = goal.get_progress()
                    print_goal(goal, progress)

        elif choice == '4':
            name = input('\033[34mНазвание цели: \033[0m').strip()
            try:
                amount = float(input('\033[34mСумма для пополнения: \033[0m'))
                manager.add_funds_to_goal(name, amount)  # Вызов через менеджер
                goal = manager.find_goal(name)
                print(f'\033[32mПополнено на \033[0m{amount:.2f}. '
                      f'\033[34mТекущий баланс: \033[0m{goal.current_balance:.2f}')
            except ValueError as e:
                print(f'\033[31mОшибка: {e}\033[0m')

        elif choice == '5':
            name = input('\033[34mНазвание цели: \033[0m').strip()
            try:
                amount = float(input('\033[34mСумма для снятия: \033[0m'))
                manager.withdraw_from_goal(name, amount)  # Вызов через менеджер
                goal = manager.find_goal(name)
                print(f'\033[32mСнято \033[0m{amount:.2f}\033[32m. Текущий баланс: \033[0m{goal.current_balance:.2f}')
            except ValueError as e:
                print(f'\033[31mОшибка: {e}\033[0m')

        elif choice == '6':
            name = input('\033[34mНазвание цели: \033[0m').strip()
            new_status = input('\033[34mНовый статус (активна/выполнена/отменена): \033[0m').strip()
            try:
                manager.update_goal_status(name, new_status)
            except ValueError as e:
                print(f'\033[31mОшибка: {e}\033[0m')

        elif choice == '7':
            name = input('\033[34mНазвание цели: \033[0m').strip()
            if manager.remove_goal(name):
                print(f'\033[31mЦель \033[0m"{name}"\033[31m удалена!\033[0m')
            else:
                print('\033[31mЦель не найдена!\033[0m')

        elif choice == '8':
            total_progress = manager.get_total_progress()
            print(f'\033[34mОбщий прогресс по всем целям: \033[0m{total_progress:.1f}%')

        elif choice == '9':
            print('\033[33mДо свидания!\033[0m')
            break
        else:
            print('\033[31mНеверный выбор. Пожалуйста, введите число от 1 до 9!\033[0m\n')


if __name__ == '__main__':
    clear_screen()
    print(student)
    main()
