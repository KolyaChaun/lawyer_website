from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.api import (contact_routers, court_form_routers, pages_routers,
                     payments_routers)
from src.core.config import BASE_DIR, PROJECT_DIR

app = FastAPI()

# Static & media
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

app.mount(
    "/media",
    StaticFiles(directory=PROJECT_DIR / "media"),
    name="media",
)

# Routers
app.include_router(pages_routers.router)
app.include_router(contact_routers.router)
app.include_router(court_form_routers.router)
app.include_router(payments_routers.router)
