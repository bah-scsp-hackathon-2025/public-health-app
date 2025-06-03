from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.report import Report

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportModel(BaseModel):
    title: str
    content: str
    author: str
    approved: bool


class ReportResponse(ReportModel):
    id: int


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_report(report: ReportModel, db: Session = Depends(get_db)):
    # Check if report already exists
    db_report = db.query(Report).filter(Report.title == report.title).first()
    if db_report:
        raise HTTPException(status_code=400, detail="Report already exists")

    db_report = Report(
        title=report.title,
        content=report.content,
        author=report.author,
        approved=report.approved,
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


@router.get("/", response_model=List[ReportResponse])
async def get_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reports = db.query(Report).offset(skip).limit(limit).all()
    return reports


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(report_id: int, report_update: ReportModel, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    db_report = Report(
        title=report_update.title or report.title,
        content=report_update.content or report.content,
        author=report_update.author or report.author,
        approved=report_update.approved or report.approved,
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


@router.delete("/{report_id}", response_model=ReportResponse)
async def delete_report(report_id: int, b: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    db.delete(report)
    db.commit()
    return report
