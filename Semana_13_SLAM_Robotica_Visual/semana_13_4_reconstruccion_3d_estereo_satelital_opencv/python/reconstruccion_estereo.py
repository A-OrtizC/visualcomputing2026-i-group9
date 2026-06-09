import cv2
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os

# Definir rutas relativas
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
media_dir = os.path.join(base_dir, 'media')

left_path = os.path.join(media_dir, 'left_image.jpg')
right_path = os.path.join(media_dir, 'right_image.jpg')

# 1. Cargar un par de imágenes satelitales (o aéreas) estereoscópicas:
print("Cargando imágenes estéreo...")
imgL = cv2.imread(left_path, cv2.IMREAD_GRAYSCALE)
imgR = cv2.imread(right_path, cv2.IMREAD_GRAYSCALE)

if imgL is None or imgR is None:
    raise FileNotFoundError("No se encontraron las imágenes estéreo en la carpeta media/")

# 2. Aplicar correspondencia estéreo con OpenCV (StereoSGBM para mejor calidad en terrenos)
print("Calculando disparidad estéreo...")
min_disp = 0
num_disp = 64 # Debe ser divisible por 16
block_size = 15

stereo = cv2.StereoSGBM_create(
    minDisparity=min_disp,
    numDisparities=num_disp,
    blockSize=block_size,
    P1=8 * 1 * block_size**2,
    P2=32 * 1 * block_size**2,
    disp12MaxDiff=1,
    uniquenessRatio=10,
    speckleWindowSize=100,
    speckleRange=32
)

disparity = stereo.compute(imgL, imgR).astype("float32") / 16.0

# 3. Visualizar mapa de disparidad (relativo a profundidad)
print("Guardando mapa de disparidad...")
plt.figure(figsize=(10, 6))
plt.imshow(disparity, cmap='inferno')
plt.colorbar(label='Disparidad (píxeles)')
plt.title("Mapa de Disparidad Estéreo")
plt.axis('off')
disparity_out = os.path.join(media_dir, 'mapa_disparidad.png')
plt.savefig(disparity_out, bbox_inches='tight')
plt.close()

# 4. Simular elevación a partir de disparidad:
print("Generando mapa de elevación...")
# Para evitar división por cero o valores negativos
disparity_safe = np.where(disparity <= 0, 1e-6, disparity)
depth_map = 1.0 / disparity_safe
depth_map[depth_map > 100] = 100 # Recorte para visualización
depth_map[depth_map < 0] = 0

# Para visualización 3D, suavizamos un poco el mapa de profundidad para evitar artefactos del matching
depth_map = cv2.GaussianBlur(depth_map, (9, 9), 0)

# Reducir la resolución para que Plotly renderice rápido y sin problemas (ej. 800x600 -> 400x300)
downscale_factor = 2
depth_map_small = cv2.resize(depth_map, (depth_map.shape[1]//downscale_factor, depth_map.shape[0]//downscale_factor))
texture_small = cv2.resize(imgL, (imgL.shape[1]//downscale_factor, imgL.shape[0]//downscale_factor))

# 5. Crear una malla 3D del terreno:
print("Creando malla 3D con textura...")
x, y = np.meshgrid(range(depth_map_small.shape[1]), range(depth_map_small.shape[0]))

# Escalar la profundidad para exagerar el relieve
z_surface = depth_map_small * 50

fig = go.Figure(data=[go.Surface(
    z=z_surface,
    x=x,
    y=y,
    surfacecolor=texture_small, # 6. Aplicar textura desde imagen original
    colorscale='gray',
    showscale=False
)])

fig.update_layout(
    title='Terreno Simulado (Reconstrucción 3D)',
    autosize=True,
    scene=dict(
        xaxis=dict(title='X'),
        yaxis=dict(title='Y'),
        zaxis=dict(title='Elevación'),
        aspectmode='data'
    )
)

# Guardar la imagen de la malla 3D (requiere el paquete kaleido que ya instalamos)
mesh_out = os.path.join(media_dir, 'malla_3d_terreno.png')
print(f"Guardando malla 3D en {mesh_out}...")
fig.write_image(mesh_out, width=1024, height=768)

# Guardar también como HTML interactivo por si el estudiante quiere manipularlo
html_out = os.path.join(media_dir, 'malla_3d_interactiva.html')
fig.write_html(html_out)

print("¡Proceso completado exitosamente!")
