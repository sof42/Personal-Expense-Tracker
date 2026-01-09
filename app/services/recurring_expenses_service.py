from app.models.recurring_expenses import RecurringExpense
from app.models.expense import Expense
from app.extensions import db
from datetime import date, timedelta

def generate_recurring_expenses_for_user(user_id):
    today = date.today()
    recurring_expenses = RecurringExpense.query.filter_by(user_id=user_id).all()

    for rec in recurring_expenses:
        next_date = rec.last_generated or rec.start_date

        while next_date <= today:
            # Only add expense if not already generated for that date
            exists = Expense.query.filter_by(user_id=user_id, description=rec.title, date=next_date).first()
            if not exists:
                exp = Expense(
                    user_id=user_id,
                    description=rec.title,
                    amount=rec.amount,
                    category=rec.category,
                    date=next_date
                )
                db.session.add(exp)

            # Calculate next occurrence
            if rec.frequency == "daily":
                next_date += timedelta(days=1)
            elif rec.frequency == "weekly":
                next_date += timedelta(weeks=1)
            elif rec.frequency == "monthly":
                month = next_date.month + 1
                year = next_date.year + month // 13
                month = month % 12 or 12
                next_date = next_date.replace(year=year, month=month)
            elif rec.frequency == "yearly":
                next_date = next_date.replace(year=next_date.year + 1)
            else:
                break

        # Update last_generated
        rec.last_generated = today

    db.session.commit()
