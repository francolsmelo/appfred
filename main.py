from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from utils.openai_helper import generate_fashion_image
from bot import router as bot_router

# Cargar variables de entorno
load_dotenv()

# Crear aplicación FastAPI
app = FastAPI(
    title="AppFred - Fashion Image Assistant",
    version="1.0.0",
    description="API para generación de imágenes de moda con IA"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta raíz para healthcheck de Render
@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "AppFred está funcionando 🚀"
    }

# Endpoint principal
@app.post("/generate")
async def generate(
    file: UploadFile,
    clothing_type: str = Form(...)
):
    """
    Genera imágenes de moda usando IA
    """
    result = await generate_fashion_image(file, clothing_type)
    return result

# Incluir rutas del bot de Telegram
app.include_router(bot_router)