# Personal Expense Tracker

A web-based application for tracking personal expenses, including recurring expenses, budget limits, and financial overviews. Built with **Flask**, **SQLAlchemy**, **PostgreSQL**, and **Bootstrap**, following **MVC architecture** and the **Strategy design pattern** for recurring expense generation.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Database Schema](#database-schema)
- [Design Patterns](#design-patterns)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Features

- User registration, login, and profile management
- Add, remove, and view **one-time expenses**
- Manage **recurring expenses** with daily, monthly, and yearly recurrence
- Automatic generation of recurring expenses
- Dashboard with **daily, monthly, and yearly spending progress bars**
- Secure password storage using hashing
- Modular backend with service layer for business logic

---

## Installation

### Prerequisites

- Python 3.10+
- PostgreSQL 13+
- `pip` (Python package manager)
- `virtualenv` (optional but recommended)

### Setup Steps

1. Clone the repository:

```bash
git clone https://github.com/yourusername/personal-expense-tracker.git
cd personal-expense-tracker
```

2. Create a virtual environment (optional):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment details in a .env file
```bash
DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/expense_tracker
SECRET_KEY=your-secret-key
```

5. Initialize the database
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application
```bash
python3 run.py
```

## Usage

- Register a new user or log in with existing credentials
- Add one-time expenses through the **Expenses** page
- Add recurring expenses through the **Recurring Expenses** page
- View the dashboard for a quick summary of daily, monthly, and yearly spending
- Remove recurring or one-time expenses as needed

---

## Database Schema

The system uses PostgreSQL with the following tables:

- `users`: Stores authentication and profile data, including username, email, password hash, and spending limits (daily, monthly, yearly)
- `expenses`: Stores individual expense entries linked to users, including description, amount, category, and date
- `recurring_expenses`: Stores recurring expense templates with title, amount, category, frequency (daily, monthly, yearly), start date, last generated date, and active status

**Relationships:**

- `users` → `expenses` (1:N): Each user can have multiple expenses
- `users` → `recurring_expenses` (1:N): Each user can have multiple recurring expense templates

---

## Design Patterns

- **MVC (Model-View-Controller)**: Separates data, logic, and presentation to improve maintainability and scalability
- **Strategy Pattern**: Allows different recurring expense generation strategies (daily, monthly, yearly) to be applied without modifying controller logic

---

## Future Improvements

- Support more complex recurring expense rules (e.g., every 2 weeks, specific weekdays)
- Add caching and background task processing for recurring expense generation
- Provide analytics and visualizations of spending trends
- Add notifications and alerts for budget limits
- Integrate with external financial services or APIs
