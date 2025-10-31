# appfred/backend/bot.py
import os
import requests
import base64
from fastapi import Request, APIRouter
from fastapi.responses import JSONResponse

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
FILE_API = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}"

# In-memory store for pending photos: {chat_id: bytes}
_pending_photos = {}

router = APIRouter()

def send_message(chat_id: int, text: str):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload, timeout=30)

def send_photo_bytes(chat_id: int, photo_bytes: bytes, filename="result.png", caption=None):
    url = f"{TELEGRAM_API}/sendPhoto"
    files = {"photo": (filename, photo_bytes)}
    data = {"chat_id": chat_id}
    if caption:
        data["caption"] = caption
    requests.post(url, files=files, data=data, timeout=60)

async def call_generate_endpoint(file_bytes: bytes, clothing_type: str, backend_base_url: str):
    """
    Llama a tu endpoint /generate (que espera multipart form-data)
    backend_base_url ejemplo: https://appfred.onrender.com
    """
    url = f"{backend_base_url.rstrip('/')}/generate"
    files = {"file": ("photo.jpg", file_bytes)}
    data = {"clothing_type": clothing_type}
    resp = requests.post(url, files=files, data=data, timeout=120)
    resp.raise_for_status()
    return resp.json()

@router.post("/telegram_webhook")
async def telegram_webhook(request: Request):
    """
    Endpoint para recibir updates de Telegram en formato JSON.
    Debes configurar el webhook en BotFather a:
      https://appfred.onrender.com/telegram_webhook
    """
    body = await request.json()
    # Basic safety:
    if "message" not in body:
        return JSONResponse({"ok": True})

    msg = body["message"]
    chat_id = msg["chat"]["id"]

    # 1) Si el usuario envía una foto:
    if "photo" in msg:
        # Telegram envía varias resoluciones, la última es la más grande
        photo_list = msg["photo"]
        file_id = photo_list[-1]["file_id"]
        # Obtener file path
        r = requests.get(f"{TELEGRAM_API}/getFile", params={"file_id": file_id}, timeout=30)
        r.raise_for_status()
        file_path = r.json().get("result", {}).get("file_path")
        if not file_path:
            send_message(chat_id, "No pude obtener la imagen. Intenta de nuevo.")
            return JSONResponse({"ok": True})

        # Descargar archivo
        file_url = f"{FILE_API}/{file_path}"
        fr = requests.get(file_url, timeout=60)
        fr.raise_for_status()
        file_bytes = fr.content

        # Si el usuario puso caption que indica tipo de prenda, la usamos:
        caption = msg.get("caption", "").strip()
        if caption:
            send_message(chat_id, "Recibida la foto. Generando imagen, un momento...")
            try:
                backend_url = os.getenv("BACKEND_BASE_URL", "https://appfred.onrender.com")
                result = await call_generate_endpoint(file_bytes, caption, backend_url)
                if "image" in result:
                    image_b64 = result["image"]
                    image_bytes = base64.b64decode(image_b64)
                    send_photo_bytes(chat_id, image_bytes, caption=f"Tu {caption}")
                else:
                    send_message(chat_id, "Hubo un error al generar la imagen.")
            except Exception as e:
                send_message(chat_id, f"Error generando imagen: {str(e)}")
            return JSONResponse({"ok": True})
        else:
            # Guardamos temporalmente la foto y pedimos tipo de prenda
            _pending_photos[chat_id] = file_bytes
            send_message(chat_id, "Foto recibida. Ahora envíame el tipo de prenda (ej: 'terno elegante' o 'vestido de gala').")
            return JSONResponse({"ok": True})

    # 2) Si el usuario envía texto (posible tipo de prenda)
    if "text" in msg:
        text = msg["text"].strip()
        # Comprueba si hay foto pendiente para este chat
        if chat_id in _pending_photos:
            file_bytes = _pending_photos.pop(chat_id)
            send_message(chat_id, f"Generando tu '{text}', espera un momento...")
            try:
                backend_url = os.getenv("BACKEND_BASE_URL", "https://appfred.onrender.com")
                result = await call_generate_endpoint(file_bytes, text, backend_url)
                if "image" in result:
                    image_b64 = result["image"]
                    image_bytes = base64.b64decode(image_b64)
                    send_photo_bytes(chat_id, image_bytes, caption=f"Tu {text}")
                else:
                    send_message(chat_id, "Hubo un error al generar la imagen.")
            except Exception as e:
                send_message(chat_id, f"Error generando imagen: {str(e)}")
            return JSONResponse({"ok": True})
        else:
            # Si no hay foto pendiente, ofrecer instrucciones
            send_message(chat_id, "No tengo una foto tuya. Por favor envíame primero una foto clara del rostro y luego el tipo de prenda.")
            return JSONResponse({"ok": True})

    # otros tipos de mensajes no tratados
    return JSONResponse({"ok": True})