import base64
import hashlib
import json
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from src.api.court_form_routers import TEMP_ORDERS
from src.core.config import LIQPAY_PRIVATE_KEY, LIQPAY_PUBLIC_KEY
from src.services.liqpay import generate_liqpay_form
from src.services.telegram import send_telegram_message_docx

router = APIRouter(prefix="/liqpay", tags=["Payments"])


@router.post("/pay", response_class=HTMLResponse)
async def liqpay_pay(request: Request):
    form = await request.form()
    order_id = form.get("order_id")

    if not order_id or order_id not in TEMP_ORDERS:
        raise HTTPException(status_code=400, detail="Invalid order_id")

    params = {
        "public_key": LIQPAY_PUBLIC_KEY,
        "version": "3",
        "action": "pay",
        "amount": "1000",
        "currency": "UAH",
        "description": "Адвокатський запит",
        "order_id": order_id,
        "sandbox": "1",
        "result_url": "https://frightenable-uninterruptive-nolan.ngrok-free.dev/payment/success",
        "server_url": "https://frightenable-uninterruptive-nolan.ngrok-free.dev/liqpay/callback",
    }

    return generate_liqpay_form(params, LIQPAY_PUBLIC_KEY, LIQPAY_PRIVATE_KEY)


@router.post("/callback")
async def liqpay_callback(request: Request):
    body = await request.form()
    data = body.get("data")
    signature = body.get("signature")

    expected_signature = base64.b64encode(
        hashlib.sha1((LIQPAY_PRIVATE_KEY + data + LIQPAY_PRIVATE_KEY).encode()).digest()
    ).decode()

    if signature != expected_signature:
        raise HTTPException(status_code=400, detail="Invalid signature")

    payment_data = json.loads(base64.b64decode(data).decode())

    if payment_data.get("status") in ("success", "sandbox"):
        order = TEMP_ORDERS.pop(payment_data["order_id"], None)
        if order:

            docx_path = Path(order["docx_path"])
            pdf_path = docx_path.with_suffix(".pdf")

            await send_telegram_message_docx(
                docx_path=order["docx_path"],
                caption="Адвокатський запит",
            )

            if docx_path.exists():
                os.remove(docx_path)
                print(f"[PAYMENT CLEAN] Deleted {docx_path.name}")

            if pdf_path.exists():
                os.remove(pdf_path)
                print(f"[PAYMENT CLEAN] Deleted {pdf_path.name}")

    return {"status": "ok"}
