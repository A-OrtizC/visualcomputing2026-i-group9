Usa gitbash en la carpeta donde se encuentre aljoado el sript y ejecuta las siguientes lineas(debes tener instalado python3.10 para que funcione correctamente):

# 1. Crear el entorno limpio
py -3.10 -m venv venv

# 2. Activar
source venv/Scripts/activate

# 3. Instalar
pip install mediapipe==0.10.14 opencv-python numpy

# 4. Ejecutar
python main.py