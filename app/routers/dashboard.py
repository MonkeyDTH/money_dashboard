from fastapi import APIRouter, Request, Depends
from sqlmodel import Session, select, func
from decimal import Decimal
from datetime import date
from typing import Literal
import json

from app.database import get_session
from app.deps import templates
from app.models import Account, AccountSnapshot, SalaryRecord, AccountType, Member, OwnerType

router = APIRouter()


def _build_dashboard_data(session: Session, view: str) -> dict:
    """按视图过滤账户，计算净资产趋势、资产配置、收入数据。"""
    # 确定过滤条件
    self_member = session.exec(select(Member).where(Member.is_self == True)).first()

    q = (
        select(AccountSnapshot.period, Account.type, func.sum(AccountSnapshot.balance).label("total"))
        .join(Account, Account.id == AccountSnapshot.account_id)
        .where(Account.is_active == True)
    )
    if view == "personal":
        q = q.where(Account.owner_type == OwnerType.member)
        if self_member:
            q = q.where(Account.owner_member_id == self_member.id)
    else:
        q = q.where(Account.owner_type == OwnerType.family)

    q = q.group_by(AccountSnapshot.period, Account.type).order_by(AccountSnapshot.period)
    snapshots = session.exec(q).all()

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
        latest_by_type = {k: float(v) for k, v in period_by_type[sorted_periods[-1]].items()}

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

    return {
        "current_net": current_net,
        "net_change": net_change,
        "trend_labels": json.dumps(trend_labels, ensure_ascii=False),
        "trend_data": json.dumps(trend_data),
        "latest_by_type": json.dumps(latest_by_type, ensure_ascii=False),
        "salary_labels": json.dumps([f"{r.period.year}年{r.period.month}月" for r in salary_rows], ensure_ascii=False),
        "salary_data": json.dumps([float(r.total) for r in salary_rows]),
    }


@router.get("/", name="dashboard")
async def dashboard(
    request: Request,
    view: str = "family",
    session: Session = Depends(get_session),
):
    if view not in ("family", "personal"):
        view = "family"
    data = _build_dashboard_data(session, view)
    return templates.TemplateResponse(request, "dashboard/index.html", {
        "view": view,
        **data,
    })
