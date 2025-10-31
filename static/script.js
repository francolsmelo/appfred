document.getElementById("generateBtn").addEventListener("click", async () => {
  const imageInput = document.getElementById("imageInput").files[0];
  const clothingType = document.getElementById("clothingType").value;
  const output = document.getElementById("output");

  if (!imageInput) {
    alert("Por favor, sube una imagen.");
    return;
  }

  if (!clothingType) {
    alert("Por favor, indica el tipo de ropa (ej: vestido elegante).");
    return;
  }

  const formData = new FormData();
  formData.append("file", imageInput);
  formData.append("clothing_type", clothingType);

  output.innerHTML = "Generando imagen... ⏳";

  const response = await fetch("https://appfred.onrender.com/generate", {
    method: "POST",
    body: formData,
  });

  const data = await response.json();

  if (data.image) {
    const img = document.createElement("img");
    img.src = "data:image/png;base64," + data.image;
    output.innerHTML = "";
    output.appendChild(img);
  } else {
    output.innerHTML = "Error al generar la imagen 😞";
  }
});
