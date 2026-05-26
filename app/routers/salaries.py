from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from decimal import Decimal
from datetime import date
from typing import Optional
import calendar

from app.database import get_session
from app.deps import templates
from app.models import SalaryRecord, SalaryItem, Company, Member, ItemType, Direction
from app.models.salary import ITEM_TYPE_LABELS, ITEM_TYPE_DEFAULT_DIRECTION

router = APIRouter(prefix="/salaries", tags=["salaries"])


def month_end(year: int, month: int) -> date:
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, last_day)


@router.get("", name="salaries_list")
async def salaries_list(request: Request, session: Session = Depends(get_session)):
    records = session.exec(select(SalaryRecord).order_by(SalaryRecord.period.desc())).all()
    companies = session.exec(select(Company)).all()
    company_map = {c.id: c for c in companies}
    return templates.TemplateResponse(request, "salaries/list.html", {
        "records": records,
        "company_map": company_map,
    })


@router.get("/new", name="salaries_new_form")
async def salaries_new_form(request: Request, session: Session = Depends(get_session)):
    companies = session.exec(select(Company).order_by(Company.start_date.desc())).all()
    members = session.exec(select(Member)).all()
    today = date.today()
    return templates.TemplateResponse(request, "salaries/form.html", {
        "record": None,
        "items": [],
        "companies": companies,
        "members": members,
        "item_types": ItemType,
        "item_type_labels": ITEM_TYPE_LABELS,
        "default_directions": ITEM_TYPE_DEFAULT_DIRECTION,
        "directions": Direction,
        "default_year": today.year,
        "default_month": today.month,
    })


@router.post("", name="salaries_create")
async def salaries_create(request: Request, session: Session = Depends(get_session)):
    form = await request.form()
    year = int(form["year"])
    month = int(form["month"])
    period = month_end(year, month)

    record = SalaryRecord(
        member_id=int(form["member_id"]),
        company_id=int(form["company_id"]),
        period=period,
        pay_date=date.fromisoformat(form["pay_date"]) if form.get("pay_date") else None,
        note=form.get("note") or None,
    )
    session.add(record)
    session.flush()

    gross = Decimal("0")
    net = Decimal("0")

    idx = 0
    while f"item_type_{idx}" in form:
        amount_str = form.get(f"amount_{idx}", "0")
        if amount_str:
            item_type = ItemType(form[f"item_type_{idx}"])
            amount = Decimal(amount_str)
            direction = Direction(form[f"direction_{idx}"])
            label = form.get(f"label_{idx}", ITEM_TYPE_LABELS[item_type])
            session.add(SalaryItem(
                salary_record_id=record.id,
                item_type=item_type,
                amount=amount,
                direction=direction,
                label=label,
            ))
            if direction == Direction.income:
                gross += amount
                net += amount
            else:
                net -= amount
        idx += 1

    record.gross = gross
    record.net = net
    session.add(record)
    session.commit()
    return RedirectResponse("/salaries", status_code=303)


@router.get("/{record_id}/edit", name="salaries_edit_form")
async def salaries_edit_form(record_id: int, request: Request, session: Session = Depends(get_session)):
    record = session.get(SalaryRecord, record_id)
    if not record:
        raise HTTPException(status_code=404)
    items = session.exec(select(SalaryItem).where(SalaryItem.salary_record_id == record_id)).all()
    companies = session.exec(select(Company).order_by(Company.start_date.desc())).all()
    members = session.exec(select(Member)).all()
    return templates.TemplateResponse(request, "salaries/form.html", {
        "record": record,
        "items": items,
        "companies": companies,
        "members": members,
        "item_types": ItemType,
        "item_type_labels": ITEM_TYPE_LABELS,
        "default_directions": ITEM_TYPE_DEFAULT_DIRECTION,
        "directions": Direction,
        "default_year": record.period.year,
        "default_month": record.period.month,
    })


@router.post("/{record_id}/edit", name="salaries_update")
async def salaries_update(record_id: int, request: Request, session: Session = Depends(get_session)):
    record = session.get(SalaryRecord, record_id)
    if not record:
        raise HTTPException(status_code=404)

    form = await request.form()
    year = int(form["year"])
    month = int(form["month"])
    record.period = month_end(year, month)
    record.member_id = int(form["member_id"])
    record.company_id = int(form["company_id"])
    record.pay_date = date.fromisoformat(form["pay_date"]) if form.get("pay_date") else None
    record.note = form.get("note") or None

    # 清空旧明细，重建
    old_items = session.exec(select(SalaryItem).where(SalaryItem.salary_record_id == record_id)).all()
    for item in old_items:
        session.delete(item)
    session.flush()

    gross = Decimal("0")
    net = Decimal("0")

    idx = 0
    while f"item_type_{idx}" in form:
        amount_str = form.get(f"amount_{idx}", "0")
        if amount_str:
            item_type = ItemType(form[f"item_type_{idx}"])
            amount = Decimal(amount_str)
            direction = Direction(form[f"direction_{idx}"])
            label = form.get(f"label_{idx}", ITEM_TYPE_LABELS[item_type])
            session.add(SalaryItem(
                salary_record_id=record.id,
                item_type=item_type,
                amount=amount,
                direction=direction,
                label=label,
            ))
            if direction == Direction.income:
                gross += amount
                net += amount
            else:
                net -= amount
        idx += 1

    record.gross = gross
    record.net = net
    session.add(record)
    session.commit()
    return RedirectResponse(f"/salaries/{record_id}", status_code=303)


@router.get("/{record_id}", name="salaries_detail")
async def salaries_detail(record_id: int, request: Request, session: Session = Depends(get_session)):
    record = session.get(SalaryRecord, record_id)
    if not record:
        raise HTTPException(status_code=404)
    items = session.exec(select(SalaryItem).where(SalaryItem.salary_record_id == record_id)).all()
    companies = session.exec(select(Company)).all()
    company_map = {c.id: c for c in companies}
    return templates.TemplateResponse(request, "salaries/detail.html", {
        "record": record,
        "items": items,
        "company_map": company_map,
        "item_type_labels": ITEM_TYPE_LABELS,
        "Direction": Direction,
    })
