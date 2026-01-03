from typing import Optional

from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates

from src.core.config import BASE_DIR
from src.services.telegram import send_telegram_message

router = APIRouter(prefix="/contact", tags=["Contact"])
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@router.post("/submit")
async def submit_contact(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    email: Optional[str] = Form(None),
    message: Optional[str] = Form(None),
):
    text = (
        "Заявка на консультацію!\n"
        f"Ім'я: {name}\n"
        f"Телефон: {phone}\n"
        f"Email: {email or 'не вказано'}\n"
        f"Повідомлення: {message or 'без опису проблеми'}"
    )

    await send_telegram_message(text)

    return templates.TemplateResponse(
        "contact.html",
        {"request": request, "success": "Дякуємо! Ваше повідомлення надіслано."},
    )
