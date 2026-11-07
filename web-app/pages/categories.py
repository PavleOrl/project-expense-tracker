from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse

from dependencies import get_category_service, get_messaging_service
from models.category import Category
from services.category_service import CategoryService
from services.messaging_service import MessagingService
from templating import templates

router = APIRouter()


def find_category(category_service: CategoryService, category_id: int) -> Category | None:
    for category in category_service.get_categories():
        if category.id == category_id:
            return category
    return None


@router.get("/categories")
def show(
    request: Request,
    category_service: Annotated[CategoryService, Depends(get_category_service)],
):
    categories = category_service.get_categories()

    return templates.TemplateResponse(request, "categories.html", {"categories": categories})


@router.post("/categories")
def add(
    category_service: Annotated[CategoryService, Depends(get_category_service)],
    messaging_service: Annotated[MessagingService, Depends(get_messaging_service)],
    name: Annotated[str, Form()] = "",
    monthly_budget: Annotated[Decimal, Form()] = Decimal("0"),
):
    # the RESTful service refuses an empty name, a negative budget, and a name that already exists
    if category_service.add(name.strip(), monthly_budget):
        messaging_service.add(f"Category added: {name}")

    return RedirectResponse("/categories", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/categories/{category_id}")
def save(
    category_id: int,
    category_service: Annotated[CategoryService, Depends(get_category_service)],
    messaging_service: Annotated[MessagingService, Depends(get_messaging_service)],
    name: Annotated[str, Form()] = "",
    monthly_budget: Annotated[Decimal, Form()] = Decimal("0"),
):
    """Every row of the table is a small form of its own: it changes the name and the budget of one category."""
    category = find_category(category_service, category_id)
    if category is not None:
        category.name = name.strip()
        category.monthly_budget = monthly_budget
        if category_service.update(category):
            messaging_service.add(f"Category saved: {category.name}")

    return RedirectResponse("/categories", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/categories/{category_id}/delete")
def delete(
    category_id: int,
    category_service: Annotated[CategoryService, Depends(get_category_service)],
    messaging_service: Annotated[MessagingService, Depends(get_messaging_service)],
):
    category = find_category(category_service, category_id)
    # the RESTful service refuses to delete a category that still has expenses
    if category is not None and category_service.delete(category):
        messaging_service.add(f"Category deleted: {category.name}")

    return RedirectResponse("/categories", status_code=status.HTTP_303_SEE_OTHER)
