from datetime import date
from typing import Optional
from sqlmodel import Field, SQLModel


class Company(SQLModel, table=True):
    __tablename__ = "company"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=128)
    member_id: int = Field(foreign_key="member.id")
    start_date: date
    end_date: Optional[date] = Field(default=None)  # None 表示在职
    note: Optional[str] = Field(default=None)
