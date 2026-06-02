"""
Taller: Entrenamiento de un Modelo de Deep Learning de Inicio a Fin
====================================================================

Este script implementa el flujo completo de entrenamiento de un modelo de
Deep Learning usando PyTorch:

    1. Carga y visualización del dataset MNIST
    2. Preparación de DataLoaders (train/val/test)
    3. Definición de un MLP (Multi-Layer Perceptron)
    4. Entrenamiento con validación por época
    5. Validación cruzada K-Fold
    6. Evaluación con métricas y matriz de confusión
    7. Fine-tuning con ResNet18 preentrenado (frozen vs unfrozen)
    8. Guardado y carga del modelo

Autores:
    - Brayan Alejandro Muñoz Pérez (bmunozp@unal.edu.co)
    - Álvaro Andrés Romero Castro (alromeroca@unal.edu.co)
    - Juan Camilo Lopez Bustos (juclopezbu@unal.edu.co)
    - Alejandro Ortiz Cortes (alortizco@unal.edu.co)

Fecha: 01 de junio de 2026
"""

import os
import time
import copy
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split, Subset
from torchvision import datasets, transforms, models
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import KFold

# ==============================================================================
# Configuración global
# ==============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, "..", "media")
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Dispositivo
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Reproducibilidad
torch.manual_seed(42)
np.random.seed(42)

# Estilo visual premium (tema oscuro)
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
    "axes.grid": True,
    "grid.color": "#2a2a4a",
    "grid.alpha": 0.5,
})

# Colores del tema
C_PRIMARY = "#e94560"
C_SECONDARY = "#0f3460"
C_ACCENT = "#06d6a0"
C_WARN = "#ffd166"
C_INFO = "#00b4d8"


# ==============================================================================
# 1. Cargar y visualizar el dataset
# ==============================================================================

def load_datasets():
    """Carga el dataset MNIST con normalización estándar."""
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,)),
    ])

    train_data = datasets.MNIST(
        root=DATA_DIR, train=True, download=True, transform=transform
    )
    test_data = datasets.MNIST(
        root=DATA_DIR, train=False, download=True, transform=transform
    )

    print(f"[INFO] Dataset MNIST cargado")
    print(f"  Entrenamiento: {len(train_data)} muestras")
    print(f"  Prueba:        {len(test_data)} muestras")
    print(f"  Forma imagen:  {train_data[0][0].shape}")
    print(f"  Clases:        {train_data.classes}")

    return train_data, test_data


def visualize_dataset(train_data, save_path=None):
    """Visualiza una cuadrícula de ejemplos del dataset."""
    fig, axes = plt.subplots(3, 8, figsize=(16, 6))

    for i, ax in enumerate(axes.flat):
        image, label = train_data[i]
        ax.imshow(image.squeeze(), cmap="gray")
        ax.set_title(f"{label}", fontsize=10, color=C_ACCENT, fontweight="bold")
        ax.axis("off")

    fig.suptitle(
        "Muestras del Dataset MNIST",
        fontsize=16, fontweight="bold", color=C_PRIMARY, y=1.02,
    )
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"[SAVED] {save_path}")
    plt.close(fig)


# ==============================================================================
# 2. Preparar DataLoaders
# ==============================================================================

def prepare_dataloaders(train_data, test_data, batch_size=64):
    """Divide el set de entrenamiento en train/val y crea DataLoaders."""
    train_size = int(0.8 * len(train_data))
    val_size = len(train_data) - train_size

    train_subset, val_subset = random_split(
        train_data, [train_size, val_size],
        generator=torch.Generator().manual_seed(42),
    )

    train_loader = DataLoader(train_subset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_subset, batch_size=batch_size)
    test_loader = DataLoader(test_data, batch_size=batch_size)

    print(f"\n[INFO] DataLoaders preparados (batch_size={batch_size})")
    print(f"  Train: {len(train_subset)} muestras ({len(train_loader)} batches)")
    print(f"  Val:   {len(val_subset)} muestras ({len(val_loader)} batches)")
    print(f"  Test:  {len(test_data)} muestras ({len(test_loader)} batches)")

    return train_loader, val_loader, test_loader


# ==============================================================================
# 3. Definir el modelo MLP
# ==============================================================================

class MLP(nn.Module):
    """
    Multi-Layer Perceptron para clasificación de MNIST.

    Arquitectura:
        Flatten → Linear(784, 128) → ReLU → Dropout(0.2) →
        Linear(128, 64) → ReLU → Linear(64, 10)
    """

    def __init__(self, input_size=28 * 28, hidden1=128, hidden2=64, num_classes=10):
        super(MLP, self).__init__()
        self.network = nn.Sequential(
            nn.Flatten(),
            nn.Linear(input_size, hidden1),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden1, hidden2),
            nn.ReLU(),
            nn.Linear(hidden2, num_classes),
        )

    def forward(self, x):
        return self.network(x)


def create_mlp():
    """Crea e imprime la arquitectura del MLP."""
    model = MLP()
    print(f"\n[INFO] Modelo MLP creado:")
    print(model)

    total_params = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Parámetros totales:     {total_params:,}")
    print(f"  Parámetros entrenables: {trainable:,}")

    return model


# ==============================================================================
# 4 & 5. Entrenamiento con validación
# ==============================================================================

def train_model(
    model, train_loader, val_loader, epochs=10, lr=0.001, verbose=True
):
    """
    Entrena el modelo con validación por época.

    Returns:
        history: dict con train_losses, val_losses, val_accuracies
    """
    model = model.to(DEVICE)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    history = {"train_loss": [], "val_loss": [], "val_accuracy": []}

    for epoch in range(epochs):
        # --- Entrenamiento ---
        model.train()
        running_loss = 0.0

        for images, labels in train_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)

            optimizer.zero_grad()
            output = model(images)
            loss = criterion(output, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        avg_train_loss = running_loss / len(train_loader)
        history["train_loss"].append(avg_train_loss)

        # --- Validación ---
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(DEVICE), labels.to(DEVICE)
                output = model(images)
                val_loss += criterion(output, labels).item()
                _, predicted = torch.max(output, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        avg_val_loss = val_loss / len(val_loader)
        val_accuracy = correct / total

        history["val_loss"].append(avg_val_loss)
        history["val_accuracy"].append(val_accuracy)

        if verbose:
            print(
                f"  Epoch {epoch + 1:2d}/{epochs} │ "
                f"Train Loss: {avg_train_loss:.4f} │ "
                f"Val Loss: {avg_val_loss:.4f} │ "
                f"Val Acc: {val_accuracy:.4f}"
            )

    return history


def plot_training_curves(history, title="Curvas de Entrenamiento", save_path=None):
    """Visualiza las curvas de pérdida y accuracy durante el entrenamiento."""
    epochs_range = range(1, len(history["train_loss"]) + 1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # --- Curvas de pérdida ---
    ax1.plot(epochs_range, history["train_loss"], "-o", color=C_PRIMARY,
             linewidth=2, markersize=5, label="Train Loss")
    ax1.plot(epochs_range, history["val_loss"], "-s", color=C_INFO,
             linewidth=2, markersize=5, label="Val Loss")
    ax1.set_xlabel("Época", fontsize=12)
    ax1.set_ylabel("Pérdida (Loss)", fontsize=12)
    ax1.set_title("Pérdida por Época", fontsize=13, fontweight="bold")
    ax1.legend(fontsize=10)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # --- Curva de accuracy ---
    ax2.plot(epochs_range, history["val_accuracy"], "-^", color=C_ACCENT,
             linewidth=2, markersize=6, label="Val Accuracy")
    ax2.set_xlabel("Época", fontsize=12)
    ax2.set_ylabel("Accuracy", fontsize=12)
    ax2.set_title("Accuracy de Validación por Época", fontsize=13, fontweight="bold")
    ax2.set_ylim(0.9, 1.0)
    ax2.legend(fontsize=10)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    # Anotar el mejor accuracy
    best_epoch = np.argmax(history["val_accuracy"])
    best_acc = history["val_accuracy"][best_epoch]
    ax2.annotate(
        f"Mejor: {best_acc:.4f}",
        xy=(best_epoch + 1, best_acc),
        xytext=(best_epoch + 1 + 1, best_acc - 0.01),
        fontsize=10, color=C_WARN, fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=C_WARN, lw=1.5),
    )

    fig.suptitle(title, fontsize=15, fontweight="bold", color=C_PRIMARY, y=1.02)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"[SAVED] {save_path}")
    plt.close(fig)


# ==============================================================================
# 6. K-Fold Cross Validation
# ==============================================================================

def kfold_cross_validation(train_data, n_splits=3, epochs=5, batch_size=64):
    """
    Realiza validación cruzada K-Fold en el set de entrenamiento.

    Args:
        train_data: Dataset completo de entrenamiento.
        n_splits: Número de folds.
        epochs: Épocas por fold.
        batch_size: Tamaño de batch.

    Returns:
        fold_results: Lista de dicts con métricas por fold.
    """
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    indices = list(range(len(train_data)))

    fold_results = []

    for fold, (train_idx, val_idx) in enumerate(kf.split(indices)):
        print(f"\n  ── Fold {fold + 1}/{n_splits} ──")

        train_subset = Subset(train_data, train_idx)
        val_subset = Subset(train_data, val_idx)

        train_loader = DataLoader(train_subset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_subset, batch_size=batch_size)

        # Modelo fresco para cada fold
        model = MLP().to(DEVICE)
        history = train_model(model, train_loader, val_loader, epochs=epochs, verbose=False)

        final_acc = history["val_accuracy"][-1]
        final_loss = history["val_loss"][-1]
        print(f"    Val Accuracy: {final_acc:.4f} | Val Loss: {final_loss:.4f}")

        fold_results.append({
            "fold": fold + 1,
            "accuracy": final_acc,
            "loss": final_loss,
            "history": history,
        })

    # Resumen
    accs = [r["accuracy"] for r in fold_results]
    print(f"\n  K-Fold Resumen:")
    print(f"    Accuracy promedio: {np.mean(accs):.4f} ± {np.std(accs):.4f}")

    return fold_results


def plot_kfold_results(fold_results, save_path=None):
    """Visualiza los resultados de K-Fold Cross Validation."""
    n_folds = len(fold_results)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # --- Barras de accuracy por fold ---
    folds = [f"Fold {r['fold']}" for r in fold_results]
    accs = [r["accuracy"] for r in fold_results]
    colors = [C_INFO, C_ACCENT, C_PRIMARY, C_WARN, "#8338ec"][:n_folds]

    bars = ax1.bar(folds, accs, color=colors, edgecolor="#eaeaea", linewidth=0.5, width=0.5)

    # Línea de promedio
    mean_acc = np.mean(accs)
    ax1.axhline(y=mean_acc, color=C_WARN, linestyle="--", linewidth=2, label=f"Promedio: {mean_acc:.4f}")

    ax1.set_ylim(0.95, 1.0)
    ax1.set_ylabel("Accuracy", fontsize=12)
    ax1.set_title("Accuracy por Fold", fontsize=13, fontweight="bold")
    ax1.legend(fontsize=10)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # Anotar valores en las barras
    for bar, acc in zip(bars, accs):
        ax1.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.001,
            f"{acc:.4f}", ha="center", fontsize=10, fontweight="bold", color="#eaeaea",
        )

    # --- Curvas de training por fold ---
    for r in fold_results:
        epochs_range = range(1, len(r["history"]["val_accuracy"]) + 1)
        ax2.plot(
            epochs_range, r["history"]["val_accuracy"],
            "-o", linewidth=1.5, markersize=4,
            label=f"Fold {r['fold']}",
        )

    ax2.set_xlabel("Época", fontsize=12)
    ax2.set_ylabel("Val Accuracy", fontsize=12)
    ax2.set_title("Convergencia por Fold", fontsize=13, fontweight="bold")
    ax2.legend(fontsize=10)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig.suptitle(
        f"K-Fold Cross Validation ({n_folds} Folds)",
        fontsize=15, fontweight="bold", color=C_PRIMARY, y=1.02,
    )
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"[SAVED] {save_path}")
    plt.close(fig)


# ==============================================================================
# 7. Evaluación: Métricas y Matriz de Confusión
# ==============================================================================

def evaluate_model(model, test_loader):
    """Evalúa el modelo en el set de prueba y retorna predicciones."""
    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(DEVICE)
            output = model(images)
            _, preds = torch.max(output, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())

    return np.array(all_preds), np.array(all_labels)


def plot_confusion_matrix(all_preds, all_labels, class_names=None, save_path=None):
    """Genera y visualiza la matriz de confusión."""
    cm = confusion_matrix(all_labels, all_preds)

    if class_names is None:
        class_names = [str(i) for i in range(10)]

    fig, ax = plt.subplots(figsize=(10, 8))

    # Heatmap con seaborn
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="magma",
        xticklabels=class_names, yticklabels=class_names,
        ax=ax, linewidths=0.5, linecolor="#2a2a4a",
        cbar_kws={"label": "Cantidad de predicciones"},
    )

    ax.set_xlabel("Predicción", fontsize=12, labelpad=10)
    ax.set_ylabel("Real", fontsize=12, labelpad=10)
    ax.set_title(
        "Matriz de Confusión — MLP en MNIST",
        fontsize=14, fontweight="bold", color=C_PRIMARY, pad=15,
    )

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"[SAVED] {save_path}")
    plt.close(fig)


def plot_predictions(model, test_data, save_path=None):
    """Visualiza predicciones individuales del modelo en una cuadrícula."""
    model.eval()

    fig, axes = plt.subplots(3, 6, figsize=(16, 7))

    for i, ax in enumerate(axes.flat):
        image, true_label = test_data[i + 100]  # Offset para variedad
        with torch.no_grad():
            output = model(image.unsqueeze(0).to(DEVICE))
            _, pred = torch.max(output, 1)
            pred_label = pred.item()

        ax.imshow(image.squeeze(), cmap="gray")
        ax.axis("off")

        is_correct = pred_label == true_label
        color = C_ACCENT if is_correct else C_PRIMARY
        symbol = "✓" if is_correct else "✗"
        ax.set_title(
            f"{symbol} Pred: {pred_label} | Real: {true_label}",
            fontsize=9, color=color, fontweight="bold",
        )

    fig.suptitle(
        "Predicciones del Modelo MLP",
        fontsize=15, fontweight="bold", color=C_PRIMARY, y=1.02,
    )
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"[SAVED] {save_path}")
    plt.close(fig)


# ==============================================================================
# 8. Fine-Tuning con ResNet18
# ==============================================================================

def prepare_resnet_data(train_data, test_data, subset_size=5000, batch_size=32):
    """
    Prepara los datos para ResNet18 (RGB, 224x224).
    Usa un subconjunto para mantener el tiempo de entrenamiento razonable en CPU.
    """
    resnet_transform = transforms.Compose([
        transforms.Resize(224),
        transforms.Grayscale(num_output_channels=3),  # 1ch → 3ch
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Recrear datasets con transform de ResNet
    resnet_train = datasets.MNIST(root=DATA_DIR, train=True, download=False, transform=resnet_transform)
    resnet_test = datasets.MNIST(root=DATA_DIR, train=False, download=False, transform=resnet_transform)

    # Usar subconjunto para velocidad
    train_indices = torch.randperm(len(resnet_train))[:subset_size]
    test_indices = torch.randperm(len(resnet_test))[:1000]

    train_subset = Subset(resnet_train, train_indices.tolist())
    test_subset = Subset(resnet_test, test_indices.tolist())

    # Split train/val
    train_size = int(0.8 * len(train_subset))
    val_size = len(train_subset) - train_size
    train_split, val_split = random_split(
        train_subset, [train_size, val_size],
        generator=torch.Generator().manual_seed(42),
    )

    train_loader = DataLoader(train_split, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_split, batch_size=batch_size)
    test_loader = DataLoader(test_subset, batch_size=batch_size)

    print(f"  ResNet data: train={len(train_split)}, val={len(val_split)}, test={len(test_subset)}")

    return train_loader, val_loader, test_loader


def create_resnet_model(num_classes=10, freeze_backbone=True):
    """
    Crea un modelo ResNet18 preentrenado con la capa final reemplazada.

    Args:
        num_classes: Número de clases de salida.
        freeze_backbone: Si True, congela todas las capas excepto la última.
    """
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

    if freeze_backbone:
        for param in model.parameters():
            param.requires_grad = False

    # Reemplazar capa final
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)

    return model.to(DEVICE)


def train_resnet(model, train_loader, val_loader, epochs=5, lr=1e-3):
    """Entrena el modelo ResNet con la configuración dada."""
    criterion = nn.CrossEntropyLoss()

    # Solo optimizar parámetros que requieren gradiente
    params_to_optimize = [p for p in model.parameters() if p.requires_grad]
    optimizer = optim.Adam(params_to_optimize, lr=lr)

    history = {"train_loss": [], "val_loss": [], "val_accuracy": []}

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0

        for images, labels in train_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            output = model(images)
            loss = criterion(output, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        avg_train_loss = running_loss / len(train_loader)
        history["train_loss"].append(avg_train_loss)

        # Validación
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(DEVICE), labels.to(DEVICE)
                output = model(images)
                val_loss += criterion(output, labels).item()
                _, predicted = torch.max(output, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        avg_val_loss = val_loss / len(val_loader)
        val_accuracy = correct / total

        history["val_loss"].append(avg_val_loss)
        history["val_accuracy"].append(val_accuracy)

        print(
            f"    Epoch {epoch + 1:2d}/{epochs} │ "
            f"Train Loss: {avg_train_loss:.4f} │ "
            f"Val Loss: {avg_val_loss:.4f} │ "
            f"Val Acc: {val_accuracy:.4f}"
        )

    return history


def run_finetuning_comparison(train_data, test_data):
    """
    Ejecuta la comparación entre fine-tuning con backbone congelado
    vs backbone descongelado.

    Returns:
        frozen_history, unfrozen_history, frozen_acc, unfrozen_acc
    """
    print("\n  Preparando datos para ResNet18...")
    train_loader, val_loader, test_loader = prepare_resnet_data(train_data, test_data)

    # --- Fase 1: Backbone congelado (solo capa final) ---
    print("\n  ── ResNet18 — Backbone CONGELADO ──")
    frozen_model = create_resnet_model(freeze_backbone=True)
    trainable_frozen = sum(p.numel() for p in frozen_model.parameters() if p.requires_grad)
    total_frozen = sum(p.numel() for p in frozen_model.parameters())
    print(f"    Params entrenables: {trainable_frozen:,} / {total_frozen:,}")

    frozen_history = train_resnet(frozen_model, train_loader, val_loader, epochs=5, lr=1e-3)

    # Evaluar en test
    frozen_preds, frozen_labels = evaluate_resnet(frozen_model, test_loader)
    frozen_acc = np.mean(frozen_preds == frozen_labels)
    print(f"    Test Accuracy (frozen): {frozen_acc:.4f}")

    # --- Fase 2: Backbone descongelado (fine-tuning completo) ---
    print("\n  ── ResNet18 — Backbone DESCONGELADO (Fine-tuning completo) ──")
    unfrozen_model = create_resnet_model(freeze_backbone=False)
    trainable_unfrozen = sum(p.numel() for p in unfrozen_model.parameters() if p.requires_grad)
    print(f"    Params entrenables: {trainable_unfrozen:,} / {total_frozen:,}")

    unfrozen_history = train_resnet(unfrozen_model, train_loader, val_loader, epochs=5, lr=1e-4)

    # Evaluar en test
    unfrozen_preds, unfrozen_labels = evaluate_resnet(unfrozen_model, test_loader)
    unfrozen_acc = np.mean(unfrozen_preds == unfrozen_labels)
    print(f"    Test Accuracy (unfrozen): {unfrozen_acc:.4f}")

    return frozen_history, unfrozen_history, frozen_acc, unfrozen_acc


def evaluate_resnet(model, test_loader):
    """Evalúa modelo ResNet en el test loader."""
    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(DEVICE)
            output = model(images)
            _, preds = torch.max(output, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())

    return np.array(all_preds), np.array(all_labels)


def plot_finetuning_comparison(
    frozen_history, unfrozen_history, frozen_acc, unfrozen_acc, save_path=None
):
    """Visualiza la comparación entre fine-tuning congelado y descongelado."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    epochs_range = range(1, len(frozen_history["val_accuracy"]) + 1)

    # --- Panel 1: Curvas de pérdida ---
    axes[0].plot(epochs_range, frozen_history["train_loss"], "-o",
                 color=C_INFO, linewidth=2, markersize=5, label="Frozen Train")
    axes[0].plot(epochs_range, unfrozen_history["train_loss"], "-s",
                 color=C_ACCENT, linewidth=2, markersize=5, label="Unfrozen Train")
    axes[0].plot(epochs_range, frozen_history["val_loss"], "--o",
                 color=C_INFO, linewidth=1.5, markersize=4, alpha=0.6, label="Frozen Val")
    axes[0].plot(epochs_range, unfrozen_history["val_loss"], "--s",
                 color=C_ACCENT, linewidth=1.5, markersize=4, alpha=0.6, label="Unfrozen Val")

    axes[0].set_xlabel("Época", fontsize=12)
    axes[0].set_ylabel("Pérdida", fontsize=12)
    axes[0].set_title("Curvas de Pérdida", fontsize=13, fontweight="bold")
    axes[0].legend(fontsize=9)
    axes[0].spines["top"].set_visible(False)
    axes[0].spines["right"].set_visible(False)

    # --- Panel 2: Curvas de accuracy ---
    axes[1].plot(epochs_range, frozen_history["val_accuracy"], "-o",
                 color=C_INFO, linewidth=2, markersize=6, label="Frozen")
    axes[1].plot(epochs_range, unfrozen_history["val_accuracy"], "-s",
                 color=C_ACCENT, linewidth=2, markersize=6, label="Unfrozen")

    axes[1].set_xlabel("Época", fontsize=12)
    axes[1].set_ylabel("Val Accuracy", fontsize=12)
    axes[1].set_title("Accuracy de Validación", fontsize=13, fontweight="bold")
    axes[1].legend(fontsize=10)
    axes[1].spines["top"].set_visible(False)
    axes[1].spines["right"].set_visible(False)

    # --- Panel 3: Comparación final (barras) ---
    labels_bar = ["Backbone\nCongelado", "Fine-tuning\nCompleto"]
    accs = [frozen_acc, unfrozen_acc]
    bar_colors = [C_INFO, C_ACCENT]

    bars = axes[2].bar(labels_bar, accs, color=bar_colors, edgecolor="#eaeaea",
                       linewidth=0.5, width=0.5)

    axes[2].set_ylim(0.85, 1.0)
    axes[2].set_ylabel("Test Accuracy", fontsize=12)
    axes[2].set_title("Comparación Final en Test", fontsize=13, fontweight="bold")
    axes[2].spines["top"].set_visible(False)
    axes[2].spines["right"].set_visible(False)

    for bar, acc in zip(bars, accs):
        axes[2].text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
            f"{acc:.4f}", ha="center", fontsize=12, fontweight="bold", color=C_WARN,
        )

    fig.suptitle(
        "Fine-Tuning ResNet18 — Congelado vs Descongelado",
        fontsize=15, fontweight="bold", color=C_PRIMARY, y=1.02,
    )
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"[SAVED] {save_path}")
    plt.close(fig)


# ==============================================================================
# 9. Guardar y cargar el modelo
# ==============================================================================

def save_model(model, path):
    """Guarda los pesos del modelo."""
    torch.save(model.state_dict(), path)
    size_mb = os.path.getsize(path) / (1024 * 1024)
    print(f"[SAVED] Modelo guardado: {path} ({size_mb:.2f} MB)")


def load_model(model_class, path, **kwargs):
    """Carga los pesos del modelo."""
    model = model_class(**kwargs)
    model.load_state_dict(torch.load(path, weights_only=True))
    model.eval()
    print(f"[LOADED] Modelo cargado: {path}")
    return model


# ==============================================================================
# MAIN — Ejecución completa
# ==============================================================================

def main():
    start_time = time.time()

    print("=" * 70)
    print("  Entrenamiento de un Modelo de Deep Learning de Inicio a Fin")
    print("=" * 70)
    print(f"  Dispositivo: {DEVICE}")

    # ──────────────────────────────────────────────────────────────────────
    # Paso 1: Cargar y visualizar el dataset
    # ──────────────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("  PASO 1: Cargar y visualizar el dataset MNIST")
    print("─" * 70)

    train_data, test_data = load_datasets()
    visualize_dataset(train_data, save_path=os.path.join(MEDIA_DIR, "dataset_samples.png"))

    # ──────────────────────────────────────────────────────────────────────
    # Paso 2: Preparar DataLoaders
    # ──────────────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("  PASO 2: Preparar DataLoaders")
    print("─" * 70)

    train_loader, val_loader, test_loader = prepare_dataloaders(train_data, test_data)

    # ──────────────────────────────────────────────────────────────────────
    # Paso 3: Definir el modelo MLP
    # ──────────────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("  PASO 3: Definir el modelo MLP")
    print("─" * 70)

    model = create_mlp()

    # ──────────────────────────────────────────────────────────────────────
    # Paso 4-5: Entrenamiento con validación
    # ──────────────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("  PASOS 4-5: Entrenamiento del MLP (10 épocas)")
    print("─" * 70)

    history = train_model(model, train_loader, val_loader, epochs=10)
    plot_training_curves(
        history,
        title="Curvas de Entrenamiento — MLP en MNIST",
        save_path=os.path.join(MEDIA_DIR, "training_curves.png"),
    )

    # ──────────────────────────────────────────────────────────────────────
    # Paso 6a: K-Fold Cross Validation
    # ──────────────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("  PASO 6a: K-Fold Cross Validation (3 folds, 5 épocas cada uno)")
    print("─" * 70)

    fold_results = kfold_cross_validation(train_data, n_splits=3, epochs=5)
    plot_kfold_results(fold_results, save_path=os.path.join(MEDIA_DIR, "kfold_results.png"))

    # ──────────────────────────────────────────────────────────────────────
    # Paso 6b: Evaluación con métricas y matriz de confusión
    # ──────────────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("  PASO 6b: Evaluación en Test Set")
    print("─" * 70)

    all_preds, all_labels = evaluate_model(model, test_loader)
    test_accuracy = np.mean(all_preds == all_labels)
    print(f"\n  Test Accuracy del MLP: {test_accuracy:.4f}")
    print(f"\n  Classification Report:")
    print(classification_report(all_labels, all_preds))

    plot_confusion_matrix(
        all_preds, all_labels,
        save_path=os.path.join(MEDIA_DIR, "confusion_matrix.png"),
    )

    plot_predictions(
        model, test_data,
        save_path=os.path.join(MEDIA_DIR, "predictions.png"),
    )

    # ──────────────────────────────────────────────────────────────────────
    # Paso 7: Fine-Tuning con ResNet18
    # ──────────────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("  PASO 7: Fine-Tuning con ResNet18 preentrenado")
    print("─" * 70)

    frozen_hist, unfrozen_hist, frozen_acc, unfrozen_acc = run_finetuning_comparison(
        train_data, test_data
    )

    plot_finetuning_comparison(
        frozen_hist, unfrozen_hist, frozen_acc, unfrozen_acc,
        save_path=os.path.join(MEDIA_DIR, "finetuning_comparison.png"),
    )

    # ──────────────────────────────────────────────────────────────────────
    # Paso 8: Guardar y cargar el modelo
    # ──────────────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("  PASO 8: Guardar y cargar el modelo")
    print("─" * 70)

    model_path = os.path.join(BASE_DIR, "modelo_final.pth")
    save_model(model, model_path)

    # Verificar carga
    loaded_model = load_model(MLP, model_path)
    loaded_preds, loaded_labels = evaluate_model(loaded_model.to(DEVICE), test_loader)
    loaded_acc = np.mean(loaded_preds == loaded_labels)
    print(f"  Accuracy del modelo cargado: {loaded_acc:.4f} (debe coincidir con {test_accuracy:.4f})")

    # ──────────────────────────────────────────────────────────────────────
    # Resumen final
    # ──────────────────────────────────────────────────────────────────────
    elapsed = time.time() - start_time

    print("\n" + "=" * 70)
    print("  RESUMEN FINAL")
    print("=" * 70)
    print(f"  Tiempo total de ejecución: {elapsed:.1f} segundos")
    print(f"\n  Resultados:")
    print(f"    MLP Test Accuracy:              {test_accuracy:.4f}")
    print(f"    K-Fold Accuracy (promedio):      {np.mean([r['accuracy'] for r in fold_results]):.4f}")
    print(f"    ResNet18 Frozen Test Accuracy:   {frozen_acc:.4f}")
    print(f"    ResNet18 Unfrozen Test Accuracy: {unfrozen_acc:.4f}")

    print(f"\n  Archivos generados en {os.path.abspath(MEDIA_DIR)}:")
    for f in sorted(os.listdir(MEDIA_DIR)):
        fpath = os.path.join(MEDIA_DIR, f)
        size_kb = os.path.getsize(fpath) / 1024
        print(f"    • {f} ({size_kb:.0f} KB)")

    print(f"\n  ¡Taller completado exitosamente! 🎉")


if __name__ == "__main__":
    main()
