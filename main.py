from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv
from utils.openai_helper import generate_fashion_image

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("ASSISTANT_ID")

app = FastAPI(title="AppFred - Fashion Image Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Bienvenido a AppFred - Asistente de moda con IA"}

@app.post("/generate")
async def generate(file: UploadFile, clothing_type: str = Form(...)):
    """Genera una imagen de moda con el rostro proporcionado"""
    result = await generate_fashion_image(file, clothing_type)
    return result
