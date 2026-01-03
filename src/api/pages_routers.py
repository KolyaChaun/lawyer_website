from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from src.core.config import BASE_DIR

router = APIRouter()
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/form")
async def form(request: Request):
    return templates.TemplateResponse("court_form.html", {"request": request})


@router.get("/contact")
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@router.get("/contract")
async def contract(request: Request):
    return templates.TemplateResponse("dogovor.html", {"request": request})


@router.get("/payment/success")
async def payment_success(request: Request):
    return templates.TemplateResponse("payment_success.html", {"request": request})

