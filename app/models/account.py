from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel


class AccountType(str, Enum):
    cash = "现金"
    demand = "活期"
    fixed = "定期"
    money_fund = "货币基金"
    stock = "股票"
    fund = "基金"
    housing_fund = "公积金"
    real_estate = "房产"
    vehicle = "车辆"
    liability = "负债"
    other = "其他"


class OwnerType(str, Enum):
    family = "family"
    member = "member"


class Account(SQLModel, table=True):
    __tablename__ = "account"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=128)
    type: AccountType
    owner_type: OwnerType = Field(default=OwnerType.family)
    owner_member_id: Optional[int] = Field(default=None, foreign_key="member.id")
    currency: str = Field(default="CNY", max_length=8)
    is_active: bool = Field(default=True)
    note: Optional[str] = Field(default=None)
    sort_order: int = Field(default=0)
