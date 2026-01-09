# app/models/recurring_expense.py
import uuid
from datetime import date
from app.extensions import db

class RecurringExpense(db.Model):
    __tablename__ = "recurring_expenses"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)

    title = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(50))

    frequency = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly, yearly
    start_date = db.Column(db.Date, nullable=False)

    last_generated = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship("User", backref="recurring_expenses")

    def __repr__(self):
        return f"<RecurringExpense {self.title} ({self.frequency})>"
