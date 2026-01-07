# app/models.py
import uuid
from datetime import datetime
from app.extensions import db

class Expense(db.Model):
    __tablename__ = "expenses"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("expenses", lazy=True))

    def __repr__(self):
        return f"<Expense {self.description} - {self.amount}>"
