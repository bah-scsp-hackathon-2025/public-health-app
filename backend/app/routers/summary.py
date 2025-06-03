from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.summary import SummaryResponse
from app.routers.alerts import get_alerts

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("/", response_model=SummaryResponse)
async def get_summary(db: Session = Depends(get_db)):
    alerts = get_alerts(db=db)
    # logic to generate summary
    #
    summary = ""

    return {"description": summary}
