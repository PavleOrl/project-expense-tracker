from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from database import get_category_repository
from dtos.category_dto import CategoryDTO
from repositories.category_repository import CategoryRepository

router = APIRouter(prefix="/api/categories", tags=["categories"])

# the repository is handed over by FastAPI (dependency injection)
CategoryRepo = Annotated[CategoryRepository, Depends(get_category_repository)]


@router.get("")
def get_all(category_repo: CategoryRepo) -> list[CategoryDTO]:
    return category_repo.get_all()


@router.get("/{id}")
def get_by_id(id: int, category_repo: CategoryRepo) -> CategoryDTO:
    category = category_repo.get_by_id(id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.post("", status_code=status.HTTP_201_CREATED)
def create(model: CategoryDTO, category_repo: CategoryRepo, response: Response) -> CategoryDTO:
    """A category with a name that already exists is refused by the database (409)."""
    category = category_repo.create(model)

    response.headers["Location"] = f"/api/categories/{category.id}"
    return category


@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def update(id: int, model: CategoryDTO, category_repo: CategoryRepo) -> None:
    if id != model.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The id in the address and the id in the body are different",
        )
    if not category_repo.update(model):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(id: int, category_repo: CategoryRepo) -> None:
    """A category that still has expenses can not be deleted: the database refuses it (409)."""
    if not category_repo.delete(id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
