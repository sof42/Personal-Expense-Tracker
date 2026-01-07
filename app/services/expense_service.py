# app/services/expense_service.py
from app.models.expense import Expense
from app.models.user import User
from app.extensions import db
from datetime import datetime
from sqlalchemy import func

def add_expense(user_id, description, amount, category=None):
    """Add a new expense for a user."""
    new_expense = Expense(
        user_id=user_id,
        description=description,
        amount=amount,
        category=category,
        date=datetime.utcnow()
    )
    db.session.add(new_expense)
    db.session.commit()
    return new_expense

def get_user_expenses(user_id):
    """Return all expenses for a user, newest first."""
    return Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc()).all()

def get_expense_by_id(expense_id):
    """Fetch a single expense by ID."""
    return Expense.query.get(expense_id)

def delete_expense(expense_id):
    """Delete an expense by ID."""
    expense = Expense.query.get(expense_id)
    if not expense:
        return False
    db.session.delete(expense)
    db.session.commit()
    return True

def get_expenses_by_category(user_id):
    """Return total amount per category for a user."""
    return (
        db.session.query(Expense.category, func.sum(Expense.amount))
        .filter_by(user_id=user_id)
        .group_by(Expense.category)
        .all()
    )