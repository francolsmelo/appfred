# bot.py
import os
import requests
import base64
from fastapi import Request, APIRouter
from fastapi.responses import JSONResponse

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
FILE_API = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}"

_pending_photos = {}
router = APIRouter()

def send_message(chat_id: int, text: str):
    requests.post(f"{TELEGRAM_API}/sendMessage", 
                 json={"chat_id": chat_id, "text": text}, 
                 timeout=30)

def send_photo_bytes(chat_id: int, photo_bytes: bytes, caption=None):
    url = f"{TELEGRAM_API}/sendPhoto"
    files = {"photo": ("result.png", photo_bytes)}
    data = {"chat_id": chat_id}
    if caption:
        data["caption"] = caption
    requests.post(url, files=files, data=data, timeout=90)

async def call_generate_endpoint(file_bytes: bytes, clothing_type: str, backend_base_url: str):
    url = f"{backend_base_url.rstrip('/')}/generate"
    files = {"file": ("photo.jpg", file_bytes)}
    data = {"clothing_type": clothing_type}
    
    resp = requests.post(url, files=files, data=data, timeout=180)  # ← Aumentado
    resp.raise_for_status()
    return resp.json()

@router.post("/telegram_webhook")
async def telegram_webhook(request: Request):
    body = await request.json()
    if "message" not in body:
        return JSONResponse({"ok": True})

    msg = body["message"]
    chat_id = msg["chat"]["id"]

    # Usuario envía foto
    if "photo" in msg:
        photo_list = msg["photo"]
        file_id = photo_list[-1]["file_id"]

        r = requests.get(f"{TELEGRAM_API}/getFile", params={"file_id": file_id}, timeout=30)
        file_path = r.json()["result"]["file_path"]

        fr = requests.get(f"{FILE_API}/{file_path}", timeout=60)
        file_bytes = fr.content

        caption = msg.get("caption", "").strip()

        if caption:
            send_message(chat_id, f"Generando tu {caption}... 🔥")
            try:
                backend_url = os.getenv("BACKEND_BASE_URL", "https://appfred.onrender.com")
                result = await call_generate_endpoint(file_bytes, caption, backend_url)
                
                if result.get("status") == "success":
                    image_bytes = base64.b64decode(result["image"])
                    send_photo_bytes(chat_id, image_bytes, caption=f"✅ Tu {caption}")
                else:
                    send_message(chat_id, result.get("message", "Error desconocido"))
            except Exception as e:
                send_message(chat_id, f"Error: {str(e)}")
        else:
            _pending_photos[chat_id] = file_bytes
            send_message(chat_id, "✅ Foto recibida.\n\nAhora dime qué quieres ponerte (ej: vestido de gala rojo elegante, traje negro formal, etc.)")

    # Usuario envía texto (descripción de ropa)
    elif "text" in msg:
        text = msg["text"].strip()
        if chat_id in _pending_photos:
            file_bytes = _pending_photos.pop(chat_id)
            send_message(chat_id, f"✨ Generando tu '{text}'... esto va a quedar brutal")
            try:
                backend_url = os.getenv("BACKEND_BASE_URL", "https://appfred.onrender.com")
                result = await call_generate_endpoint(file_bytes, text, backend_url)
                
                if result.get("status") == "success":
                    image_bytes = base64.b64decode(result["image"])
                    send_photo_bytes(chat_id, image_bytes, caption=f"✅ Tu {text}")
                else:
                    send_message(chat_id, result.get("message", "Error al generar"))
            except Exception as e:
                send_message(chat_id, f"Error generando imagen: {str(e)}")
        else:
            send_message(chat_id, "Primero envíame una foto clara tuya y luego dime la prenda.")

    return JSONResponse({"ok": True})