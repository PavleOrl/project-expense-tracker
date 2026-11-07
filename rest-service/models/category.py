from decimal import Decimal

from sqlmodel import Field, SQLModel


class Category(SQLModel, table=True):
    """One object of this class is one row of the table category."""

    category_id: int | None = Field(default=None, primary_key=True)

    # unique: two categories can not have the same name - the database refuses it
    name: str = Field(max_length=100, unique=True)

    # how much may be spent in this category in one month; 0 means "no budget"
    monthly_budget: Decimal = Field(default=Decimal("0"), max_digits=12, decimal_places=2)
