from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
from app.extensions import db
from app.models.recurring_expenses import RecurringExpense
from app.models.expense import Expense
from app.models.user import User

recurring_bp = Blueprint("recurring", __name__, url_prefix="/recurring")


# ----------------------------
# Strategy Pattern for Recurring Expenses
# ----------------------------
class RecurringStrategy:
    """Base strategy class defining interface for generating expenses."""
    def generate(self, item, user_id):
        raise NotImplementedError("This method should be implemented by subclasses.")


class DailyStrategy(RecurringStrategy):
    def generate(self, item, user_id):
        today = datetime.now().date()
        if not item.last_generated or item.last_generated < today:
            expense = Expense(
                user_id=user_id,
                description=item.title,
                amount=item.amount,
                category=item.category,
                date=today
            )
            db.session.add(expense)
            item.last_generated = today


class MonthlyStrategy(RecurringStrategy):
    def generate(self, item, user_id):
        today = datetime.now().date()
        first_of_month = today.replace(day=1)
        if not item.last_generated or item.last_generated < first_of_month:
            expense = Expense(
                user_id=user_id,
                description=item.title,
                amount=item.amount,
                category=item.category,
                date=today
            )
            db.session.add(expense)
            item.last_generated = first_of_month


class YearlyStrategy(RecurringStrategy):
    def generate(self, item, user_id):
        today = datetime.now().date()
        first_of_year = today.replace(month=1, day=1)
        if not item.last_generated or item.last_generated < first_of_year:
            expense = Expense(
                user_id=user_id,
                description=item.title,
                amount=item.amount,
                category=item.category,
                date=today
            )
            db.session.add(expense)
            item.last_generated = first_of_year


class RecurringContext:
    """Context class that executes the chosen strategy."""
    def __init__(self, strategy: RecurringStrategy):
        self.strategy = strategy

    def generate(self, item, user_id):
        self.strategy.generate(item, user_id)


# ----------------------------
# Helper: Generate all recurring expenses for a user
# ----------------------------
def generate_recurring_for_user(user_id):
    """Generates all due recurring expenses for the given user using Strategy pattern."""
    recurring_items = RecurringExpense.query.filter_by(user_id=user_id, is_active=True).all()
    for item in recurring_items:
        if item.frequency == "daily":
            strategy = DailyStrategy()
        elif item.frequency == "monthly":
            strategy = MonthlyStrategy()
        elif item.frequency == "yearly":
            strategy = YearlyStrategy()
        else:
            continue  # skip unknown frequencies

        context = RecurringContext(strategy)
        context.generate(item, user_id)

    db.session.commit()


# ----------------------------
# Route: Recurring Expenses Page
# ----------------------------
@recurring_bp.route("/", methods=["GET"])
def recurring_expenses():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    # Auto-generate recurring expenses for today
    generate_recurring_for_user(user.id)

    recurring_items = RecurringExpense.query.filter_by(user_id=user.id).all()
    return render_template("recurring_expenses.html", recurring_items=recurring_items)


# ----------------------------
# Route: Add a new recurring expense
# ----------------------------
@recurring_bp.route("/add", methods=["POST"])
def add_recurring():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    title = request.form.get("title")
    amount = request.form.get("amount")
    category = request.form.get("category")
    frequency = request.form.get("frequency")
    start_date = request.form.get("start_date")

    if not title or not amount or not frequency or not start_date:
        flash("All fields are required.", "danger")
        return redirect(url_for("recurring.recurring_expenses"))

    try:
        amount = float(amount)
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid amount or date.", "danger")
        return redirect(url_for("recurring.recurring_expenses"))

    new_item = RecurringExpense(
        user_id=user.id,
        title=title,
        amount=amount,
        category=category,
        frequency=frequency,
        start_date=start_date,
        last_generated=None,
        is_active=True
    )

    db.session.add(new_item)
    db.session.commit()
    flash("Recurring expense added.", "success")
    return redirect(url_for("recurring.recurring_expenses"))


# ----------------------------
# Route: Remove a recurring expense
# ----------------------------
@recurring_bp.route("/remove/<int:item_id>", methods=["POST"])
def remove_recurring(item_id):
    if "username" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    item = RecurringExpense.query.filter_by(id=item_id, user_id=user.id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        flash("Recurring expense removed.", "success")
    else:
        flash("Recurring expense not found.", "danger")

    return redirect(url_for("recurring.recurring_expenses"))
