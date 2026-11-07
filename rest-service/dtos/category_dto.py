from decimal import Decimal

from pydantic import BaseModel, Field


class CategoryDTO(BaseModel):
    """
    The data about a category as the clients of the service see it.

    Field(...) adds rules that FastAPI checks before our code is called:
    a request that breaks them is answered with 422 Unprocessable Content.
    """

    id: int | None = None
    name: str = Field(min_length=1, max_length=100)
    monthly_budget: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)
