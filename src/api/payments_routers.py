import base64
import hashlib
import json
import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.order_routers import get_db
from src.core.config import LIQPAY_PRIVATE_KEY, LIQPAY_PUBLIC_KEY
from src.db.database import AsyncSessionLocal
from src.db.models.order import Order
from src.services.liqpay import generate_liqpay_form
from src.services.telegram import send_telegram_message_docx

router = APIRouter(prefix="/liqpay", tags=["Payments"])


@router.post("/pay", response_class=HTMLResponse)
async def liqpay_pay(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        form = await request.form()
        order_id = form.get("order_id")
    except Exception:
        order_id = None

    if not order_id:
        try:
            data = await request.json()
            order_id = data.get("order_id")
        except Exception:
            order_id = None

    if not order_id:
        raise HTTPException(status_code=400, detail="Missing order_id")

    result = await db.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if not order.docx_path:
        raise HTTPException(status_code=400, detail="Missing docx_path")

    params = {
        "public_key": LIQPAY_PUBLIC_KEY,
        "version": "3",
        "action": "pay",
        "amount": str(order.amount),
        "currency": order.currency,
        "description": "Адвокатський запит",
        "order_id": order.order_id,
        "sandbox": "1",
        "result_url": "https://frightenable-uninterruptive-nolan.ngrok-free.dev/payment/success",
        "server_url": "https://frightenable-uninterruptive-nolan.ngrok-free.dev/liqpay/callback",
    }

    return generate_liqpay_form(params, LIQPAY_PUBLIC_KEY, LIQPAY_PRIVATE_KEY)


@router.post("/callback")
async def liqpay_callback(request: Request):
    try:
        form = await request.form()
        data = form.get("data")
        signature = form.get("signature")

        if not data or not signature:
            raise HTTPException(status_code=400, detail="Missing data or signature")

        expected_signature = base64.b64encode(
            hashlib.sha1(
                (LIQPAY_PRIVATE_KEY + data + LIQPAY_PRIVATE_KEY).encode()
            ).digest()
        ).decode()

        if signature != expected_signature:
            raise HTTPException(status_code=400, detail="Invalid signature")

        payment_data = json.loads(base64.b64decode(data).decode())
        order_id = payment_data.get("order_id")
        if not order_id:
            raise HTTPException(
                status_code=400, detail="Missing order_id in payment data"
            )

        async with AsyncSessionLocal() as session:
            async with session.begin():
                result = await session.execute(
                    select(Order).where(Order.order_id == order_id)
                )
                order = result.scalars().first()

                if not order:
                    raise HTTPException(status_code=404, detail="Order not found")

                if payment_data.get("status") in ("success", "sandbox"):
                    order.status = "success"
                    order.paid_at = datetime.utcnow()
                    await session.flush()

        try:
            absolute_path = os.path.join(
                os.getcwd(), "media/temp", os.path.basename(order.docx_path)
            )
            await send_telegram_message_docx(
                docx_path=absolute_path, caption="Адвокатський запит"
            )
        except Exception as e:
            print(f"[TELEGRAM ERROR] {e}")

        return {"status": "ok"}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
