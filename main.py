from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from utils.openai_helper import generate_fashion_image
from bot import router as bot_router
from openai import OpenAI
import requests
import os

# Cargar variables de entorno
load_dotenv()

# Variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Cliente OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Crear app FastAPI
app = FastAPI(
    title="AppFred - Fashion Image Assistant",
    version="1.0.0",
    description="Asistente IA de moda conectado con Telegram y OpenAI"
)

# Configuración CORS
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

# Endpoint principal IA imágenes
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

    print("Telegram update:", data)

    try:

        # Verificar que exista mensaje
        if "message" not in data:
            return {"ok": True}

        message_data = data["message"]

        # Obtener chat ID
        chat_id = message_data["chat"]["id"]

        # Obtener texto usuario
        user_message = message_data.get(
            "text",
            "Mensaje no compatible"
        )

        # Consulta OpenAI
        completion = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres AppFred, un asistente experto "
                        "en moda, outfits, tendencias, colores "
                        "y recomendaciones de estilo."
                    )
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            max_tokens=300
        )

        # Respuesta IA
        ai_response = completion.choices[0].message.content

        # URL Telegram API
        telegram_url = (
            f"https://api.telegram.org/bot"
            f"{TELEGRAM_BOT_TOKEN}/sendMessage"
        )

        # Enviar respuesta Telegram
        telegram_response = requests.post(
            telegram_url,
            json={
                "chat_id": chat_id,
                "text": ai_response
            }
        )

        print("Telegram response:", telegram_response.text)

    except Exception as e:
        print("Error Telegram:", str(e))

    return {"ok": True}

# Router adicional
app.include_router(bot_router)