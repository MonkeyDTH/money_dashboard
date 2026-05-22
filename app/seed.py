"""初始化种子数据：创建默认 is_self=True 的成员（如果不存在）"""
from sqlmodel import Session, select
from app.database import engine, init_db
from app.models import Member


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


if __name__ == "__main__":
    seed()
