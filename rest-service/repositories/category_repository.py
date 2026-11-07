from sqlmodel import Session, select

from dtos.category_dto import CategoryDTO
from models.category import Category


def to_dto(category: Category) -> CategoryDTO:
    return CategoryDTO(id=category.category_id, name=category.name, monthly_budget=category.monthly_budget)


class CategoryRepository:
    """Reads and writes the table category. The rest of the service sees only CategoryDTO objects."""

    def __init__(self, session: Session):
        self._session = session

    def get_all(self) -> list[CategoryDTO]:
        # SELECT * FROM category ORDER BY name
        categories = self._session.exec(select(Category).order_by(Category.name)).all()
        return [to_dto(c) for c in categories]

    def get_by_id(self, id: int) -> CategoryDTO | None:
        category = self._session.get(Category, id)
        if category is None:
            return None
        return to_dto(category)

    def create(self, category_dto: CategoryDTO) -> CategoryDTO:
        new_category = Category(name=category_dto.name, monthly_budget=category_dto.monthly_budget)
        self._session.add(new_category)
        self._session.commit()
        self._session.refresh(new_category)  # reads the new row back, with its category_id
        return to_dto(new_category)

    def update(self, category_dto: CategoryDTO) -> bool:
        """Returns False if there is no category with the given id."""
        category_to_update = self._session.get(Category, category_dto.id)
        if category_to_update is None:
            return False
        category_to_update.name = category_dto.name
        category_to_update.monthly_budget = category_dto.monthly_budget
        self._session.add(category_to_update)
        self._session.commit()
        return True

    def delete(self, id: int) -> bool:
        """Returns False if there is no category with the given id."""
        category_to_delete = self._session.get(Category, id)
        if category_to_delete is None:
            return False
        self._session.delete(category_to_delete)
        self._session.commit()
        return True
