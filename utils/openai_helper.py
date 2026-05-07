# utils/openai_helper.py
import openai
import base64
import os
from fastapi import UploadFile
from io import BytesIO

client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_fashion_image(file: UploadFile, clothing_type: str):
    """Versión mejorada con prompt potente para preservación de rostro"""
    
    # Leer la imagen
    image_bytes = await file.read()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    # Prompt ULTRA POTENTE (esto es lo que realmente mejora la calidad)
    prompt = f"""
Eres un experto mundial en virtual fashion try-on y fotografía de alta moda.

**REFERENCIA OBLIGATORIA (mantener 100% fiel):**
- Rostro, ojos, expresión, tono de piel, textura de piel, pelo, forma de la cara y pose deben ser **idénticos** a la foto original.
- No cambies proporciones del cuerpo, edad ni iluminación general.

**TAREA:**
Cambia SOLO la ropa por: {clothing_type}

**Estilo y calidad:**
- Photorealistic, 8k, ultra detallado, vogue editorial style
- Telas con física realista (draping, pliegues, brillos, caídas naturales)
- Sombras y luces que coincidan perfectamente con la foto original
- Alta costura, detalles premium, acabado profesional

Genera una imagen espectacular lista para Instagram o revista de moda.
"""

    try:
        response = await client.images.generate(
            model="gpt-image-1",          # o "dall-e-3" si prefieres
            prompt=prompt,
            n=1,
            size="1024x1024",             # o "1792x1024" para landscape
            quality="hd",
            response_format="b64_json"
        )
        
        image_b64 = response.data[0].b64_json
        
        return {
            "status": "success",
            "image": image_b64,
            "message": f"¡Listo! Tu {clothing_type}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error en generación: {str(e)}"
        }