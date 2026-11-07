import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse

from dependencies import get_category_service, get_expense_service, get_messaging_service
from services.category_service import CategoryService
from services.expense_service import ExpenseService
from services.messaging_service import MessagingService
from templating import templates

router = APIRouter()


@router.get("/expenses")
def show(
    request: Request,
    expense_service: Annotated[ExpenseService, Depends(get_expense_service)],
    category_service: Annotated[CategoryService, Depends(get_category_service)],
    category_id: str = "",
    month: str = "",
    text: str = "",
):
    """
    The filter form uses the method GET, so its values travel in the address:
    /expenses?category_id=2&month=2026-11&text=pizza
    category_id is received as text, because "All categories" sends an empty value.
    """
    selected_category_id = int(category_id) if category_id.isdigit() else None
    found = expense_service.get_expenses(selected_category_id, month, text)
    total = sum((e.amount for e in found), Decimal("0"))

    return templates.TemplateResponse(
        request,
        "expenses.html",
        {
            "expenses": found,
            "total": total,
            "categories": category_service.get_categories(),  # for the lists in the forms
            "category_id": selected_category_id,
            "month": month,
            "text": text,
            "today": datetime.date.today(),
        },
    )


@router.post("/expenses")
def add(
    expense_service: Annotated[ExpenseService, Depends(get_expense_service)],
    messaging_service: Annotated[MessagingService, Depends(get_messaging_service)],
    date: Annotated[datetime.date, Form()],
    amount: Annotated[Decimal, Form()],
    category_id: Annotated[int, Form()],
    description: Annotated[str, Form()] = "",
):
    """The values of the form are converted by FastAPI: the date into datetime.date, the amount into Decimal."""
    description = description.strip()

    # a friendly message here; the RESTful service checks the same rules again, and it has the last word
    if description == "" or amount <= 0:
        messaging_service.add("The expense was not added: it needs a description and an amount greater than zero.")
    elif expense_service.add(date, description, amount, category_id):
        messaging_service.add(f"Added: {description} ({amount} RSD)")

    return RedirectResponse("/expenses", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/expenses/{expense_id}/delete")
def delete(
    expense_id: int,
    expense_service: Annotated[ExpenseService, Depends(get_expense_service)],
    messaging_service: Annotated[MessagingService, Depends(get_messaging_service)],
):
    """
    An HTML form can send only GET and POST requests, so the request for deleting is a
    POST to an address that ends with /delete. The expense service then sends a real
    DELETE request to the RESTful service.
    """
    expense = expense_service.get_expense(expense_id)
    if expense is not None and expense_service.delete(expense):
        messaging_service.add(f"Deleted: {expense.description}")

    return RedirectResponse("/expenses", status_code=status.HTTP_303_SEE_OTHER)
