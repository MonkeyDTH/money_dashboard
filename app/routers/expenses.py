from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlmodel import Session, select
from decimal import Decimal
from datetime import date
from typing import Optional
import calendar

from app.database import get_session
from app.deps import templates
from app.models import Member, ExpenseCategory, MonthlyExpense, OtherIncome, OwnerType

router = APIRouter(prefix="/expenses", tags=["expenses"])


def month_end(year: int, month: int) -> date:
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, last_day)


@router.get("", name="expenses_index")
async def expenses_index(
    request: Request,
    year: Optional[int] = None,
    month: Optional[int] = None,
    session: Session = Depends(get_session),
):
    today = date.today()
    year = year or today.year
    month = month or today.month
    period = month_end(year, month)

    self_member = session.exec(select(Member).where(Member.is_self == True)).first()
    categories = session.exec(
        select(ExpenseCategory).order_by(ExpenseCategory.sort_order)
    ).all()

    # 已录入支出：(category_id, owner_type, owner_member_id) -> MonthlyExpense
    expenses_raw = session.exec(
        select(MonthlyExpense).where(MonthlyExpense.period == period)
    ).all()
    expenses = {(e.category_id, e.owner_type, e.owner_member_id): e for e in expenses_raw}

    # 其他收入列表
    other_incomes = session.exec(
        select(OtherIncome)
        .where(OtherIncome.period == period)
        .order_by(OtherIncome.recorded_at)
    ).all()

    return templates.TemplateResponse(request, "expenses/index.html", {
        "year": year,
        "month": month,
        "period": period,
        "self_member": self_member,
        "categories": categories,
        "expenses": expenses,
        "other_incomes": other_incomes,
    })


@router.post("/save", name="expenses_save")
async def expenses_save(
    request: Request,
    session: Session = Depends(get_session),
):
    form = await request.form()
    year = int(form["year"])
    month = int(form["month"])
    period = month_end(year, month)

    self_member = session.exec(select(Member).where(Member.is_self == True)).first()
    categories = session.exec(select(ExpenseCategory)).all()

    for cat in categories:
        for owner_type_str, member_id in [("family", None), ("member", self_member.id if self_member else None)]:
            key = f"expense_{cat.id}_{owner_type_str}"
            value = form.get(key, "").strip()
            note_key = f"note_{cat.id}_{owner_type_str}"
            note = form.get(note_key, "").strip() or None
            owner_type = OwnerType.family if owner_type_str == "family" else OwnerType.member

            existing = session.exec(
                select(MonthlyExpense)
                .where(MonthlyExpense.period == period)
                .where(MonthlyExpense.category_id == cat.id)
                .where(MonthlyExpense.owner_type == owner_type)
                .where(MonthlyExpense.owner_member_id == member_id)
            ).first()

            if value:
                amount = Decimal(value)
                if existing:
                    existing.amount = amount
                    existing.note = note
                    session.add(existing)
                else:
                    session.add(MonthlyExpense(
                        category_id=cat.id,
                        period=period,
                        amount=amount,
                        owner_type=owner_type,
                        owner_member_id=member_id,
                        note=note,
                    ))
            else:
                if existing:
                    session.delete(existing)

    session.commit()
    return RedirectResponse(f"/expenses?year={year}&month={month}", status_code=303)


@router.post("/income/add", name="income_add")
async def income_add(
    request: Request,
    session: Session = Depends(get_session),
):
    form = await request.form()
    year = int(form["year"])
    month = int(form["month"])
    period = month_end(year, month)
    amount_str = form.get("amount", "").strip()
    note = form.get("note", "").strip() or None
    owner_type_str = form.get("owner_type", "family")

    if not amount_str:
        return RedirectResponse(f"/expenses?year={year}&month={month}", status_code=303)

    self_member = session.exec(select(Member).where(Member.is_self == True)).first()
    owner_type = OwnerType.family if owner_type_str == "family" else OwnerType.member
    member_id = self_member.id if owner_type == OwnerType.member and self_member else None

    session.add(OtherIncome(
        period=period,
        amount=Decimal(amount_str),
        owner_type=owner_type,
        owner_member_id=member_id,
        note=note,
    ))
    session.commit()
    return RedirectResponse(f"/expenses?year={year}&month={month}", status_code=303)


@router.post("/income/{income_id}/delete", name="income_delete")
async def income_delete(
    income_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    form = await request.form()
    year = int(form["year"])
    month = int(form["month"])

    income = session.get(OtherIncome, income_id)
    if income:
        session.delete(income)
        session.commit()
    return RedirectResponse(f"/expenses?year={year}&month={month}", status_code=303)
