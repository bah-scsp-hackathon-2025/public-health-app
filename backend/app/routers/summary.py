from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.summary import Summary, SummaryCreate, SummaryUpdate, SummaryResponse

router = APIRouter(prefix="/summaries", tags=["summaries"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_summmary(summary: SummaryCreate, db: Session = Depends(get_db)):
    db_summary = db.query(Summary).filter(Summary.description == summary.description).first()
    if db_summary:
        raise HTTPException(status_code=400, detail="Summary already exists")

    db_summary = Summary(
        description=summary.description,
    )
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary


@router.get("/", response_model=List[SummaryResponse])
async def get_summaries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    summaries = db.query(Summary).offset(skip).limit(limit).all()
    return summaries


@router.get("/{summary_id}", response_model=SummaryResponse)
async def get_summary(summary_id: str, db: Session = Depends(get_db)):
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if summary is None:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary


@router.put("/{summary_id}", response_model=SummaryResponse)
async def update_summary(summary_id: str, summary_update: SummaryUpdate, db: Session = Depends(get_db)):
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if summary is None:
        raise HTTPException(status_code=404, detail="Summary not found")

    if summary_update.description:
        summary.description = summary_update.description

    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary


@router.delete("/{summary_id}", response_model=SummaryResponse)
async def delete_summary(summary_id: str, db: Session = Depends(get_db)):
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if summary is None:
        raise HTTPException(status_code=404, detail="Summary not found")

    db.delete(summary)
    db.commit()
    return summary
