# ============================================================
# Taller - Explorando el Universo Latente
# Introducción a Stable Diffusion con Diffusers
# ============================================================

# ============================================================
# 1. INSTALACIÓN DE DEPENDENCIAS
# ============================================================

# pip install diffusers transformers accelerate torch --upgrade

# ============================================================
# 2. IMPORTAR LIBRERÍAS
# ============================================================

from diffusers import StableDiffusionPipeline
import torch
import matplotlib.pyplot as plt

# ============================================================
# 3. CONFIGURACIÓN DEL DISPOSITIVO
# ============================================================

device = "cuda" if torch.cuda.is_available() else "cpu"

print("Dispositivo utilizado:", device)

# ============================================================
# 4. CARGAR MODELO PREENTRENADO
# ============================================================

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16 if device == "cuda" else torch.float32
)

pipe = pipe.to(device)

# ============================================================
# 5. FUNCIÓN PARA GENERAR IMÁGENES
# ============================================================

def generar_imagen(
    prompt,
    nombre_archivo,
    negative_prompt=None,
    steps=50,
    guidance=7.5,
    width=512,
    height=512,
    seed=None
):
    """
    Genera una imagen usando Stable Diffusion.
    """

    generator = None

    if seed is not None:
        generator = torch.Generator(device).manual_seed(seed)

    image = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=steps,
        guidance_scale=guidance,
        width=width,
        height=height,
        generator=generator
    ).images[0]

    image.save(nombre_archivo)

    print(f"Imagen guardada: {nombre_archivo}")

    return image

# ============================================================
# 6. GENERAR PRIMERA IMAGEN
# ============================================================

prompt_1 = "A surreal futuristic city in the clouds, digital art"

imagen_1 = generar_imagen(
    prompt=prompt_1,
    nombre_archivo="output.png",
    steps=50,
    guidance=7.5,
    seed=42
)

imagen_1.show()

# ============================================================
# 7. EJEMPLO CYBERPUNK
# ============================================================

prompt_2 = "Cyberpunk samurai in Tokyo at night, neon lights, ultra detailed"

imagen_2 = generar_imagen(
    prompt=prompt_2,
    nombre_archivo="cyberpunk.png",
    steps=40,
    guidance=8,
    seed=10
)

imagen_2.show()

# ============================================================
# 8. EJEMPLO PINTURA AL ÓLEO
# ============================================================

prompt_3 = "A medieval castle in the mountains, oil painting style"

imagen_3 = generar_imagen(
    prompt=prompt_3,
    nombre_archivo="oil_painting.png",
    steps=50,
    guidance=7.5,
    seed=20
)

imagen_3.show()

# ============================================================
# 9. EJEMPLO FOTORREALISTA
# ============================================================

prompt_4 = "Photorealistic astronaut riding a horse on Mars"

imagen_4 = generar_imagen(
    prompt=prompt_4,
    nombre_archivo="photorealistic.png",
    steps=60,
    guidance=9,
    seed=30
)

imagen_4.show()

# ============================================================
# 10. USO DE PROMPTS NEGATIVOS
# ============================================================

prompt_5 = "A beautiful futuristic car"

negative_prompt = "blurry, low quality, distorted, ugly"

imagen_5 = generar_imagen(
    prompt=prompt_5,
    nombre_archivo="negative_prompt_example.png",
    negative_prompt=negative_prompt,
    steps=50,
    guidance=8,
    seed=100
)

imagen_5.show()

# ============================================================
# 11. GENERAR VARIANTES DE UNA ESCENA
# ============================================================

base_prompt = "A dragon flying over a fantasy city"

variantes = []

for i in range(3):

    imagen = generar_imagen(
        prompt=base_prompt,
        nombre_archivo=f"dragon_variant_{i}.png",
        steps=40,
        guidance=7.5,
        seed=i
    )

    variantes.append(imagen)

# ============================================================
# 12. CREAR GALERÍA CON MATPLOTLIB
# ============================================================

prompts_galeria = [
    "A futuristic robot painter",
    "A fantasy forest with glowing trees",
    "A sci-fi spaceship interior",
    "An ancient temple underwater"
]

imagenes_galeria = []

for i, prompt in enumerate(prompts_galeria):

    imagen = generar_imagen(
        prompt=prompt,
        nombre_archivo=f"gallery_{i}.png",
        steps=30,
        guidance=7.5,
        seed=i + 50
    )

    imagenes_galeria.append(imagen)

# Mostrar galería

fig, axes = plt.subplots(2, 2, figsize=(10, 10))

for ax, img, titulo in zip(axes.flatten(), imagenes_galeria, prompts_galeria):

    ax.imshow(img)
    ax.set_title(titulo)
    ax.axis("off")

plt.tight_layout()
plt.show()

# ============================================================
# 13. GENERACIÓN POR LOTES
# ============================================================

prompt_batch = "A futuristic city at sunset"

imagenes_batch = pipe(
    [prompt_batch] * 4,
    num_inference_steps=40,
    guidance_scale=7.5
).images

for i, img in enumerate(imagenes_batch):

    nombre = f"batch_image_{i}.png"

    img.save(nombre)

    print(f"Imagen batch guardada: {nombre}")

# ============================================================
# 14. COMPARACIÓN DE PROMPT ENGINEERING
# ============================================================

prompts_engineering = [
    "A cat",
    "A realistic fluffy cat with blue eyes",
    "A photorealistic fluffy cat with blue eyes sitting near a window, cinematic lighting"
]

imagenes_engineering = []

for i, prompt in enumerate(prompts_engineering):

    imagen = generar_imagen(
        prompt=prompt,
        nombre_archivo=f"engineering_{i}.png",
        steps=40,
        guidance=8,
        seed=200 + i
    )

    imagenes_engineering.append(imagen)

# Mostrar comparación

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for ax, img, titulo in zip(axes, imagenes_engineering, prompts_engineering):

    ax.imshow(img)
    ax.set_title(titulo)
    ax.axis("off")

plt.tight_layout()
plt.show()