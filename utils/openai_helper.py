import openai
import base64

async def generate_fashion_image(file, clothing_type):
    image_bytes = await file.read()
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    prompt = f"Genera una imagen de una persona con el rostro proporcionado vistiendo un {clothing_type}."

    response = openai.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        image=encoded_image,
        size="1024x1024"
    )

    image_base64 = response.data[0].b64_json
    return {"image": image_base64}
