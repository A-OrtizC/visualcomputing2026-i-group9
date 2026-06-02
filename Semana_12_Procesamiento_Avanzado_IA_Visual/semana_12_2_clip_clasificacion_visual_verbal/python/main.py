"""
Taller: Visual y Verbal - Clasificación de Imágenes con CLIP
=============================================================

Este script demuestra el uso del modelo CLIP (Contrastive Language-Image Pre-training)
de OpenAI para clasificar imágenes utilizando descripciones en lenguaje natural,
sin necesidad de entrenamiento adicional (zero-shot classification).

Autores:
    - Brayan Alejandro Muñoz Pérez (bmunozp@unal.edu.co)
    - Álvaro Andrés Romero Castro (alromeroca@unal.edu.co)
    - Juan Camilo Lopez Bustos (juclopezbu@unal.edu.co)
    - Alejandro Ortiz Cortes (alortizco@unal.edu.co)

Fecha: 01 de junio de 2026
"""

import os
import clip
import torch
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# ==============================================================================
# Configuración global
# ==============================================================================

# Directorio base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
MEDIA_DIR = os.path.join(BASE_DIR, "..", "media")

# Crear directorio de media si no existe
os.makedirs(MEDIA_DIR, exist_ok=True)

# Configurar estilo visual de matplotlib
plt.rcParams.update({
    "figure.facecolor": "#1a1a2e",
    "axes.facecolor": "#16213e",
    "axes.edgecolor": "#e94560",
    "axes.labelcolor": "#eaeaea",
    "text.color": "#eaeaea",
    "xtick.color": "#eaeaea",
    "ytick.color": "#eaeaea",
    "font.family": "sans-serif",
    "font.size": 11,
})

# Paleta de colores para las barras de probabilidad
BAR_COLORS = [
    "#e94560", "#0f3460", "#533483", "#00b4d8",
    "#06d6a0", "#ffd166", "#ef476f", "#118ab2",
    "#073b4c", "#8338ec",
]


# ==============================================================================
# 1. Cargar el modelo CLIP y seleccionar dispositivo
# ==============================================================================

def load_clip_model(model_name: str = "ViT-B/32"):
    """
    Carga el modelo CLIP y el preprocesador de imágenes.

    Args:
        model_name: Nombre del modelo CLIP a cargar (ej: "ViT-B/32", "ViT-B/16").

    Returns:
        model: Modelo CLIP cargado.
        preprocess: Función de preprocesamiento de imágenes.
        device: Dispositivo utilizado ("cuda" o "cpu").
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[INFO] Dispositivo seleccionado: {device}")
    print(f"[INFO] Cargando modelo CLIP: {model_name}...")

    model, preprocess = clip.load(model_name, device=device)

    print(f"[INFO] Modelo cargado exitosamente.")
    print(f"[INFO] Resolución de entrada: {model.visual.input_resolution}")
    return model, preprocess, device


# ==============================================================================
# 2. Clasificación de una imagen individual
# ==============================================================================

def classify_single_image(
    image_path: str,
    labels: list[str],
    model,
    preprocess,
    device: str,
) -> tuple[np.ndarray, list[str]]:
    """
    Clasifica una imagen contra un conjunto de etiquetas de texto usando CLIP.

    Args:
        image_path: Ruta a la imagen.
        labels: Lista de etiquetas de texto para comparar.
        model: Modelo CLIP cargado.
        preprocess: Función de preprocesamiento.
        device: Dispositivo ("cuda" o "cpu").

    Returns:
        probs: Array de probabilidades para cada etiqueta.
        labels: Lista de etiquetas (misma entrada).
    """
    # Cargar y preprocesar la imagen
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)

    # Tokenizar las etiquetas de texto
    text = clip.tokenize(labels).to(device)

    # Obtener embeddings y calcular similitud
    with torch.no_grad():
        image_features = model.encode_image(image)
        text_features = model.encode_text(text)

        # Calcular similitud coseno (logits)
        logits_per_image, logits_per_text = model(image, text)

        # Convertir a probabilidades con softmax
        probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]

    return probs, labels


# ==============================================================================
# 3. Visualización de resultados
# ==============================================================================

def visualize_classification(
    image_path: str,
    labels: list[str],
    probs: np.ndarray,
    title: str = "CLIP Classification",
    save_path: str | None = None,
):
    """
    Visualiza la imagen junto con un gráfico de barras de probabilidades.

    Args:
        image_path: Ruta a la imagen clasificada.
        labels: Lista de etiquetas.
        probs: Array de probabilidades.
        title: Título del gráfico.
        save_path: Ruta donde guardar la imagen (opcional).
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw={"width_ratios": [1, 1.3]})

    # --- Panel izquierdo: imagen ---
    img = Image.open(image_path)
    axes[0].imshow(img)
    axes[0].axis("off")

    # Etiqueta de predicción más probable
    best_idx = np.argmax(probs)
    best_label = labels[best_idx]
    best_prob = probs[best_idx]
    axes[0].set_title(
        f'Predicción: "{best_label}" ({best_prob:.1%})',
        fontsize=13,
        fontweight="bold",
        color="#06d6a0",
        pad=10,
    )

    # --- Panel derecho: barras de probabilidad ---
    sorted_indices = np.argsort(probs)
    sorted_labels = [labels[i] for i in sorted_indices]
    sorted_probs = probs[sorted_indices]
    colors = [BAR_COLORS[i % len(BAR_COLORS)] for i in range(len(sorted_labels))]

    bars = axes[1].barh(sorted_labels, sorted_probs, color=colors, edgecolor="#eaeaea", linewidth=0.5)
    axes[1].set_xlim(0, 1.0)
    axes[1].set_xlabel("Probabilidad", fontsize=12)
    axes[1].set_title("Distribución de probabilidades", fontsize=13, fontweight="bold", pad=10)

    # Añadir porcentaje al final de cada barra
    for bar, prob in zip(bars, sorted_probs):
        axes[1].text(
            bar.get_width() + 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"{prob:.1%}",
            va="center",
            fontsize=10,
            color="#eaeaea",
        )

    # Estilo del gráfico
    axes[1].spines["top"].set_visible(False)
    axes[1].spines["right"].set_visible(False)
    axes[1].tick_params(axis="y", labelsize=10)

    fig.suptitle(title, fontsize=15, fontweight="bold", color="#e94560", y=1.02)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"[SAVED] {save_path}")

    plt.close(fig)


# ==============================================================================
# 4. Clasificación por lote (Bonus)
# ==============================================================================

def classify_batch(
    image_paths: list[str],
    labels: list[str],
    model,
    preprocess,
    device: str,
    title: str = "Batch Classification",
    save_path: str | None = None,
):
    """
    Clasifica múltiples imágenes contra un mismo conjunto de etiquetas y
    muestra los resultados en una cuadrícula.

    Args:
        image_paths: Lista de rutas a imágenes.
        labels: Lista de etiquetas de texto.
        model: Modelo CLIP.
        preprocess: Función de preprocesamiento.
        device: Dispositivo.
        title: Título general.
        save_path: Ruta donde guardar el resultado.
    """
    n = len(image_paths)
    fig, axes = plt.subplots(2, n, figsize=(5 * n, 8))

    # Si solo hay una imagen, asegurar que axes sea 2D
    if n == 1:
        axes = axes.reshape(2, 1)

    all_probs = []

    for i, img_path in enumerate(image_paths):
        probs, _ = classify_single_image(img_path, labels, model, preprocess, device)
        all_probs.append(probs)

        # --- Fila superior: imágenes ---
        img = Image.open(img_path)
        axes[0, i].imshow(img)
        axes[0, i].axis("off")

        best_idx = np.argmax(probs)
        axes[0, i].set_title(
            f'"{labels[best_idx]}" ({probs[best_idx]:.1%})',
            fontsize=11,
            fontweight="bold",
            color="#06d6a0",
            pad=8,
        )

        # --- Fila inferior: barras ---
        sorted_idx = np.argsort(probs)
        sorted_labels_i = [labels[j] for j in sorted_idx]
        sorted_probs_i = probs[sorted_idx]
        colors = [BAR_COLORS[j % len(BAR_COLORS)] for j in range(len(sorted_labels_i))]

        axes[1, i].barh(sorted_labels_i, sorted_probs_i, color=colors, edgecolor="#eaeaea", linewidth=0.5)
        axes[1, i].set_xlim(0, 1.0)
        axes[1, i].tick_params(axis="y", labelsize=8)
        axes[1, i].spines["top"].set_visible(False)
        axes[1, i].spines["right"].set_visible(False)

        # Porcentajes en las barras
        for idx_bar, (label_val, prob_val) in enumerate(zip(sorted_labels_i, sorted_probs_i)):
            axes[1, i].text(
                prob_val + 0.02, idx_bar, f"{prob_val:.1%}",
                va="center", fontsize=8, color="#eaeaea",
            )

    fig.suptitle(title, fontsize=16, fontweight="bold", color="#e94560", y=1.02)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"[SAVED] {save_path}")

    plt.close(fig)

    return all_probs


# ==============================================================================
# 5. Comparación de estilos de prompts
# ==============================================================================

def compare_prompt_styles(
    image_path: str,
    prompt_sets: dict[str, list[str]],
    model,
    preprocess,
    device: str,
    image_name: str = "image",
    save_path: str | None = None,
):
    """
    Compara diferentes estilos de prompts sobre una misma imagen.
    Muestra la imagen una vez y múltiples gráficos de barras lado a lado.

    Args:
        image_path: Ruta a la imagen.
        prompt_sets: Diccionario {nombre_del_estilo: [lista_de_etiquetas]}.
        model: Modelo CLIP.
        preprocess: Función de preprocesamiento.
        device: Dispositivo.
        image_name: Nombre descriptivo de la imagen.
        save_path: Ruta para guardar.
    """
    n_sets = len(prompt_sets)
    fig, axes = plt.subplots(1, n_sets + 1, figsize=(5 * (n_sets + 1), 5),
                              gridspec_kw={"width_ratios": [1] + [1.2] * n_sets})

    # --- Imagen ---
    img = Image.open(image_path)
    axes[0].imshow(img)
    axes[0].axis("off")
    axes[0].set_title(f"Imagen: {image_name}", fontsize=12, fontweight="bold", pad=10)

    # --- Un gráfico de barras por cada estilo de prompt ---
    for idx, (style_name, labels) in enumerate(prompt_sets.items()):
        probs, _ = classify_single_image(image_path, labels, model, preprocess, device)

        sorted_indices = np.argsort(probs)
        sorted_labels = [labels[j] for j in sorted_indices]
        sorted_probs = probs[sorted_indices]
        colors = [BAR_COLORS[j % len(BAR_COLORS)] for j in range(len(sorted_labels))]

        ax = axes[idx + 1]
        ax.barh(sorted_labels, sorted_probs, color=colors, edgecolor="#eaeaea", linewidth=0.5)
        ax.set_xlim(0, 1.0)
        ax.set_title(style_name, fontsize=12, fontweight="bold", color="#00b4d8", pad=10)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="y", labelsize=9)

        for bar_rect, prob_val in zip(ax.patches, sorted_probs):
            ax.text(
                bar_rect.get_width() + 0.02,
                bar_rect.get_y() + bar_rect.get_height() / 2,
                f"{prob_val:.1%}",
                va="center", fontsize=9, color="#eaeaea",
            )

    fig.suptitle(
        f"Comparación de estilos de prompt — {image_name}",
        fontsize=14, fontweight="bold", color="#e94560", y=1.02,
    )
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"[SAVED] {save_path}")

    plt.close(fig)


# ==============================================================================
# 6. Experimento con prompts ambiguos/subjetivos
# ==============================================================================

def experiment_ambiguous_prompts(
    image_paths: list[str],
    image_names: list[str],
    ambiguous_labels: list[str],
    model,
    preprocess,
    device: str,
    save_path: str | None = None,
):
    """
    Prueba prompts ambiguos o subjetivos en múltiples imágenes y muestra
    cómo CLIP interpreta conceptos abstractos.

    Args:
        image_paths: Lista de rutas a imágenes.
        image_names: Nombres descriptivos de cada imagen.
        ambiguous_labels: Lista de etiquetas ambiguas/subjetivas.
        model: Modelo CLIP.
        preprocess: Función de preprocesamiento.
        device: Dispositivo.
        save_path: Ruta para guardar.
    """
    n = len(image_paths)
    fig, axes = plt.subplots(2, n, figsize=(5 * n, 9))

    if n == 1:
        axes = axes.reshape(2, 1)

    for i, (img_path, img_name) in enumerate(zip(image_paths, image_names)):
        probs, _ = classify_single_image(img_path, ambiguous_labels, model, preprocess, device)

        # Imagen
        img = Image.open(img_path)
        axes[0, i].imshow(img)
        axes[0, i].axis("off")
        axes[0, i].set_title(img_name, fontsize=11, fontweight="bold", pad=8)

        # Barras
        sorted_idx = np.argsort(probs)
        sorted_labels = [ambiguous_labels[j] for j in sorted_idx]
        sorted_probs = probs[sorted_idx]
        colors = [BAR_COLORS[j % len(BAR_COLORS)] for j in range(len(sorted_labels))]

        axes[1, i].barh(sorted_labels, sorted_probs, color=colors, edgecolor="#eaeaea", linewidth=0.5)
        axes[1, i].set_xlim(0, 1.0)
        axes[1, i].tick_params(axis="y", labelsize=8)
        axes[1, i].spines["top"].set_visible(False)
        axes[1, i].spines["right"].set_visible(False)

        best_idx = np.argmax(probs)
        axes[0, i].text(
            0.5, -0.05,
            f'→ "{ambiguous_labels[best_idx]}" ({probs[best_idx]:.1%})',
            transform=axes[0, i].transAxes,
            ha="center", fontsize=10, color="#06d6a0", fontweight="bold",
        )

    fig.suptitle(
        "Experimento: Prompts Ambiguos y Subjetivos",
        fontsize=15, fontweight="bold", color="#e94560", y=1.02,
    )
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"[SAVED] {save_path}")

    plt.close(fig)


# ==============================================================================
# 7. Embeddings - Visualización de similitud (Bonus extra)
# ==============================================================================

def visualize_similarity_matrix(
    image_paths: list[str],
    image_names: list[str],
    labels: list[str],
    model,
    preprocess,
    device: str,
    save_path: str | None = None,
):
    """
    Genera un heatmap de similitud coseno entre imágenes y etiquetas de texto,
    mostrando cómo CLIP relaciona representaciones visuales y textuales.

    Args:
        image_paths: Lista de rutas a imágenes.
        image_names: Nombres de las imágenes.
        labels: Lista de etiquetas de texto.
        model: Modelo CLIP.
        preprocess: Función de preprocesamiento.
        device: Dispositivo.
        save_path: Ruta para guardar.
    """
    # Codificar todas las imágenes
    image_tensors = torch.cat([
        preprocess(Image.open(p)).unsqueeze(0) for p in image_paths
    ]).to(device)

    text_tokens = clip.tokenize(labels).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image_tensors)
        text_features = model.encode_text(text_tokens)

        # Normalizar
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        # Similitud coseno
        similarity = (image_features @ text_features.T).cpu().numpy()

    # Visualizar heatmap
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(similarity, cmap="magma", aspect="auto", vmin=0, vmax=0.4)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=10)
    ax.set_yticks(range(len(image_names)))
    ax.set_yticklabels(image_names, fontsize=10)

    # Anotar valores en cada celda
    for i in range(len(image_names)):
        for j in range(len(labels)):
            text_val = f"{similarity[i, j]:.2f}"
            text_color = "white" if similarity[i, j] < 0.25 else "black"
            ax.text(j, i, text_val, ha="center", va="center", fontsize=9, color=text_color)

    plt.colorbar(im, ax=ax, label="Similitud coseno", shrink=0.8)
    ax.set_title(
        "Matriz de Similitud Coseno (Imagen ↔ Texto)",
        fontsize=14, fontweight="bold", color="#e94560", pad=15,
    )
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"[SAVED] {save_path}")

    plt.close(fig)


# ==============================================================================
# MAIN - Ejecución de todas las actividades
# ==============================================================================

def main():
    print("=" * 70)
    print("  CLIP - Clasificación de Imágenes Visual y Verbal")
    print("=" * 70)

    # -----------------------------------------------------------------------
    # Paso 1: Cargar modelo
    # -----------------------------------------------------------------------
    model, preprocess, device = load_clip_model("ViT-B/32")

    # -----------------------------------------------------------------------
    # Paso 2: Definir imágenes y etiquetas
    # -----------------------------------------------------------------------
    image_files = {
        "cat": os.path.join(IMAGES_DIR, "cat.png"),
        "sports_car": os.path.join(IMAGES_DIR, "sports_car.png"),
        "horse": os.path.join(IMAGES_DIR, "horse.png"),
        "tree": os.path.join(IMAGES_DIR, "tree.png"),
        "dog": os.path.join(IMAGES_DIR, "dog.png"),
    }

    # Verificar que las imágenes existen
    for name, path in image_files.items():
        if not os.path.exists(path):
            print(f"[ERROR] Imagen no encontrada: {path}")
            return
    print(f"[INFO] {len(image_files)} imágenes de prueba encontradas.")

    # Etiquetas básicas para clasificación
    basic_labels = ["a cat", "a dog", "a horse", "a car", "a tree"]

    # -----------------------------------------------------------------------
    # Paso 3: Clasificación individual de cada imagen
    # -----------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("  ACTIVIDAD 1: Clasificación individual")
    print("-" * 70)

    for name, img_path in image_files.items():
        probs, labels = classify_single_image(img_path, basic_labels, model, preprocess, device)

        # Mostrar resultados en consola
        print(f"\n  Imagen: {name}")
        best_idx = np.argmax(probs)
        for i, (label, prob) in enumerate(zip(labels, probs)):
            marker = " ★" if i == best_idx else ""
            print(f"    {label:25s} → {prob:.4f} ({prob:.1%}){marker}")

        # Guardar visualización
        save_name = os.path.join(MEDIA_DIR, f"clasificacion_{name}.png")
        visualize_classification(
            img_path, labels, probs,
            title=f"Clasificación CLIP — {name}",
            save_path=save_name,
        )

    # -----------------------------------------------------------------------
    # Paso 4: Clasificación por lote (Bonus)
    # -----------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("  ACTIVIDAD 2: Clasificación por lote")
    print("-" * 70)

    batch_paths = list(image_files.values())
    batch_probs = classify_batch(
        batch_paths, basic_labels, model, preprocess, device,
        title="Clasificación por Lote — CLIP ViT-B/32",
        save_path=os.path.join(MEDIA_DIR, "clasificacion_lote.png"),
    )
    print("  [OK] Clasificación por lote completada.")

    # -----------------------------------------------------------------------
    # Paso 5: Comparación de estilos de prompt
    # -----------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("  ACTIVIDAD 3: Comparación de estilos de prompt")
    print("-" * 70)

    # Comparar prompts simples vs detallados en la imagen del gato
    cat_prompt_sets = {
        "Etiquetas simples": ["cat", "dog", "horse", "car", "tree"],
        "Descripciones detalladas": [
            "a tabby cat sitting on furniture",
            "a golden retriever playing",
            "a horse galloping in a meadow",
            "a red sports car driving fast",
            "a large oak tree in a park",
        ],
    }
    compare_prompt_styles(
        image_files["cat"], cat_prompt_sets, model, preprocess, device,
        image_name="Gato",
        save_path=os.path.join(MEDIA_DIR, "comparacion_prompts_cat.png"),
    )

    # Comparar prompts en la imagen del carro deportivo
    car_prompt_sets = {
        "Etiquetas simples": ["cat", "dog", "horse", "car", "tree"],
        "Descripciones detalladas": [
            "a cute fluffy cat",
            "a happy dog running",
            "a brown horse in nature",
            "a fast red sports car on a highway",
            "a green tree with leaves",
        ],
    }
    compare_prompt_styles(
        image_files["sports_car"], car_prompt_sets, model, preprocess, device,
        image_name="Carro deportivo",
        save_path=os.path.join(MEDIA_DIR, "comparacion_prompts_car.png"),
    )
    print("  [OK] Comparación de prompts completada.")

    # -----------------------------------------------------------------------
    # Paso 6: Prompts ambiguos y subjetivos
    # -----------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("  ACTIVIDAD 4: Prompts ambiguos y subjetivos")
    print("-" * 70)

    ambiguous_labels = [
        "something happy",
        "something dangerous",
        "something peaceful",
        "something fast",
        "something alive",
    ]

    experiment_ambiguous_prompts(
        list(image_files.values()),
        list(image_files.keys()),
        ambiguous_labels,
        model, preprocess, device,
        save_path=os.path.join(MEDIA_DIR, "prompts_ambiguos.png"),
    )
    print("  [OK] Experimento con prompts ambiguos completado.")

    # -----------------------------------------------------------------------
    # Paso 7: Matriz de similitud (Bonus extra)
    # -----------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("  ACTIVIDAD 5: Matriz de similitud coseno")
    print("-" * 70)

    visualize_similarity_matrix(
        list(image_files.values()),
        list(image_files.keys()),
        basic_labels,
        model, preprocess, device,
        save_path=os.path.join(MEDIA_DIR, "matriz_similitud.png"),
    )
    print("  [OK] Matriz de similitud generada.")

    # -----------------------------------------------------------------------
    # Resumen
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("  RESULTADOS GUARDADOS EN:")
    print(f"  {os.path.abspath(MEDIA_DIR)}")
    print("=" * 70)

    media_files = os.listdir(MEDIA_DIR)
    for f in sorted(media_files):
        fpath = os.path.join(MEDIA_DIR, f)
        size_kb = os.path.getsize(fpath) / 1024
        print(f"  • {f} ({size_kb:.0f} KB)")

    print(f"\n  Total: {len(media_files)} archivos generados.")
    print("  ¡Taller completado exitosamente! 🎉")


if __name__ == "__main__":
    main()
