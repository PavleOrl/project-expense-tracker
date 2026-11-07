"""
The connection with the database, and the repositories.

The database is the SQLite file expenses.db in this folder. It is created, with a few
categories and expenses in it, the first time the service is started. To start again
from scratch, stop the service and delete the file.
"""

import datetime
from decimal import Decimal
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine, select

from models.category import Category
from models.expense import Expense
from repositories.category_repository import CategoryRepository
from repositories.expense_repository import ExpenseRepository

DATABASE_FILE = Path(__file__).parent / "expenses.db"

# The engine knows where the database is, and how to talk to it.
engine = create_engine(f"sqlite:///{DATABASE_FILE}")


@event.listens_for(engine, "connect")
def switch_on_foreign_keys(connection, connection_record):
    """SQLite checks foreign keys only if it is asked to, on every new connection."""
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


def get_session():
    """Hands over a session - a conversation with the database - and closes it afterwards."""
    with Session(engine) as session:
        yield session


def get_category_repository(session: Annotated[Session, Depends(get_session)]) -> CategoryRepository:
    """A repository needs a session; FastAPI obtains it first, from get_session()."""
    return CategoryRepository(session)


def get_expense_repository(session: Annotated[Session, Depends(get_session)]) -> ExpenseRepository:
    return ExpenseRepository(session)


def create_database() -> None:
    """Creates the tables (if they do not exist), and fills the empty tables with data."""
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        if session.exec(select(Category)).first() is not None:
            return  # there is data already

        food = Category(name="Food", monthly_budget=Decimal("18000"))
        transport = Category(name="Transport", monthly_budget=Decimal("4000"))
        housing = Category(name="Housing", monthly_budget=Decimal("35000"))
        bills = Category(name="Bills", monthly_budget=Decimal("8000"))
        health = Category(name="Health", monthly_budget=Decimal("3000"))
        education = Category(name="Education", monthly_budget=Decimal("5000"))
        fun = Category(name="Fun", monthly_budget=Decimal("4000"))
        clothes = Category(name="Clothes", monthly_budget=Decimal("6000"))
        other = Category(name="Other")
        session.add_all([food, transport, housing, bills, health, education, fun, clothes, other])
        session.commit()  # after the commit every category has its category_id

        d = datetime.date
        session.add_all(
            [
                Expense(date=d(2026, 10, 1), description="Rent for October", amount=Decimal("35000.00"), category_id=housing.category_id),
                Expense(date=d(2026, 10, 2), description="Monthly bus pass", amount=Decimal("2600.00"), category_id=transport.category_id),
                Expense(date=d(2026, 10, 3), description="Supermarket - weekly shopping", amount=Decimal("4870.50"), category_id=food.category_id),
                Expense(date=d(2026, 10, 5), description="Textbook: Software Engineering", amount=Decimal("3200.00"), category_id=education.category_id),
                Expense(date=d(2026, 10, 7), description="Electricity bill", amount=Decimal("3150.75"), category_id=bills.category_id),
                Expense(date=d(2026, 10, 8), description="Lunch with friends", amount=Decimal("1450.00"), category_id=food.category_id),
                Expense(date=d(2026, 10, 10), description="Cinema", amount=Decimal("750.00"), category_id=fun.category_id),
                Expense(date=d(2026, 10, 11), description="Supermarket - weekly shopping", amount=Decimal("5120.30"), category_id=food.category_id),
                Expense(date=d(2026, 10, 14), description="Mobile phone bill", amount=Decimal("1999.00"), category_id=bills.category_id),
                Expense(date=d(2026, 10, 16), description="Pharmacy - vitamins", amount=Decimal("1280.00"), category_id=health.category_id),
                Expense(date=d(2026, 10, 18), description="Winter jacket", amount=Decimal("8990.00"), category_id=clothes.category_id),
                Expense(date=d(2026, 10, 19), description="Supermarket - weekly shopping", amount=Decimal("4430.80"), category_id=food.category_id),
                Expense(date=d(2026, 10, 22), description="Football match ticket", amount=Decimal("1200.00"), category_id=fun.category_id),
                Expense(date=d(2026, 10, 25), description="Taxi home", amount=Decimal("890.00"), category_id=transport.category_id),
                Expense(date=d(2026, 10, 27), description="Pizza delivery", amount=Decimal("1650.00"), category_id=food.category_id),
                Expense(date=d(2026, 10, 30), description="Internet bill", amount=Decimal("2490.00"), category_id=bills.category_id),
                Expense(date=d(2026, 11, 1), description="Rent for November", amount=Decimal("35000.00"), category_id=housing.category_id),
                Expense(date=d(2026, 11, 1), description="Monthly bus pass", amount=Decimal("2600.00"), category_id=transport.category_id),
                Expense(date=d(2026, 11, 1), description="Coffee and croissant", amount=Decimal("420.00"), category_id=food.category_id),
            ]
        )
        session.commit()
