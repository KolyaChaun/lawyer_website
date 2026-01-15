import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.db.models.order import Order
from src.schemas.order_schema import OrderCreate

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/create")
async def create_order(data: OrderCreate, db: AsyncSession = Depends(get_db)):
    order_id = data.order_id or str(uuid.uuid4())

    result = await db.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalar_one_or_none()

    if order:
        if order.status == "paid":
            return {
                "order_id": order.order_id,
                "docx_path": order.docx_path,
            }

        order.docx_path = data.docx_path
        order.pdf_path = None
        await db.flush()

        return {
            "order_id": order.order_id,
            "docx_path": order.docx_path,
        }

    order = Order(
        order_id=order_id,
        docx_path=data.docx_path,
        pdf_path=None,
        amount=1000,
        currency="UAH",
        status="pending",
    )

    db.add(order)
    await db.flush()
    await db.refresh(order)

    return {
        "order_id": order.order_id,
        "docx_path": order.docx_path,
    }
