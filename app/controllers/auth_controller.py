from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services.user_service import login_user, register_user, update_user, get_user_by_username
from app.models.user import User
from app.models.expense import Expense
from app.models.recurring_expenses import RecurringExpense
from sqlalchemy import func
from datetime import datetime, timedelta
from app.extensions import db

auth_bp = Blueprint("auth", __name__)

# ---------------- Landing Page ----------------
@auth_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# ---------------- Login ----------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        result = login_user(request.form)
        if result["success"]:
            session["username"] = request.form.get("username")
            return redirect(url_for("auth.dashboard"))
        flash(result.get("error", "Login failed"), "danger")
        return redirect(url_for("auth.login"))
    return render_template("login.html")


# ---------------- Register ----------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        result = register_user(request.form)
        if result["success"]:
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))
        flash(result.get("error", "Registration failed"), "danger")
        return redirect(url_for("auth.register"))
    return render_template("register.html")


# ---------------- Dashboard ----------------
@auth_bp.route("/dashboard", methods=["GET"])
def dashboard():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    # ---------- Generate Recurring Expenses ----------
    today = datetime.now().date()
    recurring_expenses = RecurringExpense.query.filter_by(user_id=user.id).all()

    for recur in recurring_expenses:
        # Determine last generated date
        last_date = recur.last_generated or recur.start_date
        current_date = last_date + timedelta(days=1)

        # Generate expenses according to frequency
        while current_date <= today:
            generate = False
            if recur.frequency == "daily":
                generate = True
            elif recur.frequency == "weekly" and current_date.weekday() == last_date.weekday():
                generate = True
            elif recur.frequency == "monthly" and current_date.day == recur.start_date.day:
                generate = True
            elif recur.frequency == "yearly" and current_date.month == recur.start_date.month and current_date.day == recur.start_date.day:
                generate = True

            if generate:
                # Avoid duplicates
                exists = Expense.query.filter_by(user_id=user.id, description=recur.title, date=current_date).first()
                if not exists:
                    new_expense = Expense(
                        user_id=user.id,
                        description=recur.title,
                        amount=recur.amount,
                        category=recur.category,
                        date=current_date
                    )
                    db.session.add(new_expense)

                # Update last_generated
                recur.last_generated = current_date

            # Move to next day
            current_date += timedelta(days=1)

    db.session.commit()

    # ---------- Recent Expenses ----------
    recent_expenses = Expense.query.filter_by(user_id=user.id) \
        .order_by(Expense.date.desc()) \
        .limit(5) \
        .all()

    # ---------- Spent Amounts ----------
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)

    daily_spent = db.session.query(func.coalesce(func.sum(Expense.amount), 0)) \
        .filter(Expense.user_id == user.id, func.date(Expense.date) == today).scalar()

    monthly_spent = db.session.query(func.coalesce(func.sum(Expense.amount), 0)) \
        .filter(Expense.user_id == user.id, Expense.date >= start_of_month).scalar()

    yearly_spent = db.session.query(func.coalesce(func.sum(Expense.amount), 0)) \
        .filter(Expense.user_id == user.id, Expense.date >= start_of_year).scalar()

    # ---------- Percentages ----------
    def calc_pct(spent, limit):
        if limit and limit > 0:
            return min(int((spent / limit) * 100), 100)
        return 0

    daily_pct = calc_pct(daily_spent, user.daily_limit)
    monthly_pct = calc_pct(monthly_spent, user.monthly_limit)
    yearly_pct = calc_pct(yearly_spent, user.yearly_limit)

    return render_template(
        "dashboard.html",
        username=user.username,
        recent_expenses=recent_expenses,

        daily_limit=user.daily_limit,
        monthly_limit=user.monthly_limit,
        yearly_limit=user.yearly_limit,

        daily_spent=daily_spent,
        monthly_spent=monthly_spent,
        yearly_spent=yearly_spent,

        daily_pct=daily_pct,
        monthly_pct=monthly_pct,
        yearly_pct=yearly_pct
    )


# ---------------- Profile ----------------
@auth_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    username = session["username"]
    user = get_user_by_username(username)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("auth.logout"))

    if request.method == "POST" and request.form.get("_method") == "PUT":
        # Email & Password
        new_email = request.form.get("email") or user.email
        new_password = request.form.get("password") or None

        try:
            new_daily_limit = float(request.form.get("daily_limit") or user.daily_limit or 0)
            new_monthly_limit = float(request.form.get("monthly_limit") or user.monthly_limit or 0)
            new_yearly_limit = float(request.form.get("yearly_limit") or user.yearly_limit or 0)
        except ValueError:
            flash("Limits must be valid numbers.", "danger")
            return redirect(url_for("auth.profile"))

        result = update_user(
            username,
            new_email=new_email,
            new_password=new_password,
            daily_limit=new_daily_limit,
            monthly_limit=new_monthly_limit,
            yearly_limit=new_yearly_limit
        )

        flash(result["message"], "success" if result["success"] else "danger")
        return redirect(url_for("auth.profile"))

    return render_template(
        "profile.html",
        username=user.username,
        email=user.email,
        daily_limit=user.daily_limit,
        monthly_limit=user.monthly_limit,
        yearly_limit=user.yearly_limit
    )


# ---------------- Recurring Expenses Management ----------------
@auth_bp.route("/recurring", methods=["GET", "POST"])
def recurring():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        flash("User not found", "danger")
        return redirect(url_for("auth.logout"))

    if request.method == "POST":
        title = request.form.get("title")
        amount = float(request.form.get("amount"))
        category = request.form.get("category") or ""
        frequency = request.form.get("frequency")
        start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date()

        new_recur = RecurringExpense(
            user_id=user.id,
            title=title,
            amount=amount,
            category=category,
            frequency=frequency,
            start_date=start_date
        )
        db.session.add(new_recur)
        db.session.commit()
        flash("Recurring expense added!", "success")
        return redirect(url_for("auth.recurring"))

    recurring_list = RecurringExpense.query.filter_by(user_id=user.id).all()
    return render_template("recurring.html", recurring_list=recurring_list)


# ---------------- Logout ----------------
@auth_bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))
