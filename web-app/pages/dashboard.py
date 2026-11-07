import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from dependencies import get_category_service, get_expense_service
from services.category_service import CategoryService
from services.expense_service import ExpenseService
from templating import templates

router = APIRouter()


def shift_month(month: str, delta: int) -> str:
    """Returns the month that is delta months before (-1) or after (+1) the given one: "2026-11", -1 -> "2026-10"."""
    year, number = int(month[:4]), int(month[5:])
    # months are counted from 0 here, so that // and % can carry over into the next or previous year
    index = year * 12 + (number - 1) + delta
    return f"{index // 12}-{index % 12 + 1:02d}"


@router.get("/dashboard")
def show(
    request: Request,
    expense_service: Annotated[ExpenseService, Depends(get_expense_service)],
    category_service: Annotated[CategoryService, Depends(get_category_service)],
    month: str = "",
):
    """The parameter month comes from the address: /dashboard?month=2026-10 (without it - the current month)."""
    if month == "":
        month = datetime.date.today().strftime("%Y-%m")

    month_expenses = expense_service.get_expenses(month=month)  # the service filters, not this page
    total = sum((e.amount for e in month_expenses), Decimal("0"))
    totals = expense_service.totals_by_category(month_expenses)
    # max() with key= finds the expense with the largest amount; default=None when the month is empty
    largest = max(month_expenses, key=lambda e: e.amount, default=None)
    latest = expense_service.get_expenses()[:5]  # the five newest expenses of all

    # one row for every category that has a budget or has been spent on: spent against budget
    budget_rows = []
    for category in category_service.get_categories():
        spent = totals.get(category.name, Decimal("0"))
        if spent == 0 and category.monthly_budget == 0:
            continue
        budget_rows.append(
            {
                "category": category,
                "spent": spent,
                "budget": category.monthly_budget,
                # the share of the budget that has been spent (None when the category has no budget)
                "percent": round(spent / category.monthly_budget * 100) if category.monthly_budget > 0 else None,
            }
        )
    # the categories that have used the largest share of their budget first
    budget_rows.sort(key=lambda row: row["percent"] if row["percent"] is not None else -1, reverse=True)

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "month": month,
            "previous_month": shift_month(month, -1),
            "next_month": shift_month(month, 1),
            "total": total,
            "count": len(month_expenses),
            "largest": largest,
            "budget_rows": budget_rows,
            "latest": latest,
        },
    )
