from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from database import get_category_repository, get_expense_repository
from dtos.expense_dto import ExpenseDTO
from repositories.category_repository import CategoryRepository
from repositories.expense_repository import ExpenseRepository

router = APIRouter(prefix="/api/expenses", tags=["expenses"])

# the repositories are handed over by FastAPI (dependency injection)
ExpenseRepo = Annotated[ExpenseRepository, Depends(get_expense_repository)]
CategoryRepo = Annotated[CategoryRepository, Depends(get_category_repository)]


def check_category(category_repo: CategoryRepository, category_id: int) -> None:
    """An expense can belong only to a category that exists."""
    if category_repo.get_by_id(category_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"There is no category with the id {category_id}",
        )


@router.get("")
def get_all(
    expense_repo: ExpenseRepo,
    category_id: int | None = None,
    # pattern: the month must look like 2026-11 (four digits, a dash, two digits)
    month: Annotated[str, Query(pattern=r"^(\d{4}-\d{2})?$")] = "",
    text: str = "",
) -> list[ExpenseDTO]:
    """
    All the expenses, the newest first. The parameters in the address narrow the list:
    /api/expenses?category_id=2&month=2026-11&text=pizza
    """
    return expense_repo.get_all(category_id, month, text)


@router.get("/{id}")
def get_by_id(id: int, expense_repo: ExpenseRepo) -> ExpenseDTO:
    expense = expense_repo.get_by_id(id)
    if expense is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return expense


@router.post("", status_code=status.HTTP_201_CREATED)
def create(
    model: ExpenseDTO, expense_repo: ExpenseRepo, category_repo: CategoryRepo, response: Response
) -> ExpenseDTO:
    check_category(category_repo, model.category_id)
    expense = expense_repo.create(model)

    response.headers["Location"] = f"/api/expenses/{expense.id}"
    return expense


@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def update(id: int, model: ExpenseDTO, expense_repo: ExpenseRepo, category_repo: CategoryRepo) -> None:
    if id != model.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The id in the address and the id in the body are different",
        )
    check_category(category_repo, model.category_id)

    if not expense_repo.update(model):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(id: int, expense_repo: ExpenseRepo) -> None:
    if not expense_repo.delete(id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
