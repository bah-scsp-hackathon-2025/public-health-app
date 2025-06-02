from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/items", tags=["items"])

# In-memory storage for demo purposes
items_db = []


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


class ItemCreate(ItemBase):
    pass


class ItemResponse(ItemBase):
    id: int


@router.post("/", response_model=ItemResponse)
async def create_item(item: ItemCreate):
    item_id = len(items_db) + 1
    new_item = {"id": item_id, **item.dict()}
    items_db.append(new_item)
    return new_item


@router.get("/", response_model=List[ItemResponse])
async def get_items():
    return items_db


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    item = next((item for item in items_db if item["id"] == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
