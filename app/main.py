from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from app.chat import router as chat_router
from app.routes.chat_htmx import router as htmx_router
from app.routes.api.chat_api import router as chat_api_router
from fastapi.staticfiles import StaticFiles
from .security.resource_manager import resource_auth_middleware

app = FastAPI()
app.middleware("http")(resource_auth_middleware)

app.mount("/static", StaticFiles(directory="app/web/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Incluir routers
app.include_router(chat_router)
app.include_router(htmx_router)
app.include_router(chat_api_router, prefix="/api")
