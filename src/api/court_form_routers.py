import subprocess
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

from src.services.doc_generator import generate_advocate_request_doc

router = APIRouter(prefix="/court-form", tags=["Court Form"])


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

        return {
            "success": True,
            "pdf_url": f"/media/temp/{pdf_path.name}",
            "docx_path": f"/media/temp/{docx_path.name}",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
