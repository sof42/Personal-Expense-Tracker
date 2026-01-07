from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services.user_service import login_user, register_user, update_user, get_user_by_username
from app.models.user import User
from app.models.expense import Expense
from sqlalchemy import func
from datetime import datetime
from app.extensions import db

auth_bp = Blueprint("auth", __name__)

# Landing page
@auth_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Login route
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        result = login_user(request.form)
        if result["success"]:
            session["username"] = request.form.get("username")
            return redirect(url_for("auth.dashboard"))
        return result["error"], 400
    return render_template("login.html")

# Register route
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        result = register_user(request.form)
        if result["success"]:
            return redirect(url_for("auth.login"))
        return result["error"], 400
    return render_template("register.html")

# Dashboard route (GET only)
@auth_bp.route("/dashboard", methods=["GET"])
def dashboard():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    # Fetch recent expenses (latest 5)
    recent_expenses = Expense.query.filter_by(user_id=user.id).order_by(Expense.date.desc()).limit(5).all()

    # Compute spent amounts
    today = datetime.utcnow().date()
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)

    daily_spent = db.session.query(func.coalesce(func.sum(Expense.amount), 0)) \
        .filter(Expense.user_id == user.id, func.date(Expense.date) == today).scalar()

    monthly_spent = db.session.query(func.coalesce(func.sum(Expense.amount), 0)) \
        .filter(Expense.user_id == user.id, Expense.date >= start_of_month).scalar()

    yearly_spent = db.session.query(func.coalesce(func.sum(Expense.amount), 0)) \
        .filter(Expense.user_id == user.id, Expense.date >= start_of_year).scalar()

    return render_template(
        "dashboard.html",
        username=user.username,
        recent_expenses=recent_expenses,
        daily_limit=user.daily_limit,
        monthly_limit=user.monthly_limit,
        yearly_limit=user.yearly_limit,
        daily_spent=daily_spent,
        monthly_spent=monthly_spent,
        yearly_spent=yearly_spent
    )

@auth_bp.route("/profile", methods=["GET", "POST"])
def profile():
    # Ensure user is logged in
    if "username" not in session:
        return redirect(url_for("auth.login"))

    username = session["username"]
    user = get_user_by_username(username)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("auth.logout"))

    # Handle updates via simulated PUT
    if request.method == "POST" and request.form.get("_method") == "PUT":
        # Email and password
        new_email = request.form.get("email") or user.email
        new_password = request.form.get("password") or None  # None = don't change

        # Limits: safely convert to float, fall back to existing values
        try:
            new_daily_limit = float(request.form.get("daily_limit") or user.daily_limit or 0)
            new_monthly_limit = float(request.form.get("monthly_limit") or user.monthly_limit or 0)
            new_yearly_limit = float(request.form.get("yearly_limit") or user.yearly_limit or 0)
        except ValueError:
            flash("Limits must be valid numbers.", "danger")
            return redirect(url_for("auth.profile"))

        # Update user in the database
        result = update_user(
            username,
            new_email=new_email,
            new_password=new_password,
            daily_limit=new_daily_limit,
            monthly_limit=new_monthly_limit,
            yearly_limit=new_yearly_limit
        )

        # Show success or error message
        flash(result["message"], "success" if result["success"] else "danger")
        return redirect(url_for("auth.profile"))

    # GET request: render profile with current values
    return render_template(
        "profile.html",
        username=user.username,
        email=user.email,
        daily_limit=user.daily_limit,
        monthly_limit=user.monthly_limit,
        yearly_limit=user.yearly_limit
    )

# Logout route
@auth_bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
