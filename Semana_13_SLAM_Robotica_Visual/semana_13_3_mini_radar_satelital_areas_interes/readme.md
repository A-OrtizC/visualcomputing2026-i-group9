# Taller Convoluciones Personalizadas

## Nombre del estudiante

* Brayan Alejandro Muñoz Pérez bmunozp@unal.edu.co
* Álvaro Andrés Romero Castro alromeroca@unal.edu.co
* Juan Camilo Lopez Bustos juclopezbu@unal.edu.co
* Alejandro Ortiz Cortes alortizco@unal.edu.co

## Fecha de entrega
1 de junio de 2026

---

# Descripción breve

El objetivo de este taller fue de utilizar clustering en secciones de una imagen satelital para poder despues categorizar regiones basados en su color. 

---

# Implementaciones

## Implementación en Python

## Funcionalidades desarrolladas

### 1. Uso de k-means para agrupar regiones

Se hizo uso de k-means para agrupar cada pixel por color, con esto los centroides son el color "promedio" de esa región.

```python
n_clusters = 3
pixels = roi.reshape((-1, 3))

kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
kmeans.fit(pixels)
segmented_labels = kmeans.labels_.reshape(roi.shape[:2])
centers = kmeans.cluster_centers_

segmented_colored = np.zeros_like(roi)
for i in range(n_clusters):
    segmented_colored[segmented_labels == i] = centers[i]
```

---

### 2. Etiquetado de centroides 

A partir de etiquetas y colores dados por el usuario, el programa etiqueta cada cluster basado a que color se acerca más.

```python
int24_to_rgb = lambda x: np.uint8([x//(256*256), (x//256) % 256, x % 256])
hex_to_rgb = lambda x: int24_to_rgb(int(x.lstrip("#"),16))
center_to_label = {}
for i,v in enumerate(centers):
    closest = pickers[0][1].value
    # cls_c = hex_to_rgb(pickers[0][0].value)
    min_dist = np.linalg.norm(hex_to_rgb(pickers[0][0].value) - v)
    for col, lbl in pickers[1:]:
        rgb = hex_to_rgb(col.value)
        if (dist:=np.linalg.norm(rgb - v)) < min_dist:
            min_dist = dist
            closest = lbl.value
            # cls_c = rgb
    center_to_label[i] = closest
    print(f"El centroide {i+1} se acerca más a la etiquetea \"{closest}\"")
```

---

### 2. Contornos y Etiquetado de Regiones 

A partir de los pixeles agrupados creamos mascaras binarias y obtenemos sus contornos. Despues dibujamos tanto el contorno como la etiqueta asociada al centroide del grupo.

```python
roi_contours = roi.copy()
text = []

for i in range(n_clusters):
    binary_mask = np.uint8(segmented_labels == i) * 255

    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    min_area = 100
    max_area = roi.size / 10
    filtered_contours = [c for c in contours if  max_area > cv2.contourArea(c) > min_area]

    cv2.drawContours(roi_contours, filtered_contours, -1, (0,0,0), 2)
    cv2.drawContours(roi_contours, filtered_contours, -1, centers[i], 1)

    bin_contours = segmented_colored.copy() #cv2.cvtColor(binary_mask, cv2.COLOR_GRAY2RGB)
    cv2.drawContours(bin_contours, filtered_contours, -1, (0, 0, 0), 2)
    plt.axis("off")
    plt.title(f"Contornos para \"{center_to_label[i]}\"")
    plt.imshow(bin_contours, cmap="gray")
    plt.show()

    for _, c in enumerate(filtered_contours):
        M = cv2.moments(c)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            text.append((center_to_label[i], cX, cY))
        else:
            text.append((f"Zona {_+1}", cX, cY))
            

plt.figure(figsize=(8, 8))
plt.imshow(roi_contours)
for t, x, y in text:
    txt = plt.text(x, y, t, ha="center")
    txt.set_path_effects([
        path_effects.withStroke(linewidth=3, foreground="white")
    ])
plt.title(f"Contornos y Etiquetas de cada Clase")
plt.axis('off')
plt.show()
```

---

# Resultados visuales

## Capturas de la implementación

### Sección de la imagen original

![ROI](media/ROI.png)

---

### Agrupamiento de pixeles por k-means

![Agrupamiento](media/clustering.png)

---

### Contornos generados por regiones binarias

![Contorno 1](media/contornos_1.png)
![Contorno 2](media/contornos_2.png)
![Contorno 3](media/contornos_3.png)

---

### Contornos y Etiquetado Final

![Contorno 1](media/contornos_4.png)

---

# Código relevante

## Obtención de la región de interés

```python
image = cv2.imread('image.png')
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

r = cv2.selectROI("Selecciona ROI", cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR), fromCenter=False)
cv2.destroyAllWindows()

roi = image_rgb[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]

plt.title("Imagen escogida")
plt.axis("off")
plt.imshow(roi)
plt.show()
```

---

## Uso de k-means para Agrupar por Color

```python
n_clusters = 3
pixels = roi.reshape((-1, 3))

kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
kmeans.fit(pixels)
segmented_labels = kmeans.labels_.reshape(roi.shape[:2])
centers = kmeans.cluster_centers_

segmented_colored = np.zeros_like(roi)
for i in range(n_clusters):
    segmented_colored[segmented_labels == i] = centers[i]
    
fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].imshow(roi)
ax[0].set_title("ROI Original")
ax[0].axis('off')

ax[1].imshow(segmented_colored)
ax[1].set_title("Segmentación K-means")
ax[1].axis('off')
plt.show()
```

## Método de Entrada por Usuario de Etiquetas y Colores

```python
pickers = []
n_lbl = int(input("Ingrese un número de etiquetas a crear: "))
for i in range(n_lbl):
    text = widgets.Label(value=f"Nombre y color de etiqueta {i+1}:")
    color_picker = widgets.ColorPicker(
        concise=True,
        value='blue',
        disabled=False
    )
    label = widgets.Text()
    display(widgets.HBox([text, label, color_picker]))
    pickers.append((color_picker, label))
```

## Asociación de Centroide a Etiqueta

```python
int24_to_rgb = lambda x: np.uint8([x//(256*256), (x//256) % 256, x % 256])
hex_to_rgb = lambda x: int24_to_rgb(int(x.lstrip("#"),16))
center_to_label = {}
for i,v in enumerate(centers):
    closest = pickers[0][1].value
    # cls_c = hex_to_rgb(pickers[0][0].value)
    min_dist = np.linalg.norm(hex_to_rgb(pickers[0][0].value) - v)
    for col, lbl in pickers[1:]:
        rgb = hex_to_rgb(col.value)
        if (dist:=np.linalg.norm(rgb - v)) < min_dist:
            min_dist = dist
            closest = lbl.value
            # cls_c = rgb
    center_to_label[i] = closest
    print(f"El centroide {i+1} se acerca más a la etiquetea \"{closest}\"")
    # print(closest, v, cls_c, np.linalg.norm(cls_c - v))
# print(center_to_label)
```

## Visualización de Contornos y Etiquetas

```python
roi_contours = roi.copy()
text = []

for i in range(n_clusters):
    binary_mask = np.uint8(segmented_labels == i) * 255

    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    min_area = 100
    max_area = roi.size / 10
    filtered_contours = [c for c in contours if  max_area > cv2.contourArea(c) > min_area]

    cv2.drawContours(roi_contours, filtered_contours, -1, (0,0,0), 2)
    cv2.drawContours(roi_contours, filtered_contours, -1, centers[i], 1)

    bin_contours = segmented_colored.copy() #cv2.cvtColor(binary_mask, cv2.COLOR_GRAY2RGB)
    cv2.drawContours(bin_contours, filtered_contours, -1, (0, 0, 0), 2)
    plt.axis("off")
    plt.title(f"Contornos para \"{center_to_label[i]}\"")
    plt.imshow(bin_contours, cmap="gray")
    plt.show()

    for _, c in enumerate(filtered_contours):
        M = cv2.moments(c)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            text.append((center_to_label[i], cX, cY))
        else:
            text.append((f"Zona {_+1}", cX, cY))
            

plt.figure(figsize=(8, 8))
plt.imshow(roi_contours)
for t, x, y in text:
    txt = plt.text(x, y, t, ha="center")
    txt.set_path_effects([
        path_effects.withStroke(linewidth=3, foreground="white")
    ])
plt.title(f"Contornos y Etiquetas de cada Clase")
plt.axis('off')
plt.show()
```

---

# Prompts utilizados

Para este taller no hubo un uso de prompts, exepto los snippets que presenta google al buscar.

---

# Aprendizajes y dificultades

## Aprendizajes

Se profundizo el entendimiento de clustering y del uso de k-means. Además de poder apreciar un uso más creativo de esta herramienta para uso conjunto con opencv y sus contornos.

## Dificultades

Fue particularmente difícil etiquetar las regiones ya que requirió de etiquetar los clusters, obtener los contornos de cada cluster 1 a 1 y correctamente aplicarlos.