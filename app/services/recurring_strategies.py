from datetime import datetime
from app.models.expense import Expense
from app.extensions import db

# Base strategy interface
class RecurringStrategy:
    """Base strategy interface for recurring expenses."""
    def generate(self, recurring_expense, user_id):
        """Generate an Expense from a RecurringExpense."""
        raise NotImplementedError("You must implement the generate() method.")


# Concrete strategies for each frequency
class DailyStrategy(RecurringStrategy):
    def generate(self, recurring_expense, user_id):
        today = datetime.now().date()
        if not recurring_expense.last_generated or recurring_expense.last_generated < today:
            new_expense = Expense(
                user_id=user_id,
                description=recurring_expense.title,
                amount=recurring_expense.amount,
                category=recurring_expense.category,
                date=today
            )
            db.session.add(new_expense)
            recurring_expense.last_generated = today


class MonthlyStrategy(RecurringStrategy):
    def generate(self, recurring_expense, user_id):
        today = datetime.now().date()
        if (not recurring_expense.last_generated 
            or recurring_expense.last_generated.month < today.month 
            or recurring_expense.last_generated.year < today.year):
            new_expense = Expense(
                user_id=user_id,
                description=recurring_expense.title,
                amount=recurring_expense.amount,
                category=recurring_expense.category,
                date=today
            )
            db.session.add(new_expense)
            recurring_expense.last_generated = today


class YearlyStrategy(RecurringStrategy):
    def generate(self, recurring_expense, user_id):
        today = datetime.now().date()
        if (not recurring_expense.last_generated 
            or recurring_expense.last_generated.year < today.year):
            new_expense = Expense(
                user_id=user_id,
                description=recurring_expense.title,
                amount=recurring_expense.amount,
                category=recurring_expense.category,
                date=today
            )
            db.session.add(new_expense)
            recurring_expense.last_generated = today


# Context class to apply a strategy
class RecurringContext:
    def __init__(self, strategy: RecurringStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: RecurringStrategy):
        self._strategy = strategy

    def generate(self, recurring_expense, user_id):
        self._strategy.generate(recurring_expense, user_id)
