import uuid
from datetime import datetime

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    status: Mapped[str] = mapped_column(String, default="created")
    docx_path: Mapped[str]
    pdf_path: Mapped[str | None]
    amount: Mapped[int] = mapped_column(default=1000)
    currency: Mapped[str] = mapped_column(default="UAH")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    paid_at: Mapped[datetime | None] = mapped_column(default=None)
