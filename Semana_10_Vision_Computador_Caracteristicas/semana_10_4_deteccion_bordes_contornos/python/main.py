import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import filters, measure
import math

def mostrar_imagenes(titulos, imagenes, filas, columnas, figsize=(15, 10)):
    """Función auxiliar para mostrar múltiples imágenes con matplotlib."""
    fig, axes = plt.subplots(filas, columnas, figsize=figsize)
    # Si solo hay una fila o columna, axes podría no ser un array 2D
    if filas * columnas == 1:
        axes = [axes]
    else:
        axes = axes.ravel()
        
    for i in range(len(axes)):
        if i < len(imagenes):
            if len(imagenes[i].shape) == 2:
                axes[i].imshow(imagenes[i], cmap='gray')
            else:
                axes[i].imshow(cv2.cvtColor(imagenes[i], cv2.COLOR_BGR2RGB))
            axes[i].set_title(titulos[i])
        
        # Ocultar siempre los ejes
        axes[i].axis('off')
        
    plt.tight_layout()
    plt.show()

def paso1_operadores_basicos(img_gray):
    print("--- 1. Operadores Básicos de Detección de Bordes ---")
    sobel_x = cv2.Sobel(img_gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(img_gray, cv2.CV_64F, 0, 1, ksize=3)
    sobel_mag = cv2.magnitude(sobel_x, sobel_y)
    
    prewitt_edges = filters.prewitt(img_gray)
    laplacian = cv2.Laplacian(img_gray, cv2.CV_64F)
    
    scharr_x = cv2.Scharr(img_gray, cv2.CV_64F, 1, 0)
    scharr_y = cv2.Scharr(img_gray, cv2.CV_64F, 0, 1)
    scharr_mag = cv2.magnitude(scharr_x, scharr_y)

    sobel_mag = np.uint8(np.absolute(sobel_mag))
    laplacian = np.uint8(np.absolute(laplacian))
    scharr_mag = np.uint8(np.absolute(scharr_mag))

    titulos = ['Original Gris', 'Sobel Magnitud', 'Prewitt', 'Laplaciano', 'Scharr Magnitud']
    imagenes = [img_gray, sobel_mag, prewitt_edges, laplacian, scharr_mag]
    mostrar_imagenes(titulos, imagenes, 2, 3)

def paso2_detector_canny(img_gray):
    print("--- 2. Detector de Bordes de Canny ---")
    blur_bajo = cv2.GaussianBlur(img_gray, (3, 3), sigmaX=0.5)
    blur_alto = cv2.GaussianBlur(img_gray, (9, 9), sigmaX=2.0)

    canny_sin_filtro = cv2.Canny(img_gray, 50, 150)
    canny_blur_bajo = cv2.Canny(blur_bajo, 50, 150)
    canny_blur_alto = cv2.Canny(blur_alto, 50, 150)
    
    canny_umb_bajo = cv2.Canny(blur_bajo, 10, 50)
    canny_umb_alto = cv2.Canny(blur_bajo, 150, 200)

    titulos = ['Sin Filtro', 'Blur (sigma=0.5)', 'Blur (sigma=2.0)', 'Umbrales Bajos', 'Umbrales Altos']
    imagenes = [canny_sin_filtro, canny_blur_bajo, canny_blur_alto, canny_umb_bajo, canny_umb_alto]
    mostrar_imagenes(titulos, imagenes, 2, 3)

def paso3_y_4_contornos_y_formas(img_color, img_gray):
    print("--- 3 & 4. Detección de Contornos y Aproximación de Formas ---")
    img_resultado = img_color.copy()
    blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    contornos, jerarquia = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    area_minima = 500
    area_maxima = 50000
    
    for cnt in contornos:
        area = cv2.contourArea(cnt)
        if area_minima < area < area_maxima:
            perimetro = cv2.arcLength(cnt, True)
            epsilon = 0.04 * perimetro
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            cv2.drawContours(img_resultado, [approx], -1, (0, 255, 0), 2)
            
            vertices = len(approx)
            x, y, w, h = cv2.boundingRect(approx)
            forma = "Desconocida"
            
            if vertices == 3:
                forma = "Triangulo"
            elif vertices == 4:
                aspect_ratio = float(w)/h
                forma = "Cuadrado" if 0.95 <= aspect_ratio <= 1.05 else "Rectangulo"
            elif vertices == 5:
                forma = "Pentagono"
            elif vertices > 5:
                circularidad = 4 * np.pi * (area / (perimetro * perimetro))
                forma = "Circulo" if circularidad > 0.8 else "Poligono"
            
            cv2.putText(img_resultado, forma, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    titulos = ['Binarización Adaptativa', 'Detección y Clasificación']
    imagenes = [thresh, img_resultado]
    mostrar_imagenes(titulos, imagenes, 1, 2, figsize=(12, 6))
    return thresh, contornos

def paso5_y_6_momentos_e_inspeccion(img_color, thresh, contornos):
    print("--- 5 & 6. Análisis de Momentos e Inspección ---")
    img_inspeccion = img_color.copy()
    objetos_validos = 0
    defectos = 0
    
    etiquetas = measure.label(thresh)
    propiedades = measure.regionprops(etiquetas)
    
    for cnt, prop in zip(contornos, propiedades):
        area = cv2.contourArea(cnt)
        if area < 500: continue
            
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            excentricidad = prop.eccentricity
            orientacion = prop.orientation
            
            if excentricidad < 0.4 and area > 1000:
                color, estado = (0, 255, 0), "OK"
                objetos_validos += 1
            else:
                color, estado = (0, 0, 255), "DEFECTO"
                defectos += 1

            cv2.drawContours(img_inspeccion, [cnt], -1, color, 2)
            cv2.circle(img_inspeccion, (cx, cy), 5, (255, 0, 0), -1)
            
            x_fin = int(cx + 20 * math.cos(orientacion))
            y_fin = int(cy + 20 * math.sin(orientacion))
            cv2.line(img_inspeccion, (cx, cy), (x_fin, y_fin), (255, 255, 0), 2)
            cv2.putText(img_inspeccion, f"{estado}", (cx - 20, cy - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    resumen = f"Validos: {objetos_validos} | Defectos: {defectos}"
    cv2.putText(img_inspeccion, resumen, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    mostrar_imagenes(['Control de Calidad (Momentos & Inspección)'], [img_inspeccion], 1, 1, figsize=(8, 8))

def ejecutar_bonus(img_color, img_gray, contornos):
    print("--- BONUS: Esquinas, Medición y OCR Simple ---")
    img_esquinas = img_color.copy()
    img_medida = img_color.copy()
    img_ocr = img_color.copy()

    # 1. Shi-Tomasi (Detección de esquinas)
    esquinas = cv2.goodFeaturesToTrack(img_gray, maxCorners=50, qualityLevel=0.01, minDistance=10)
    if esquinas is not None:
        esquinas = np.int32(esquinas)
        for i in esquinas:
            x, y = i.ravel()
            cv2.circle(img_esquinas, (x, y), 4, (0, 165, 255), -1)

    # 2. Medición de objetos con referencia
    # Asumimos que el objeto con el área más grande es nuestra referencia conocida (ej: 5.0 cm)
    if len(contornos) > 0:
        contornos_ordenados = sorted(contornos, key=cv2.contourArea, reverse=True)
        cnt_referencia = contornos_ordenados[0]
        x, y, w, h = cv2.boundingRect(cnt_referencia)
        
        ancho_real_cm = 5.0  # Medida conocida ficticia
        pixeles_por_cm = w / ancho_real_cm
        
        for cnt in contornos_ordenados[:5]:  # Medir los 5 más grandes
            rect = cv2.minAreaRect(cnt)
            (cx, cy), (dim_w, dim_h), angle = rect
            box = cv2.boxPoints(rect)
            box = np.int32(box)
            
            ancho_obj = dim_w / pixeles_por_cm
            alto_obj = dim_h / pixeles_por_cm
            
            cv2.drawContours(img_medida, [box], 0, (0, 255, 0), 2)
            cv2.putText(img_medida, f"{ancho_obj:.1f}x{alto_obj:.1f}cm", (int(cx)-20, int(cy)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1, cv2.LINE_AA)

    # 3. OCR Simple usando contornos
    # Usamos heurísticas simples (solidez y proporción) para adivinar "letras" o "números"
    blur_ocr = cv2.GaussianBlur(img_gray, (3, 3), 0)
    thresh_ocr = cv2.adaptiveThreshold(blur_ocr, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 5)
    cnts_ocr, _ = cv2.findContours(thresh_ocr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in cnts_ocr:
        x, y, w, h = cv2.boundingRect(cnt)
        area = cv2.contourArea(cnt)
        
        # Filtrar por tamaño de "carácter" típico
        if 50 < area < 800 and 10 < w < 100 and 10 < h < 100:
            aspect_ratio = w / float(h)
            extent = area / float(w * h) # Solidez del rectángulo delimitador
            
            caracter = "?" # Desconocido
            if aspect_ratio < 0.4:
                caracter = "1" # Delgado y alto
            elif aspect_ratio > 0.8 and extent > 0.7:
                caracter = "0" # Cuadrado y muy sólido
            elif 0.5 < aspect_ratio < 0.9 and extent < 0.5:
                caracter = "A" # Forma de triángulo vacío
                
            cv2.rectangle(img_ocr, (x, y), (x + w, y + h), (255, 255, 0), 1)
            cv2.putText(img_ocr, caracter, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    titulos = ['Shi-Tomasi (Esquinas)', 'Medición (Ref = 5cm)', 'Segmentación OCR Simple']
    imagenes = [img_esquinas, img_medida, img_ocr]
    mostrar_imagenes(titulos, imagenes, 1, 3, figsize=(15, 5))

def main():
    ruta_imagen = 'imagen_prueba.jpg' 
    img_color = cv2.imread(ruta_imagen)
    
    if img_color is None:
        print(f"Error: No se pudo cargar '{ruta_imagen}'.")
        return

    max_dimension = 800
    h, w = img_color.shape[:2]
    if max(h, w) > max_dimension:
        escala = max_dimension / max(h, w)
        img_color = cv2.resize(img_color, (int(w * escala), int(h * escala)))

    img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)

    paso1_operadores_basicos(img_gray)
    paso2_detector_canny(img_gray)
    thresh, contornos = paso3_y_4_contornos_y_formas(img_color, img_gray)
    paso5_y_6_momentos_e_inspeccion(img_color, thresh, contornos)
    
    # Ejecutar la función combinada del Bonus
    ejecutar_bonus(img_color, img_gray, contornos)
    
    print("¡Taller completado con éxito!")

if __name__ == "__main__":
    main()