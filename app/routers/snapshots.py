from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from decimal import Decimal
from datetime import date
from typing import Optional
import calendar

from app.database import get_session
from app.deps import templates
from app.models import Account, AccountSnapshot

router = APIRouter(prefix="/snapshots", tags=["snapshots"])


def month_end(year: int, month: int) -> date:
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, last_day)


@router.get("", name="snapshots_entry")
async def snapshots_entry(
    request: Request,
    year: Optional[int] = None,
    month: Optional[int] = None,
    session: Session = Depends(get_session),
):
    today = date.today()
    year = year or today.year
    month = month or today.month
    period = month_end(year, month)

    accounts = session.exec(
        select(Account).where(Account.is_active == True).order_by(Account.sort_order, Account.id)
    ).all()

    existing = {
        s.account_id: s
        for s in session.exec(
            select(AccountSnapshot).where(AccountSnapshot.period == period)
        ).all()
    }

    prev_period = month_end(year if month > 1 else year - 1, month - 1 if month > 1 else 12)
    prev = {
        s.account_id: s.balance
        for s in session.exec(
            select(AccountSnapshot).where(AccountSnapshot.period == prev_period)
        ).all()
    }

    return templates.TemplateResponse(request, "snapshots/entry.html", {
        "year": year,
        "month": month,
        "period": period,
        "accounts": accounts,
        "existing": existing,
        "prev": prev,
    })


@router.post("", name="snapshots_save")
async def snapshots_save(request: Request, session: Session = Depends(get_session)):
    form = await request.form()
    year = int(form["year"])
    month = int(form["month"])
    period = month_end(year, month)

    for key, value in form.items():
        if not key.startswith("balance_"):
            continue
        account_id = int(key.split("_")[1])
        if not value:
            continue
        balance = Decimal(str(value))

        existing = session.exec(
            select(AccountSnapshot)
            .where(AccountSnapshot.account_id == account_id)
            .where(AccountSnapshot.period == period)
        ).first()

        if existing:
            existing.balance = balance
            session.add(existing)
        else:
            session.add(AccountSnapshot(account_id=account_id, period=period, balance=balance))

    session.commit()
    return RedirectResponse(f"/snapshots?year={year}&month={month}", status_code=303)
