#routes/factory.py
from typing import Type, TypeVar, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import get_db directly from app.database.base
from app.database.base import get_db
from app.repositories.base import BaseRepository

ModelType = TypeVar("ModelType")
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)
ResponseSchema = TypeVar("ResponseSchema", bound=BaseModel)

def create_crud_route(
    model: Type[ModelType],
    create_schema: Type[CreateSchema],
    update_schema: Type[UpdateSchema],
    response_schema: Type[ResponseSchema],
    prefix: str,
    tags: List[str],
    id_field: str
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=tags)
    repo = BaseRepository(model)

    @router.get("", response_model=List[response_schema])
    def get_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        return repo.get_all(db, skip=skip, limit=limit)

    @router.get("/{item_id}", response_model=response_schema)
    def get_one(item_id: int, db: Session = Depends(get_db)):
        item = repo.get_by_id(db, id_field, item_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        return item

    @router.post("", response_model=response_schema, status_code=status.HTTP_201_CREATED)
    def create(payload: create_schema, db: Session = Depends(get_db)):
        try:
            return repo.create(db, payload.model_dump())
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    @router.patch("/{item_id}", response_model=response_schema)
    def update(item_id: int, payload: update_schema, db: Session = Depends(get_db)):
        item = repo.get_by_id(db, id_field, item_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        update_data = payload.model_dump(exclude_unset=True)
        return repo.update(db, item, update_data)

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete(item_id: int, db: Session = Depends(get_db)):
        item = repo.get_by_id(db, id_field, item_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        repo.delete(db, item)
        return None

    return router