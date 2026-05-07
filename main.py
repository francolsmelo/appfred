from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from utils.openai_helper import generate_fashion_image
from bot import router as bot_router

load_dotenv()

app = FastAPI(title="AppFred - Fashion Image Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "AppFred está funcionando 🚀"}

@app.post("/generate")
async def generate(file: UploadFile, clothing_type: str = Form(...)):
    """Endpoint principal para generar imagen de moda"""
    result = await generate_fashion_image(file, clothing_type)
    return result

# Webhook de Telegram
app.include_router(bot_router)