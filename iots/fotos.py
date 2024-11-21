# -*- coding: utf-8 -*-
""" Toma una foto, la guarda y la muestra en una ventana @author: Myriam """

import urllib.request
import cv2
import numpy as np

# Cambiar por la URL de la ESP32cam
url = "http://172.20.10.11/capture"

# Ruta donde se guardará la imagen

ruta_imagen = "/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/iots/fotos/imagen2.jpg"

while True:
    # Descargar la imagen desde la ESP32cam
    response = urllib.request.urlopen(url)
    image_np = np.array(bytearray(response.read()), dtype=np.uint8)
    image = cv2.imdecode(image_np, -1)

    # Guardar la imagen en la ruta especificada, si ya hay una, la 
    # sobrescribe. Avisa en la consola cada vez que guarda una imagen nueva
    cv2.imwrite(ruta_imagen, image)
    print("Imagen guardada en:", ruta_imagen)

    # Mostrar la imagen en una ventana
    cv2.imshow("Imagen desde ESP32cam", image)

    # Esperar 30 segundos o salir si se presiona la tecla 'ESC'
    if cv2.waitKey(30000) & 0xFF == 27:
        break

cv2.destroyAllWindows()