import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ExpenseDTO(BaseModel):
    """
    The data about an expense as the clients of the service see it (a data transfer object).

    It does not look like a row of the table expense: next to the key category_id
    it also carries the name of the category, taken from the table category.
    When a client sends an ExpenseDTO (to add or to change an expense), only category_id
    is used - the name of the category is ignored.
    """

    id: int | None = None
    date: datetime.date
    description: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)  # gt=0: greater than zero
    category_id: int
    category_name: str | None = None
