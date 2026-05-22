from typing import Optional
from sqlmodel import Field, SQLModel


class Member(SQLModel, table=True):
    __tablename__ = "member"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=64)
    is_self: bool = Field(default=False)
