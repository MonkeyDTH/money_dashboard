from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel


class ItemType(str, Enum):
    base = "base"                       # 基本工资
    bonus = "bonus"                     # 奖金
    allowance = "allowance"             # 津贴/补贴
    overtime = "overtime"               # 加班费
    stock = "stock"                     # 股权激励
    social_insurance = "social_insurance"   # 社保（个人部分）
    housing_fund = "housing_fund"       # 公积金（个人部分）
    income_tax = "income_tax"           # 个税
    other_deduction = "other_deduction" # 其他扣除
    other_income = "other_income"       # 其他收入


class Direction(str, Enum):
    income = "income"       # 收入项（正）
    deduction = "deduction" # 扣除项（负）


ITEM_TYPE_LABELS = {
    ItemType.base: "基本工资",
    ItemType.bonus: "奖金",
    ItemType.allowance: "津贴/补贴",
    ItemType.overtime: "加班费",
    ItemType.stock: "股权激励",
    ItemType.social_insurance: "社保（个人）",
    ItemType.housing_fund: "公积金（个人）",
    ItemType.income_tax: "个税",
    ItemType.other_deduction: "其他扣除",
    ItemType.other_income: "其他收入",
}

# 各 item_type 的默认方向
ITEM_TYPE_DEFAULT_DIRECTION = {
    ItemType.base: Direction.income,
    ItemType.bonus: Direction.income,
    ItemType.allowance: Direction.income,
    ItemType.overtime: Direction.income,
    ItemType.stock: Direction.income,
    ItemType.social_insurance: Direction.deduction,
    ItemType.housing_fund: Direction.deduction,
    ItemType.income_tax: Direction.deduction,
    ItemType.other_deduction: Direction.deduction,
    ItemType.other_income: Direction.income,
}


class SalaryRecord(SQLModel, table=True):
    __tablename__ = "salary_record"

    id: Optional[int] = Field(default=None, primary_key=True)
    member_id: int = Field(foreign_key="member.id")
    company_id: int = Field(foreign_key="company.id")
    period: date                                    # 工资归属月份（月末）
    pay_date: Optional[date] = Field(default=None)  # 实际发薪日
    gross: Decimal = Field(default=Decimal("0"), decimal_places=2, max_digits=14)  # 应发合计
    net: Decimal = Field(default=Decimal("0"), decimal_places=2, max_digits=14)    # 实发合计
    note: Optional[str] = Field(default=None)


class SalaryItem(SQLModel, table=True):
    __tablename__ = "salary_item"

    id: Optional[int] = Field(default=None, primary_key=True)
    salary_record_id: int = Field(foreign_key="salary_record.id")
    item_type: ItemType
    amount: Decimal = Field(decimal_places=2, max_digits=14)  # 统一存正数
    direction: Direction
    label: str = Field(max_length=64)  # 自定义名称，如"年终奖"
