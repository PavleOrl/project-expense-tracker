from decimal import Decimal

import httpx2

from models.category import Category
from services.category_service import CategoryService
from services.messaging_service import MessagingService


class RestCategoryService(CategoryService):
    """Obtains the categories from the RESTful service, and sends the changes to it."""

    def __init__(self, request_uri: str, messaging_service: MessagingService):
        self._request_uri = request_uri  # the address of the resource: http://localhost:8001/api/categories
        self._messaging_service = messaging_service

    def get_categories(self) -> list[Category]:
        # sending request for reading to the server
        response = httpx2.get(self._request_uri)
        response.raise_for_status()

        categories = []
        for item in response.json():
            categories.append(
                Category(id=item["id"], name=item["name"], monthly_budget=Decimal(item["monthly_budget"]))
            )
        return categories

    def add(self, name: str, monthly_budget: Decimal) -> bool:
        # sending request for adding to the server
        category_add = {"name": name, "monthly_budget": str(monthly_budget)}
        response = httpx2.post(self._request_uri, json=category_add)
        return self._report(response, "add")

    def update(self, category: Category) -> bool:
        # sending request for updating to the server
        category_upd = {"id": category.id, "name": category.name, "monthly_budget": str(category.monthly_budget)}
        response = httpx2.put(f"{self._request_uri}/{category.id}", json=category_upd)
        return self._report(response, "update")

    def delete(self, category: Category) -> bool:
        # sending request for deleting to the server
        response = httpx2.delete(f"{self._request_uri}/{category.id}")
        return self._report(response, "delete")

    def _report(self, response: httpx2.Response, operation: str) -> bool:
        """Adds a message if the service has refused the request; returns True if it has accepted it."""
        if not response.is_success:
            self._messaging_service.add(
                f"CategoryService: error in {operation} - {response.status_code} {response.text}"
            )
        return response.is_success
