from datetime import date
from decimal import Decimal
from typing import Optional
from sqlmodel import Field, SQLModel
from app.models.account import OwnerType


class ExpenseCategory(SQLModel, table=True):
    __tablename__ = "expense_category"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=64)
    color: str = Field(default="#6366f1", max_length=16)
    sort_order: int = Field(default=0)


class MonthlyExpense(SQLModel, table=True):
    __tablename__ = "monthly_expense"

    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="expense_category.id")
    period: date
    amount: Decimal = Field(decimal_places=2, max_digits=14)
    owner_type: OwnerType = Field(default=OwnerType.family)
    owner_member_id: Optional[int] = Field(default=None, foreign_key="member.id")
    note: Optional[str] = Field(default=None)
