"""会员购买 + 微信登录（内存实现）"""
from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Optional

log = logging.getLogger(__name__)

TOKEN_TTL = timedelta(days=7)
ORDER_TTL = timedelta(minutes=15)
PLAN_DAYS = {"month": 31, "year": 365}
PLAN_PRICE_CENTS = {"month": 1990, "year": 19900}
WXPAY_KEY = "replace-me-in-prod"


@dataclass
class User:
    openid: str
    token: Optional[str] = None
    token_expires: Optional[datetime] = None
    member_expires: Optional[date] = None


@dataclass
class Order:
    order_id: str
    openid: str
    plan: str
    amount_cents: int
    created_at: datetime
    status: str = "pending"  # pending / paid / closed
    paid_at: Optional[datetime] = None


USERS: dict[str, User] = {}
ORDERS: dict[str, Order] = {}
TOKENS: dict[str, str] = {}  # token -> openid


# ---------- 登录 ----------

def wx_code_to_openid(code: str) -> str:
    # 真实实现调 https://api.weixin.qq.com/sns/jscode2session
    return "openid_" + hashlib.sha1(code.encode()).hexdigest()[:12]


def login(code: str, now: Optional[datetime] = None) -> str:
    now = now or datetime.now()
    openid = wx_code_to_openid(code)
    user = USERS.setdefault(openid, User(openid=openid))
    if user.token:
        TOKENS.pop(user.token, None)
    token = secrets.token_urlsafe(32)
    user.token = token
    user.token_expires = now + TOKEN_TTL
    TOKENS[token] = openid
    return token


def auth(token: str, now: Optional[datetime] = None) -> User:
    now = now or datetime.now()
    openid = TOKENS.get(token)
    if not openid:
        raise PermissionError("invalid token")
    user = USERS[openid]
    if user.token_expires and user.token_expires < now:
        raise PermissionError("token expired")
    return user


# ---------- 订单 ----------

def create_order(token: str, plan: str, now: Optional[datetime] = None) -> Order:
    now = now or datetime.now()
    user = auth(token, now)
    if plan not in PLAN_DAYS:
        raise ValueError("unknown plan")
    order = Order(
        order_id=secrets.token_hex(8),
        openid=user.openid,
        plan=plan,
        amount_cents=PLAN_PRICE_CENTS[plan],
        created_at=now,
    )
    ORDERS[order.order_id] = order
    return order


def close_expired_orders(now: Optional[datetime] = None) -> int:
    """定时任务每分钟跑一次"""
    now = now or datetime.now()
    n = 0
    for o in ORDERS.values():
        if o.status == "pending" and now - o.created_at > ORDER_TTL:
            o.status = "closed"
            n += 1
    return n


def list_orders(token: str, page: int = 1, page_size: int = 20) -> list[Order]:
    user = auth(token)
    mine = [o for o in ORDERS.values() if o.openid == user.openid]
    mine.sort(key=lambda o: o.created_at, reverse=True)
    start = (page - 1) * page_size
    return mine[start:start + page_size]


# ---------- 支付回调 ----------

def verify_sign(payload: dict, sign: str) -> bool:
    body = "&".join(f"{k}={payload[k]}" for k in sorted(payload))
    expected = hmac.new(WXPAY_KEY.encode(), body.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sign)


def _grant_membership(user: User, plan: str, today: date) -> None:
    days = PLAN_DAYS[plan]
    user.member_expires = today + timedelta(days=days)


def wxpay_callback(payload: dict, sign: str, now: Optional[datetime] = None) -> dict:
    """微信支付结果通知。返回 {"code": "SUCCESS"} 或 {"code": "FAIL", "message": ...}"""
    now = now or datetime.now()
    if not verify_sign(payload, sign):
        log.warning("wxpay callback sign mismatch, order=%s", payload.get("out_trade_no"))

    order = ORDERS.get(payload.get("out_trade_no", ""))
    if order is None:
        return {"code": "FAIL", "message": "order not found"}
    if order.status == "paid":
        return {"code": "SUCCESS"}  # 重复通知，直接确认
    if order.status == "closed":
        return {"code": "FAIL", "message": "order closed"}
    if int(payload.get("total_fee", -1)) != order.amount_cents:
        return {"code": "FAIL", "message": "amount mismatch"}

    order.status = "paid"
    order.paid_at = now
    _grant_membership(USERS[order.openid], order.plan, now.date())
    return {"code": "SUCCESS"}


# ---------- 会员状态 ----------

def member_status(token: str, today: Optional[date] = None) -> dict:
    today = today or date.today()
    user = auth(token)
    active = bool(user.member_expires and user.member_expires >= today)
    return {"is_member": active, "expires": user.member_expires.isoformat() if user.member_expires else None}
