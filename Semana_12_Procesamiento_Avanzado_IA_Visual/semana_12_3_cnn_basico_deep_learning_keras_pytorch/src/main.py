import torch
import torch.nn as nn
import torch.optim as optim

import torchvision
import torchvision.transforms as transforms

import matplotlib.pyplot as plt

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

# =========================================
# CARGAR DATASET
# =========================================

transform = transforms.ToTensor()

train_dataset = torchvision.datasets.MNIST(
    root="./data",
    train=True,
    download=True,
    transform=transform
)

test_dataset = torchvision.datasets.MNIST(
    root="./data",
    train=False,
    download=True,
    transform=transform
)

train_loader = torch.utils.data.DataLoader(
    train_dataset,
    batch_size=64,
    shuffle=True
)

test_loader = torch.utils.data.DataLoader(
    test_dataset,
    batch_size=64,
    shuffle=False
)

print("Cantidad entrenamiento:", len(train_dataset))
print("Cantidad prueba:", len(test_dataset))


# =========================================
# VISUALIZAR IMÁGENES
# =========================================

images, labels = next(iter(train_loader))

plt.figure(figsize=(10, 5))

for i in range(10):

    plt.subplot(2, 5, i + 1)

    plt.imshow(images[i].squeeze(), cmap="gray")

    plt.title(f"Label: {labels[i].item()}")

    plt.axis("off")

plt.tight_layout()
plt.show()


# =========================================
# DEFINIR MODELO CNN
# =========================================

class CNN(nn.Module):

    def __init__(self):

        super(CNN, self).__init__()

        self.conv_layers = nn.Sequential(

            # Conv 1
            nn.Conv2d(
                in_channels=1,
                out_channels=32,
                kernel_size=3,
                padding=1
            ),

            nn.ReLU(),

            nn.MaxPool2d(
                kernel_size=2,
                stride=2
            ),

            # Conv 2
            nn.Conv2d(
                in_channels=32,
                out_channels=64,
                kernel_size=3,
                padding=1
            ),

            nn.ReLU(),

            nn.MaxPool2d(
                kernel_size=2,
                stride=2
            )
        )

        self.fc_layers = nn.Sequential(

            nn.Flatten(),

            nn.Linear(64 * 7 * 7, 128),

            nn.ReLU(),

            nn.Dropout(0.5),

            nn.Linear(128, 10)
        )

    def forward(self, x):

        x = self.conv_layers(x)

        x = self.fc_layers(x)

        return x


model = CNN()

print(model)


# =========================================
# FUNCIÓN DE PÉRDIDA Y OPTIMIZADOR
# =========================================

criterion = nn.CrossEntropyLoss()

optimizer = optim.Adam(
    model.parameters(),
    lr=0.001
)


# =========================================
# ENTRENAMIENTO
# =========================================

epochs = 5

train_losses = []
train_accuracies = []

for epoch in range(epochs):

    model.train()

    running_loss = 0

    correct = 0

    total = 0

    for images, labels in train_loader:

        # Reiniciar gradientes
        optimizer.zero_grad()

        # Forward
        outputs = model(images)

        # Calcular pérdida
        loss = criterion(outputs, labels)

        # Backpropagation
        loss.backward()

        # Actualizar pesos
        optimizer.step()

        running_loss += loss.item()

        # Accuracy
        _, predicted = torch.max(outputs.data, 1)

        total += labels.size(0)

        correct += (predicted == labels).sum().item()

    epoch_loss = running_loss / len(train_loader)

    epoch_accuracy = 100 * correct / total

    train_losses.append(epoch_loss)

    train_accuracies.append(epoch_accuracy)

    print(f"\nEpoch [{epoch + 1}/{epochs}]")

    print(f"Loss: {epoch_loss:.4f}")

    print(f"Accuracy: {epoch_accuracy:.2f}%")


# =========================================
# GRÁFICAS DE ENTRENAMIENTO
# =========================================

plt.figure(figsize=(12, 5))

# Loss
plt.subplot(1, 2, 1)

plt.plot(train_losses)

plt.title("Loss por Epoch")

plt.xlabel("Epoch")

plt.ylabel("Loss")

# Accuracy
plt.subplot(1, 2, 2)

plt.plot(train_accuracies)

plt.title("Accuracy por Epoch")

plt.xlabel("Epoch")

plt.ylabel("Accuracy")

plt.tight_layout()

plt.show()


# =========================================
# EVALUAR MODELO
# =========================================

model.eval()

correct = 0

total = 0

all_labels = []

all_predictions = []

with torch.no_grad():

    for images, labels in test_loader:

        outputs = model(images)

        _, predicted = torch.max(outputs, 1)

        total += labels.size(0)

        correct += (predicted == labels).sum().item()

        all_labels.extend(labels.numpy())

        all_predictions.extend(predicted.numpy())

accuracy = 100 * correct / total

print(f"\nAccuracy final en test: {accuracy:.2f}%")


# =========================================
# MATRIZ DE CONFUSIÓN
# =========================================

cm = confusion_matrix(
    all_labels,
    all_predictions
)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm
)

disp.plot(cmap="Blues")

plt.title("Matriz de Confusión")

plt.show()


# =========================================
# VISUALIZAR PREDICCIONES
# =========================================

images, labels = next(iter(test_loader))

outputs = model(images)

_, predicted = torch.max(outputs, 1)

plt.figure(figsize=(12, 6))

for i in range(10):

    plt.subplot(2, 5, i + 1)

    plt.imshow(images[i].squeeze(), cmap="gray")

    color = "green"

    if predicted[i] != labels[i]:
        color = "red"

    plt.title(
        f"P:{predicted[i].item()} / R:{labels[i].item()}",
        color=color
    )

    plt.axis("off")

plt.tight_layout()

plt.show()


# =========================================
# GUARDAR MODELO
# =========================================

torch.save(
    model.state_dict(),
    "cnn_mnist.pt"
)

print("\nModelo guardado correctamente")


# =========================================
# CARGAR MODELO
# =========================================

loaded_model = CNN()

loaded_model.load_state_dict(
    torch.load("cnn_mnist.pt")
)

loaded_model.eval()

print("Modelo cargado correctamente")