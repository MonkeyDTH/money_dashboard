from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from typing import Optional

from app.database import get_session
from app.deps import templates
from app.models import Account, Member, AccountType, OwnerType

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", name="accounts_list")
async def accounts_list(request: Request, session: Session = Depends(get_session)):
    accounts = session.exec(select(Account).order_by(Account.sort_order, Account.id)).all()
    members = session.exec(select(Member)).all()
    return templates.TemplateResponse(request, "accounts/list.html", {
        "accounts": accounts,
        "members": members,
        "account_types": AccountType,
        "owner_types": OwnerType,
    })


@router.post("", name="accounts_create")
async def accounts_create(
    request: Request,
    name: str = Form(...),
    type: AccountType = Form(...),
    owner_type: OwnerType = Form(...),
    owner_member_id: Optional[int] = Form(None),
    currency: str = Form("CNY"),
    note: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    account = Account(
        name=name, type=type, owner_type=owner_type,
        owner_member_id=owner_member_id if owner_type == OwnerType.member else None,
        currency=currency, note=note,
    )
    session.add(account)
    session.commit()
    accounts = session.exec(select(Account).order_by(Account.sort_order, Account.id)).all()
    members = session.exec(select(Member)).all()
    return templates.TemplateResponse(request, "partials/account_table.html", {
        "accounts": accounts,
        "members": members,
    }, headers={"HX-Trigger": "accountSaved"})


@router.get("/{account_id}/edit", name="accounts_edit_form", response_class=HTMLResponse)
async def accounts_edit_form(account_id: int, request: Request, session: Session = Depends(get_session)):
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404)
    members = session.exec(select(Member)).all()
    return templates.TemplateResponse(request, "partials/account_edit_modal.html", {
        "account": account,
        "members": members,
        "account_types": AccountType,
        "owner_types": OwnerType,
    })


@router.post("/{account_id}", name="accounts_update")
async def accounts_update(
    account_id: int,
    request: Request,
    name: str = Form(...),
    type: AccountType = Form(...),
    owner_type: OwnerType = Form(...),
    owner_member_id: Optional[int] = Form(None),
    currency: str = Form("CNY"),
    is_active: bool = Form(False),
    note: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404)
    account.name = name
    account.type = type
    account.owner_type = owner_type
    account.owner_member_id = owner_member_id if owner_type == OwnerType.member else None
    account.currency = currency
    account.is_active = is_active
    account.note = note
    session.add(account)
    session.commit()
    accounts = session.exec(select(Account).order_by(Account.sort_order, Account.id)).all()
    members = session.exec(select(Member)).all()
    return templates.TemplateResponse(request, "partials/account_table.html", {
        "accounts": accounts,
        "members": members,
    }, headers={"HX-Trigger": "accountSaved"})
