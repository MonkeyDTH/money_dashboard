"""
一次性脚本：从 data/个人资产记录.xlsx 导入个人账户和月度余额快照。

- 新建 7 个个人账户（owner_type=member，已存在则跳过）
- 每月取日期最大的一行作为当月快照，period 存月末
- 余额为 None 或 <= 0 的账户该月跳过
- 幂等：按 (account_id, period) 去重，已有则更新
"""
import calendar
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

# 确保项目根目录在 sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import openpyxl
from sqlmodel import Session, select

from app.database import engine, init_db
from app.models import Account, AccountSnapshot, AccountType, Member, OwnerType


# Excel 列索引（0-based）→ 账户定义
ACCOUNT_DEFS = [
    (1, "现金（个人）", AccountType.cash),
    (2, "农行卡",       AccountType.demand),
    (3, "招行卡",       AccountType.demand),
    (4, "其他银行",     AccountType.demand),
    (5, "蚂蚁财富",     AccountType.money_fund),
    (6, "微信理财通",   AccountType.money_fund),
    (7, "蛋卷基金",     AccountType.fund),
]

EXCEL_PATH = Path(__file__).parent.parent.parent / "data" / "个人资产记录.xlsx"


def month_end(year: int, month: int) -> date:
    return date(year, month, calendar.monthrange(year, month)[1])


def load_monthly_last(ws) -> dict[tuple[int, int], list]:
    """按 (year, month) 取日期最大的一行。"""
    monthly: dict[tuple[int, int], list] = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        d = row[0]
        if not isinstance(d, datetime):
            continue
        key = (d.year, d.month)
        if key not in monthly or d > monthly[key][0]:
            monthly[key] = [d] + list(row[1:])
    return monthly


def run():
    init_db()

    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    ws = wb["Sheet1"]
    monthly = load_monthly_last(ws)
    print(f"Excel 共 {len(monthly)} 个月份")

    with Session(engine) as session:
        # 获取 is_self 成员
        self_member = session.exec(select(Member).where(Member.is_self == True)).first()
        if not self_member:
            print("错误：找不到 is_self=True 的成员，请先创建默认成员")
            return

        # 创建或获取账户
        account_ids: dict[int, int] = {}  # col_idx -> account.id
        for col_idx, name, acc_type in ACCOUNT_DEFS:
            existing = session.exec(
                select(Account).where(Account.name == name).where(Account.owner_type == OwnerType.member)
            ).first()
            if existing:
                account_ids[col_idx] = existing.id
                print(f"账户已存在，跳过创建：{name} (id={existing.id})")
            else:
                acc = Account(
                    name=name,
                    type=acc_type,
                    owner_type=OwnerType.member,
                    owner_member_id=self_member.id,
                    currency="CNY",
                    is_active=True,
                )
                session.add(acc)
                session.flush()
                account_ids[col_idx] = acc.id
                print(f"新建账户：{name} (id={acc.id})")

        # 导入快照
        inserted = updated = skipped = 0
        for (year, month), row_data in sorted(monthly.items()):
            period = month_end(year, month)
            # row_data[0] 是 datetime，后面索引 col_idx-1（因为 row_data 从列1开始）
            for col_idx, name, _ in ACCOUNT_DEFS:
                raw = row_data[col_idx]  # row_data = [datetime, col1, col2, ...]，索引与列号一致
                if raw is None:
                    skipped += 1
                    continue
                try:
                    balance = Decimal(str(raw))
                except Exception:
                    skipped += 1
                    continue
                if balance <= 0:
                    skipped += 1
                    continue

                account_id = account_ids[col_idx]
                existing_snap = session.exec(
                    select(AccountSnapshot)
                    .where(AccountSnapshot.account_id == account_id)
                    .where(AccountSnapshot.period == period)
                ).first()

                if existing_snap:
                    existing_snap.balance = balance
                    session.add(existing_snap)
                    updated += 1
                else:
                    session.add(AccountSnapshot(account_id=account_id, period=period, balance=balance))
                    inserted += 1

        session.commit()
        print(f"\n导入完成：新增 {inserted} 条，更新 {updated} 条，跳过 {skipped} 条")


if __name__ == "__main__":
    run()
