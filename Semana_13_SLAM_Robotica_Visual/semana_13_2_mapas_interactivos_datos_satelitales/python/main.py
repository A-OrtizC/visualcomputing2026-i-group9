import os
import webbrowser
import numpy as np
import rasterio
from rasterio.plot import show
from rasterio.warp import transform_bounds
import matplotlib.pyplot as plt
import folium
import geopandas as gpd
from folium.raster_layers import ImageOverlay
from branca.colormap import linear

# ============================================================
# CONFIGURACIÓN
# ============================================================

RED_BAND = "B4.tif"
NIR_BAND = "B5.tif"
VECTOR_FILE = "rutas.geojson"

# ============================================================
# VALIDAR ARCHIVOS
# ============================================================

if not os.path.exists(RED_BAND):
    print(f"ERROR: No existe {RED_BAND}")
    exit()

if not os.path.exists(NIR_BAND):
    print(f"ERROR: No existe {NIR_BAND}")
    exit()

# ============================================================
# LEER BANDAS SATELITALES
# ============================================================

print("Abriendo bandas satelitales...")

red_src = rasterio.open(RED_BAND)
nir_src = rasterio.open(NIR_BAND)

print("\nInformación del TIFF:")
print(red_src.meta)

print("\nCRS:")
print(red_src.crs)

# ============================================================
# MOSTRAR BANDA ROJA
# ============================================================

plt.figure(figsize=(10, 8))

show(red_src, cmap='Reds', title="Banda Roja (B4)")

# ============================================================
# LEER ARRAYS
# ============================================================

red = red_src.read(1).astype("float32")

nir = nir_src.read(1).astype("float32")

# ============================================================
# CALCULAR NDVI
# ============================================================

print("\nCalculando NDVI...")

np.seterr(divide='ignore', invalid='ignore')

ndvi = (nir - red) / (nir + red)

ndvi = np.nan_to_num(ndvi)

print("NDVI calculado correctamente")

# ============================================================
# MOSTRAR NDVI
# ============================================================

plt.figure(figsize=(12, 8))

plt.imshow(ndvi, cmap='RdYlGn')

plt.title("Mapa NDVI")

plt.colorbar(label='NDVI')

plt.axis("off")

plt.show()

# ============================================================
# GUARDAR NDVI COMO PNG
# ============================================================

plt.imsave(
    "ndvi.png",
    ndvi,
    cmap='RdYlGn'
)

print("Imagen NDVI guardada como ndvi.png")

# ============================================================
# TRANSFORMAR COORDENADAS A EPSG:4326
# ============================================================

bounds = transform_bounds(
    red_src.crs,
    "EPSG:4326",
    *red_src.bounds
)

left, bottom, right, top = bounds

print("\nBounds transformados:")
print(bounds)

# ============================================================
# CENTRO DEL MAPA
# ============================================================

center_lat = (top + bottom) / 2
center_lon = (left + right) / 2

# ============================================================
# CREAR MAPA
# ============================================================

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=12
)

# Ajustar mapa al TIFF
m.fit_bounds([
    [bottom, left],
    [top, right]
])

# ============================================================
# CAPAS BASE
# ============================================================

folium.TileLayer(
    'OpenStreetMap',
    name='OpenStreetMap'
).add_to(m)

folium.TileLayer(
    'CartoDB positron',
    name='CartoDB'
).add_to(m)

folium.TileLayer(
    'CartoDB dark_matter',
    name='Dark'
).add_to(m)

# ============================================================
# OVERLAY NDVI
# ============================================================

ImageOverlay(
    image=ndvi,
    bounds=[[bottom, left], [top, right]],
    opacity=0.6,
    name='NDVI',
    interactive=True
).add_to(m)

# ============================================================
# CARGAR GEOJSON
# ============================================================

if os.path.exists(VECTOR_FILE):

    print("\nCargando GeoJSON...")

    rutas = gpd.read_file(VECTOR_FILE)

    print("\nColumnas disponibles:")
    print(rutas.columns)

    # Convertir CRS si es necesario
    if rutas.crs is not None and rutas.crs != "EPSG:4326":
        rutas = rutas.to_crs(epsg=4326)

    # Mostrar capa vectorial
    rutas.plot(figsize=(10, 8))

    plt.title("Capas Vectoriales")

    plt.show()

    # Agregar al mapa
    folium.GeoJson(
        rutas,
        name="Rutas",
        tooltip=folium.GeoJsonTooltip(
            fields=["nombre"],
            aliases=["Zona:"]
        ),
        style_function=lambda x: {
            "fillColor": "blue",
            "color": "red",
            "weight": 3,
            "fillOpacity": 0.2
        }
    ).add_to(m)

else:
    print("\nNo se encontró rutas.geojson")

# ============================================================
# CLICK PARA COORDENADAS
# ============================================================

folium.LatLngPopup().add_to(m)

# ============================================================
# LEYENDA NDVI
# ============================================================

colormap = linear.RdYlGn_11.scale(-1, 1)

colormap.caption = "Indice NDVI"

colormap.add_to(m)

# ============================================================
# CONTROL DE CAPAS
# ============================================================

folium.LayerControl().add_to(m)

# ============================================================
# ESTADÍSTICAS
# ============================================================

print("\n========================")
print("ESTADISTICAS NDVI")
print("========================")

print(f"NDVI minimo: {np.min(ndvi):.4f}")
print(f"NDVI maximo: {np.max(ndvi):.4f}")
print(f"NDVI promedio: {np.mean(ndvi):.4f}")

# ============================================================
# HISTOGRAMA
# ============================================================

plt.figure(figsize=(10, 6))

plt.hist(
    ndvi.flatten(),
    bins=50
)

plt.title("Histograma NDVI")

plt.xlabel("Valor NDVI")

plt.ylabel("Frecuencia")

plt.show()

# ============================================================
# GUARDAR HTML
# ============================================================

output_map = "mapa_interactivo.html"

m.save(output_map)

print(f"\nMapa guardado en: {output_map}")

# ============================================================
# ABRIR NAVEGADOR
# ============================================================

webbrowser.open(output_map)

print("\nMapa abierto en el navegador")