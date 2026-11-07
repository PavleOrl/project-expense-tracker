import datetime
from decimal import Decimal

import httpx2

from models.expense import Expense
from services.expense_service import ExpenseService
from services.messaging_service import MessagingService


def to_expense(item: dict) -> Expense:
    """Makes an Expense from one JSON object of the service (a dictionary, after response.json())."""
    return Expense(
        id=item["id"],
        date=datetime.date.fromisoformat(item["date"]),
        description=item["description"],
        amount=Decimal(item["amount"]),  # the service sends the amount as text, e.g. "990.50"
        category_id=item["category_id"],
        category_name=item["category_name"],
    )


class RestExpenseService(ExpenseService):
    """
    Obtains the expenses from the RESTful service, and sends the changes to it.

    This class is a client of the service: it sends HTTP requests with the library
    httpx2, in the same way a browser sends them - only the answers are JSON, not HTML.
    The application keeps no expenses of its own: the data lives in the service.
    """

    def __init__(self, request_uri: str, messaging_service: MessagingService):
        self._request_uri = request_uri  # the address of the resource: http://localhost:8001/api/expenses
        self._messaging_service = messaging_service

    def get_expenses(self, category_id: int | None = None, month: str = "", text: str = "") -> list[Expense]:
        # only the parameters that are given are sent: /api/expenses?category_id=2&month=2026-11
        params = {}
        if category_id is not None:
            params["category_id"] = category_id
        if month != "":
            params["month"] = month
        if text != "":
            params["text"] = text

        # sending request for reading to the server
        response = httpx2.get(self._request_uri, params=params)
        response.raise_for_status()  # an answer such as 404 or 500 becomes an exception

        # the JSON array has become a list of dictionaries; a list comprehension makes Expense objects of them
        return [to_expense(item) for item in response.json()]

    def get_expense(self, expense_id: int) -> Expense | None:
        response = httpx2.get(f"{self._request_uri}/{expense_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return to_expense(response.json())

    def add(self, date: datetime.date, description: str, amount: Decimal, category_id: int) -> bool:
        # sending request for adding to the server; the dictionary is sent as JSON
        expense_add = {
            "date": date.isoformat(),
            "description": description,
            "amount": str(amount),  # as text, so that it stays exact
            "category_id": category_id,
        }
        response = httpx2.post(self._request_uri, json=expense_add)
        return self._report(response, "add")

    def update(self, expense: Expense) -> bool:
        # sending request for updating to the server
        expense_upd = {
            "id": expense.id,
            "date": expense.date.isoformat(),
            "description": expense.description,
            "amount": str(expense.amount),
            "category_id": expense.category_id,
        }
        response = httpx2.put(f"{self._request_uri}/{expense.id}", json=expense_upd)
        return self._report(response, "update")

    def delete(self, expense: Expense) -> bool:
        # sending request for deleting to the server
        response = httpx2.delete(f"{self._request_uri}/{expense.id}")
        return self._report(response, "delete")

    def _report(self, response: httpx2.Response, operation: str) -> bool:
        """Adds a message if the service has refused the request; returns True if it has accepted it."""
        if not response.is_success:  # the status code is not 2xx
            self._messaging_service.add(
                f"ExpenseService: error in {operation} - {response.status_code} {response.text}"
            )
        return response.is_success
