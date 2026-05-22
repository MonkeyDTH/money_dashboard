from decimal import Decimal
from fastapi.templating import Jinja2Templates


def format_amount(value) -> str:
    """格式化金额：千分位，保留两位小数"""
    if value is None:
        return "—"
    try:
        v = Decimal(str(value))
        return f"{v:,.2f}"
    except Exception:
        return str(value)


def format_period(value) -> str:
    """格式化月份：2026-05-31 → 2026年5月"""
    if value is None:
        return "—"
    try:
        return f"{value.year}年{value.month}月"
    except Exception:
        return str(value)


def register_filters(templates: Jinja2Templates) -> None:
    templates.env.filters["amount"] = format_amount
    templates.env.filters["period"] = format_period
