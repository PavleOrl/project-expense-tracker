from abc import ABC, abstractmethod
from decimal import Decimal

from models.category import Category


class CategoryService(ABC):
    """
    What a page may ask for when it needs categories.

    The methods that change the data return True if the change has been carried out,
    and False if it has been refused.
    """

    @abstractmethod
    def get_categories(self) -> list[Category]:
        """Returns all the categories, ordered by name."""

    @abstractmethod
    def add(self, name: str, monthly_budget: Decimal) -> bool:
        """Adds a new category."""

    @abstractmethod
    def update(self, category: Category) -> bool:
        """Stores the changed data of the category."""

    @abstractmethod
    def delete(self, category: Category) -> bool:
        """Removes the category."""
