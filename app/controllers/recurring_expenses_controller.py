from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
from app.extensions import db
from app.models.recurring_expenses import RecurringExpense
from app.models.expense import Expense
from app.models.user import User

recurring_bp = Blueprint("recurring", __name__, url_prefix="/recurring")


# ----------------------------
# Helper: Generate recurring expenses for a user
# ----------------------------
def generate_recurring_for_user(user_id):
    today = datetime.now().date()
    recurring_items = RecurringExpense.query.filter_by(user_id=user_id, is_active=True).all()

    for item in recurring_items:
        # Check if the expense should be generated today
        if not item.last_generated or item.last_generated < today:
            # Create a new Expense
            new_expense = Expense(
                user_id=user_id,
                description=item.title,
                amount=item.amount,
                category=item.category,
                date=today
            )
            db.session.add(new_expense)

            # Update last_generated based on frequency
            if item.frequency == "daily":
                item.last_generated = today
            elif item.frequency == "monthly":
                item.last_generated = today.replace(day=1)
            elif item.frequency == "yearly":
                item.last_generated = today.replace(month=1, day=1)
            else:
                item.last_generated = today  # fallback

    db.session.commit()


# ----------------------------
# View: Recurring Expenses Page
# ----------------------------
@recurring_bp.route("/", methods=["GET"])
def recurring_expenses():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    # Generate recurring expenses automatically for today
    generate_recurring_for_user(user.id)

    recurring_items = RecurringExpense.query.filter_by(user_id=user.id).all()
    return render_template("recurring_expenses.html", recurring_items=recurring_items)


# ----------------------------
# Add a new recurring expense
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
    frequency = request.form.get("frequency")  # daily, monthly, yearly
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
# Remove a recurring expense
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
