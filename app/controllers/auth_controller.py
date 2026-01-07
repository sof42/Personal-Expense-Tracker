from flask import Blueprint, render_template, request, redirect, url_for, session
from app.services.user_service import login_user, register_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def index():
    # Always show the landing page, regardless of login status
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

# Dashboard route (only for logged-in users)
@auth_bp.route("/dashboard")
def dashboard():
    if "username" not in session:
        # Only redirect to login if NOT logged in
        return redirect(url_for("auth.login"))
    return render_template("dashboard.html", username=session["username"])

# Profile route
@auth_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if "username" not in session:
        return redirect(url_for("auth.login"))
    
    username = session["username"]

    if request.method == "POST":
        # can handle updating email/password later
        # For now, just a placeholder
        new_email = request.form.get("email")
        new_password = request.form.get("password")
        # Call user_service.update_user(username, new_email, new_password)
        # For now, just print to console to check
        print(f"Update for {username}: email={new_email}, password={new_password}")
        return redirect(url_for("auth.profile"))

    return render_template("profile.html", username=username)

# Logout
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
