from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from utils.openai_helper import generate_fashion_image
from bot import router as bot_router
import requests
import os

# Cargar variables
load_dotenv()

# Token Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Crear app
app = FastAPI(
    title="AppFred - Fashion Image Assistant",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta raíz
@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "AppFred está funcionando 🚀"
    }

# Endpoint principal IA
@app.post("/generate")
async def generate(
    file: UploadFile,
    clothing_type: str = Form(...)
):
    result = await generate_fashion_image(file, clothing_type)
    return result

# Webhook Telegram
@app.post("/webhook")
async def telegram_webhook(request: Request):

    data = await request.json()

    try:
        message = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

        response_text = f"Recibí tu mensaje: {message}"

        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

        requests.post(
            telegram_url,
            json={
                "chat_id": chat_id,
                "text": response_text
            }
        )

    except Exception as e:
        print("Error Telegram:", e)

    return {"ok": True}

# Router adicional
app.include_router(bot_router)