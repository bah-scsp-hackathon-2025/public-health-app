from typing import List
from fastapi import APIRouter
from app.models.trend import TrendResponse

router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("/", response_model=List[TrendResponse])
async def get_trends():
    # logic to generate trends
    #

    # dummy data
    trends = [{"set1": [1, 2, 3, 4]}]
    return trends
