import datetime
from abc import ABC, abstractmethod
from decimal import Decimal

from models.expense import Expense


class ExpenseService(ABC):
    """
    What a page may ask for when it needs expenses.

    This class only says WHAT can be done (it is an abstract class, an "interface").
    HOW it is done is written in a class that inherits from it - see RestExpenseService.
    Compare it with Homework 2: there the expenses came from a file (FileExpenseService),
    here they come from the RESTful service - and the pages hardly had to change.

    The methods that change the data return True if the change has been carried out,
    and False if it has been refused.
    """

    @abstractmethod
    def get_expenses(self, category_id: int | None = None, month: str = "", text: str = "") -> list[Expense]:
        """
        Returns the expenses, the newest first: only those of the given category,
        in the given month ("2026-11"), whose description contains the given text.
        An empty value means "any".
        """

    @abstractmethod
    def get_expense(self, expense_id: int) -> Expense | None:
        """Returns the expense with the given id, or None if there is no such expense."""

    @abstractmethod
    def add(self, date: datetime.date, description: str, amount: Decimal, category_id: int) -> bool:
        """Adds a new expense."""

    @abstractmethod
    def update(self, expense: Expense) -> bool:
        """Stores the changed data of the expense."""

    @abstractmethod
    def delete(self, expense: Expense) -> bool:
        """Removes the expense."""

    def totals_by_category(self, expenses: list[Expense]) -> dict[str, Decimal]:
        """
        Adds up the amounts of the given expenses per category name.

        This method is not abstract: it is written once, here, and every class
        that inherits from ExpenseService gets it for free.
        """
        totals: dict[str, Decimal] = {}
        for expense in expenses:
            totals[expense.category_name] = totals.get(expense.category_name, Decimal("0")) + expense.amount
        return totals
