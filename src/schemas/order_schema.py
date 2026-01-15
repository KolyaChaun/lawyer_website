from typing import Optional

from pydantic import BaseModel


class OrderCreate(BaseModel):
    docx_path: str
    order_id: Optional[str] = None
