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
