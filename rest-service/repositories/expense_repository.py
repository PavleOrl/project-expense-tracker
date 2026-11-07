import datetime

from sqlmodel import Session, select

from dtos.expense_dto import ExpenseDTO
from models.expense import Expense


def to_dto(expense: Expense) -> ExpenseDTO:
    """Makes the object that is sent to the clients from a row of the table (and its category)."""
    return ExpenseDTO(
        id=expense.expense_id,
        date=expense.date,
        description=expense.description,
        amount=expense.amount,
        category_id=expense.category.category_id,
        category_name=expense.category.name,
    )


def month_range(month: str) -> tuple[datetime.date, datetime.date]:
    """The first day of the month "2026-11", and the first day of the next month."""
    first = datetime.date.fromisoformat(month + "-01")
    if first.month == 12:
        next_first = datetime.date(first.year + 1, 1, 1)
    else:
        next_first = datetime.date(first.year, first.month + 1, 1)
    return first, next_first


class ExpenseRepository:
    """Reads and writes the table expense. The rest of the service sees only ExpenseDTO objects."""

    def __init__(self, session: Session):
        self._session = session

    def get_all(self, category_id: int | None = None, month: str = "", text: str = "") -> list[ExpenseDTO]:
        """
        Returns the expenses, the newest first. Every parameter that is given narrows the result;
        the statement is built step by step, and becomes, for example:

            SELECT * FROM expense
            WHERE category_id = 2 AND date >= '2026-11-01' AND date < '2026-12-01'
            ORDER BY date DESC, expense_id DESC
        """
        statement = select(Expense)
        if category_id is not None:
            statement = statement.where(Expense.category_id == category_id)
        if month != "":
            first, next_first = month_range(month)
            statement = statement.where(Expense.date >= first, Expense.date < next_first)
        if text != "":
            # LIKE '%text%' - in SQLite it does not distinguish upper and lower case letters
            statement = statement.where(Expense.description.contains(text))
        statement = statement.order_by(Expense.date.desc(), Expense.expense_id.desc())

        expenses = self._session.exec(statement).all()
        # a list comprehension: the list of the results of to_dto(e), for every e in expenses
        return [to_dto(e) for e in expenses]

    def get_by_id(self, id: int) -> ExpenseDTO | None:
        expense = self._session.get(Expense, id)
        if expense is None:
            return None
        return to_dto(expense)

    def create(self, expense_dto: ExpenseDTO) -> ExpenseDTO:
        new_expense = Expense(
            date=expense_dto.date,
            description=expense_dto.description,
            amount=expense_dto.amount,
            category_id=expense_dto.category_id,
        )
        self._session.add(new_expense)
        self._session.commit()
        self._session.refresh(new_expense)  # reads the new row back, with its expense_id
        return to_dto(new_expense)

    def update(self, expense_dto: ExpenseDTO) -> bool:
        """Returns False if there is no expense with the given id."""
        expense_to_update = self._session.get(Expense, expense_dto.id)
        if expense_to_update is None:
            return False
        expense_to_update.date = expense_dto.date
        expense_to_update.description = expense_dto.description
        expense_to_update.amount = expense_dto.amount
        expense_to_update.category_id = expense_dto.category_id
        self._session.add(expense_to_update)
        self._session.commit()
        return True

    def delete(self, id: int) -> bool:
        """Returns False if there is no expense with the given id."""
        expense_to_delete = self._session.get(Expense, id)
        if expense_to_delete is None:
            return False
        self._session.delete(expense_to_delete)
        self._session.commit()
        return True
