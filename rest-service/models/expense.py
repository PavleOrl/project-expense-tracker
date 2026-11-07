import datetime
from decimal import Decimal

from sqlmodel import Field, Relationship, SQLModel

from models.category import Category


class Expense(SQLModel, table=True):
    """One object of this class is one row of the table expense."""

    expense_id: int | None = Field(default=None, primary_key=True)

    date: datetime.date = Field(index=True)  # an index makes searching by date faster

    description: str = Field(max_length=255)

    # a Decimal, not a float: money must be exact; 12 digits, 2 of them after the decimal point
    amount: Decimal = Field(max_digits=12, decimal_places=2)

    # the foreign key: every expense belongs to one category
    category_id: int = Field(foreign_key="category.category_id")

    # Not a column: the object of the class Category to which category_id refers.
    # It is read from the table category when it is used for the first time.
    category: Category = Relationship()
