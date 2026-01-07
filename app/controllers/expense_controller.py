from flask import Blueprint, render_template, request, redirect, session, url_for
from app.models.user import User
from app.services.expense_service import add_expense, get_user_expenses
from collections import defaultdict

expense_bp = Blueprint("expense", __name__)

@expense_bp.route("/expenses", methods=["GET", "POST"])
def expenses():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(username=session["username"]).first()

    if request.method == "POST":
        add_expense(
            user_id=user.id,
            description=request.form["description"],
            amount=float(request.form["amount"]),
            category=request.form.get("category") or "Uncategorized"
        )
        return redirect(url_for("expense.expenses"))

    # Fetch expenses
    expenses = get_user_expenses(user.id)

    # AGGREGATE AMOUNTS BY CATEGORY
    category_totals = defaultdict(float)
    for exp in expenses:
        category = exp.category or "Uncategorized"
        category_totals[category] += exp.amount

    category_labels = list(category_totals.keys())
    category_values = list(category_totals.values())

    return render_template(
        "expenses.html",
        username=user.username,
        expenses=expenses,
        category_labels=category_labels,
        category_values=category_values
    )
