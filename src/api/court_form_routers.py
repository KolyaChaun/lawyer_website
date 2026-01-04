import subprocess
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

from src.services.doc_generator import generate_advocate_request_doc

router = APIRouter(prefix="/court-form", tags=["Court Form"])

TEMP_ORDERS: dict[str, dict] = {}


@router.post("/submit")
async def submit_court_form(request: Request):
    try:
        form_data = await request.json()

        docx_path = Path(generate_advocate_request_doc(form_data))
        pdf_path = docx_path.with_suffix(".pdf")

        subprocess.run(
            [
                "soffice",
                "--headless",
                "--convert-to",
                "pdf",
                str(docx_path),
                "--outdir",
                str(docx_path.parent),
            ],
            check=True,
        )

        order_id = str(uuid.uuid4())
        TEMP_ORDERS[order_id] = {
            "docx_path": str(docx_path),
            "form_data": form_data,
        }

        return {
            "success": True,
            "pdf_url": f"/media/temp/{pdf_path.name}",
            "order_id": order_id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
