from app.models.user import User
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

def register_user(data):
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(username=username).first():
        return {"success": False, "error": "Username already exists"}

    if User.query.filter_by(email=email).first():
        return {"success": False, "error": "Email already exists"}

    new_user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )

    db.session.add(new_user)
    db.session.commit()

    return {"success": True}

def login_user(data):
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password):
        return {"success": False, "error": "Invalid credentials"}

    return {"success": True}

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def update_user(username, new_email=None, new_password=None,
                daily_limit=None, monthly_limit=None, yearly_limit=None):
    user = User.query.filter_by(username=username).first()
    if not user:
        return {"success": False, "message": "User not found."}

    # Update fields if provided
    if new_email:
        user.email = new_email
    if new_password:
        user.password_hash = generate_password_hash(new_password)
    if daily_limit is not None:
        user.daily_limit = daily_limit
    if monthly_limit is not None:
        user.monthly_limit = monthly_limit
    if yearly_limit is not None:
        user.yearly_limit = yearly_limit

    try:
        db.session.commit()
        return {"success": True, "message": "Profile updated successfully."}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": f"Error updating profile: {str(e)}"}
