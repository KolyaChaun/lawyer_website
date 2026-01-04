import os
import time
from pathlib import Path

from celery import Celery

BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "media" / "temp"

MAX_AGE_SECONDS = 12 * 3600


celery_app = Celery(
    "lawyer_website",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

celery_app.conf.timezone = "Europe/Kyiv"
celery_app.conf.enable_utc = True


@celery_app.task(name="clean_temp_files")
def clean_temp_files():

    if not TEMP_DIR.exists():
        return "TEMP_DIR not found"

    deleted = 0

    for file in TEMP_DIR.iterdir():
        if file.is_file() and file.suffix in (".docx", ".pdf"):
            age = time.time() - file.stat().st_mtime
            if age > MAX_AGE_SECONDS:
                file.unlink(missing_ok=True)
                deleted += 1
                print(f"[CLEAN] File has been deleted.: {file.name}")

    return f"Deleted {deleted} files"


celery_app.conf.beat_schedule = {
    "clean-temp-every-12-hours": {
        "task": "clean_temp_files",
        "schedule": 12 * 3600,
    },
}
