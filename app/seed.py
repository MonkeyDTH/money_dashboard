"""初始化种子数据：创建默认成员和支出大类（如果不存在）"""
from sqlmodel import Session, select
from app.database import engine, init_db
from app.models import Member, ExpenseCategory

_EXPENSE_CATEGORIES = [
    {"name": "生活消费", "color": "#3B82F6", "sort_order": 1},
    {"name": "固定支出", "color": "#8B5CF6", "sort_order": 2},
    {"name": "特别支出", "color": "#F59E0B", "sort_order": 3},
]


def seed():
    init_db()
    with Session(engine) as session:
        existing = session.exec(select(Member).where(Member.is_self == True)).first()
        if not existing:
            session.add(Member(name="我", is_self=True))
            session.commit()
            print("已创建默认成员")
        else:
            print(f"默认成员已存在：{existing.name}")

        for cat in _EXPENSE_CATEGORIES:
            exists = session.exec(
                select(ExpenseCategory).where(ExpenseCategory.name == cat["name"])
            ).first()
            if not exists:
                session.add(ExpenseCategory(**cat))
        session.commit()


if __name__ == "__main__":
    seed()
