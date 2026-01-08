from pydantic import BaseModel
from typing import Optional


class OrderCreate(BaseModel):
    docx_path: str
    order_id: Optional[str] = None
