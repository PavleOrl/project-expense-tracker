import datetime
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Expense:
    """
    The data about one expense, as the RESTful service sends it.

    The amount is a Decimal, not a float: money must be exact (0.1 + 0.2 is not exactly 0.3 with floats).
    """

    id: int
    date: datetime.date
    description: str
    amount: Decimal
    category_id: int
    category_name: str

    def month(self) -> str:
        """The month of the expense as text, for example "2026-11" (the format of <input type="month">)."""
        return self.date.strftime("%Y-%m")
