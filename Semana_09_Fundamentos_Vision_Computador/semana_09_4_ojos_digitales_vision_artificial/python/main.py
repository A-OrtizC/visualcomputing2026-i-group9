import cv2
import numpy as np

def nothing(x):
    pass

def main():
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        return

    window_name = 'Ojos Digitales - Vision Artificial'
    cv2.namedWindow(window_name)
    
    cv2.createTrackbar('Filtro', window_name, 0, 6, nothing)
    # Reducimos el máximo a 7 para evitar inestabilidad en los filtros de bordes de OpenCV
    cv2.createTrackbar('Kernel', window_name, 1, 7, nothing)

    filtros_nombres = [
        "Original", "Escala de Grises", "Gaussian Blur", 
        "Sharpening (Fijo 3x3)", "Sobel X", 
        "Sobel Y", "Laplacian"
    ]

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        
        filtro_idx = cv2.getTrackbarPos('Filtro', window_name)
        k_val = cv2.getTrackbarPos('Kernel', window_name)
        
        # k siempre impar (1, 3, 5, 7, 9, 11, 13, 15)
        k = k_val * 2 + 1 if k_val > 0 else 1
        
        # Para derivadas (Sobel/Laplacian), OpenCV recomienda máximo 7 y mínimo 3
        k_sobel = min(k, 7)
        if k_sobel == 1:
            k_sobel = 3

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        resultado = frame.copy()
        usa_kernel = False # Bandera para la interfaz

        if filtro_idx == 1: # Grises
            resultado = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            
        elif filtro_idx == 2: # Gaussian Blur
            resultado = cv2.GaussianBlur(frame, (k, k), 0)
            usa_kernel = True
            
        elif filtro_idx == 3: # Sharpening (Kernel FIJO)
            kernel_sharpen = np.array([[-1, -1, -1],
                                       [-1,  9, -1],
                                       [-1, -1, -1]])
            resultado = cv2.filter2D(frame, -1, kernel_sharpen)
            
        elif filtro_idx == 4: # Sobel X
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=k_sobel)
            resultado = cv2.cvtColor(cv2.convertScaleAbs(sobelx), cv2.COLOR_GRAY2BGR)
            usa_kernel = True
            k = k_sobel # Para mostrar en UI
            
        elif filtro_idx == 5: # Sobel Y
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=k_sobel)
            resultado = cv2.cvtColor(cv2.convertScaleAbs(sobely), cv2.COLOR_GRAY2BGR)
            usa_kernel = True
            k = k_sobel # Para mostrar en UI
            
        elif filtro_idx == 6: # Laplacian
            laplacian = cv2.Laplacian(gray, cv2.CV_64F, ksize=k_sobel)
            resultado = cv2.cvtColor(cv2.convertScaleAbs(laplacian), cv2.COLOR_GRAY2BGR)
            usa_kernel = True
            k = k_sobel # Para mostrar en UI

        # Texto dinámico en pantalla
        texto_kernel = f" (K: {k})" if usa_kernel else " (K: No aplica)"
        info_text = f"Filtro: {filtros_nombres[filtro_idx]}{texto_kernel}"
        
        cv2.putText(resultado, info_text, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow(window_name, resultado)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()