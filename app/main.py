from fastapi import FastAPI
from app.chat import router as chat_router

app = FastAPI()

# Rutas principales
@app.get("/")
def read_root():
    return {"message": "¡Hola, Sebastián! El agente está vivo."}

# Incluir router del chat
app.include_router(chat_router)
