from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from sqlmodel import Field, SQLModel


class AccountSnapshot(SQLModel, table=True):
    __tablename__ = "account_snapshot"
    __table_args__ = {"sqlite_autoincrement": False}

    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id")
    period: date  # 统一存当月最后一天，如 2026-05-31
    balance: Decimal = Field(decimal_places=2, max_digits=14)
    recorded_at: datetime = Field(default_factory=datetime.now)
