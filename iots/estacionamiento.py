# -*- coding: utf-8 -*-
"""Compara una imagen con una referencia @author: Myriam"""

import cv2  # Librería OpenCV para procesar imágenes
import sys  # sys maneja errores

# Ruta de las imágenes que va a comparar, es necesario que las imágenes tengan
# el mismo tamaño y la misma perspectiva
foto_referencia = (
    "/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/iots/fotos/imagen.jpg"
)
foto_actual = (
    "/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/iots/fotos/imagen2.jpg"
)

# Delimita la Region de Interés (ROI) dentro de las imágenes
# Coordenadas de la caja, el formato es (x, y, ancho, alto)
# donde x,y son las coordenadas de la esquina superior izquierda de la caja
# todos estos numeros son los pixeles
caja = (0, 0, 320, 240)  # Ajusta según las coordenadas del cajón

# Cargar imágenes y cambiar a escala de grises para facilitar el análisis
# También se puede hacer en color cv2.IMREAD_COLOR pero lo hace más lento
imagen_referencia = cv2.imread(foto_referencia, cv2.IMREAD_GRAYSCALE)
imagen_actual = cv2.imread(foto_actual, cv2.IMREAD_GRAYSCALE)

# Si las impagenes no se cargaron correctamente, imprime un error y termina
if imagen_referencia is None or imagen_actual is None:
    print("Error: No se cargaron las imágenes")
    sys.exit()

# Extraer la ROI (Región de interés) para la caja en ambas imágenes
x, y, w, h = caja
roi_referencia = imagen_referencia[y : y + h, x : x + w]
roi_actual = imagen_actual[y : y + h, x : x + w]

# Calcular la diferencia entre las dos imágenes y la convierte en una imagen
# binaria
diferencia = cv2.absdiff(roi_referencia, roi_actual)

# Aplicar un umbral para resaltar las diferencias, pixeles mayores a 30 se
# vuelven blancos (255), el resto, se vuelven negros
_, diferencia_binaria = cv2.threshold(diferencia, 30, 255, cv2.THRESH_BINARY)

# Contar los píxeles blncos (diferentes) en la imagen
diferencia_total = cv2.countNonZero(diferencia_binaria)

# Definir un umbral para decidir si el pato se encuentra o no dentro de la caja
# este numero es el maximo de pixeles diferentes que pueden presentarse entre ambas imágenes
umbral_diferencia = 300

# Determinar el estado del pato
estado = (
    "hay cambio"
    if diferencia_total > umbral_diferencia
    else "no hay cambio en las fotos"
)
print(f"{estado}")

# Mostrar las imágenes y resultados
cv2.imshow("Referencia (Caja vacia)", roi_referencia)
cv2.imshow("Actual (imagen a evaluar)", roi_actual)
cv2.imshow("Diferencia", diferencia_binaria)

# Redimensionar las ventanas
cv2.namedWindow("Referencia (Caja vacia)", cv2.WINDOW_NORMAL)
cv2.namedWindow("Actual (imagen a evaluar)", cv2.WINDOW_NORMAL)
cv2.namedWindow("Diferencia", cv2.WINDOW_NORMAL)

cv2.resizeWindow("Referencia (Caja vacia)", 600, 400)
cv2.resizeWindow("Actual (imagen a evaluar)", 600, 400)
cv2.resizeWindow("Diferencia", 600, 400)

# Esperar a que el usuario cierre las ventanas o presione una tecla para terminar el programa
cv2.waitKey(0)
cv2.destroyAllWindows()
