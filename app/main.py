from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from app.chat import router as chat_router
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Incluir router del chat
app.include_router(chat_router)
