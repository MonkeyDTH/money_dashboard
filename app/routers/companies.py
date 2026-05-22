from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from datetime import date
from typing import Optional

from app.database import get_session
from app.deps import templates
from app.models import Company, Member

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", name="companies_list")
async def companies_list(request: Request, session: Session = Depends(get_session)):
    companies = session.exec(select(Company).order_by(Company.start_date.desc())).all()
    members = session.exec(select(Member)).all()
    member_map = {m.id: m for m in members}
    return templates.TemplateResponse(request, "companies/list.html", {
        "companies": companies,
        "members": members,
        "member_map": member_map,
    })


@router.post("", name="companies_create")
async def companies_create(
    name: str = Form(...),
    member_id: int = Form(...),
    start_date: date = Form(...),
    end_date: Optional[date] = Form(None),
    note: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    company = Company(name=name, member_id=member_id, start_date=start_date, end_date=end_date, note=note)
    session.add(company)
    session.commit()
    return RedirectResponse("/companies", status_code=303)


@router.post("/{company_id}/edit", name="companies_update")
async def companies_update(
    company_id: int,
    name: str = Form(...),
    member_id: int = Form(...),
    start_date: date = Form(...),
    end_date: Optional[date] = Form(None),
    note: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404)
    company.name = name
    company.member_id = member_id
    company.start_date = start_date
    company.end_date = end_date
    company.note = note
    session.add(company)
    session.commit()
    return RedirectResponse("/companies", status_code=303)
