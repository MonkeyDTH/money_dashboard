from fastapi import APIRouter, Request, Depends
from sqlmodel import Session, select, func
from decimal import Decimal
from datetime import date
import json

from app.database import get_session
from app.deps import templates
from app.models import Account, AccountSnapshot, SalaryRecord, AccountType

router = APIRouter()


@router.get("/", name="dashboard")
async def dashboard(request: Request, session: Session = Depends(get_session)):
    snapshots = session.exec(
        select(AccountSnapshot.period, Account.type, func.sum(AccountSnapshot.balance).label("total"))
        .join(Account, Account.id == AccountSnapshot.account_id)
        .where(Account.is_active == True)
        .group_by(AccountSnapshot.period, Account.type)
        .order_by(AccountSnapshot.period)
    ).all()

    period_net: dict[date, Decimal] = {}
    period_by_type: dict[date, dict[str, Decimal]] = {}
    for row in snapshots:
        sign = Decimal("-1") if row.type == AccountType.liability else Decimal("1")
        period_net[row.period] = period_net.get(row.period, Decimal("0")) + sign * row.total
        period_by_type.setdefault(row.period, {})
        period_by_type[row.period][row.type.value] = (
            period_by_type[row.period].get(row.type.value, Decimal("0")) + row.total
        )

    sorted_periods = sorted(period_net.keys())
    trend_labels = [f"{p.year}年{p.month}月" for p in sorted_periods]
    trend_data = [float(period_net[p]) for p in sorted_periods]

    latest_by_type: dict[str, float] = {}
    if sorted_periods:
        latest_period = sorted_periods[-1]
        latest_by_type = {k: float(v) for k, v in period_by_type[latest_period].items()}

    current_net = Decimal("0")
    net_change = Decimal("0")
    if sorted_periods:
        current_net = period_net[sorted_periods[-1]]
        if len(sorted_periods) >= 2:
            net_change = current_net - period_net[sorted_periods[-2]]

    salary_rows = session.exec(
        select(SalaryRecord.period, func.sum(SalaryRecord.net).label("total"))
        .group_by(SalaryRecord.period)
        .order_by(SalaryRecord.period.desc())
        .limit(12)
    ).all()
    salary_rows = list(reversed(salary_rows))
    salary_labels = [f"{r.period.year}年{r.period.month}月" for r in salary_rows]
    salary_data = [float(r.total) for r in salary_rows]

    return templates.TemplateResponse(request, "dashboard/index.html", {
        "current_net": current_net,
        "net_change": net_change,
        "trend_labels": json.dumps(trend_labels, ensure_ascii=False),
        "trend_data": json.dumps(trend_data),
        "latest_by_type": json.dumps(latest_by_type, ensure_ascii=False),
        "salary_labels": json.dumps(salary_labels, ensure_ascii=False),
        "salary_data": json.dumps(salary_data),
    })
