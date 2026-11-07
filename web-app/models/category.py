from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Category:
    """The data about one category, as the RESTful service sends it."""

    id: int
    name: str
    monthly_budget: Decimal  # how much may be spent in one month; 0 means "no budget"
