"""
The services of the application, and the functions that hand them over.

Compare this file with the one in Homework 2: there the expenses came from a file
(FileExpenseService), here they come from the RESTful service (RestExpenseService).
The pages know only the abstract classes ExpenseService and CategoryService.
"""

import os

from services.category_service import CategoryService
from services.expense_service import ExpenseService
from services.messaging_service import MessagingService
from services.rest_category_service import RestCategoryService
from services.rest_expense_service import RestExpenseService

# the address of the RESTful service (it can be changed with an environment variable)
REST_SERVICE_URL = os.environ.get("REST_SERVICE_URL", "http://localhost:8001/api")


def write_message_to_console(messages: list[str]) -> None:
    """A listener: it is called by the messaging service whenever the messages change."""
    if messages:
        print("Message:", messages[-1])  # the last message of the list


# one object of each service for the whole application
_messaging_service = MessagingService()
_messaging_service.on_messages_changed.append(write_message_to_console)

_expense_service = RestExpenseService(REST_SERVICE_URL + "/expenses", _messaging_service)
_category_service = RestCategoryService(REST_SERVICE_URL + "/categories", _messaging_service)


def get_messaging_service() -> MessagingService:
    return _messaging_service


def get_expense_service() -> ExpenseService:
    return _expense_service


def get_category_service() -> CategoryService:
    return _category_service
