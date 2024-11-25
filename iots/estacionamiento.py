import cv2
import os
import json
import sys
import numpy as np
from skimage.metrics import structural_similarity as ssim

def cargar_imagen(ruta, escala_grises=True):
    """Carga una imagen desde una ruta específica."""
    flag = cv2.IMREAD_GRAYSCALE if escala_grises else cv2.IMREAD_COLOR
    imagen = cv2.imread(ruta, flag)
    if imagen is None:
        raise ValueError(f"No se pudo cargar la imagen desde {ruta}")
    return imagen

def calcular_similitud(roi1, roi2):
    """Calcula el índice de similitud estructural (SSIM) entre dos ROIs."""
    return ssim(roi1, roi2, full=True)

def crear_mascara(imagen_shape, vertices):
    """Crea una máscara binaria para un polígono definido por vértices."""
    mascara = np.zeros(imagen_shape[:2], dtype=np.uint8)
    # Mostrar imagen al usuario para verla
    cv2.imshow("Setup de cajones", mascara)
    cv2.fillPoly(mascara, [np.array(vertices, np.int32)], 255)
    return mascara

def aplicar_mascara(imagen, mascara):
    """Aplica una máscara binaria a una imagen."""
    return cv2.bitwise_and(imagen, imagen, mask=mascara)

def guardar_coordenadas(ruta_archivo, coordenadas):
    """Guarda las coordenadas de los cajones en un archivo JSON."""
    with open(ruta_archivo, "w") as archivo:
        json.dump(coordenadas, archivo, indent=4)
    print(f"Coordenadas guardadas en {ruta_archivo}")

def cargar_coordenadas(ruta_archivo):
    """Carga las coordenadas de los cajones desde un archivo JSON."""
    if os.path.exists(ruta_archivo):
        with open(ruta_archivo, "r") as archivo:
            return json.load(archivo)
    else:
        print("No se encontraron coordenadas guardadas. Realiza el setup inicial.")
        return []

# Ruta del archivo para guardar coordenadas
archivo_coordenadas = "lugares_estacionamiento.json"

# Cargar las coordenadas guardadas o realizar setup inicial
lugares_estacionamiento = cargar_coordenadas(archivo_coordenadas)

if not lugares_estacionamiento:  # Si no hay coordenadas, ejecutar setup inicial
    print("No se encontraron coordenadas. Realiza el setup inicial.")
    imagen = cv2.imread(
        "/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/iots/fotos/original.jpg"
    )
    vertices_cajon = []

    def seleccionar_cajones(event, x, y, flags, param):
        global vertices_cajon, lugares_estacionamiento, imagen
        if event == cv2.EVENT_LBUTTONDOWN:
            vertices_cajon.append((x, y))
            cv2.circle(imagen, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow("Setup de cajones", imagen)
            if len(vertices_cajon) == 4:  # Completar cajón
                lugares_estacionamiento.append(vertices_cajon.copy())
                cv2.polylines(
                    imagen,
                    [np.array(vertices_cajon, np.int32)],
                    isClosed=True,
                    color=(255, 0, 0),
                    thickness=2,
                )
                vertices_cajon = []  # Reiniciar para el siguiente cajón

    cv2.imshow("Setup de cajones", imagen)
    cv2.setMouseCallback("Setup de cajones", seleccionar_cajones)
    cv2.waitKey(0)
    guardar_coordenadas(archivo_coordenadas, lugares_estacionamiento)
    cv2.destroyAllWindows()

# Imágenes para probar
foto_referencia = (
    "/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/iots/fotos/vacio.jpg"
)
foto_actual = (
    "/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/iots/fotos/seiscohes.jpg"
)

try:
    # Cargar imágenes
    imagen_referencia = cargar_imagen(foto_referencia)
    imagen_actual = cargar_imagen(foto_actual)

    # Evaluar cada lugar de estacionamiento
    for i, vertices in enumerate(lugares_estacionamiento, start=1):
        mascara = crear_mascara(imagen_referencia.shape, vertices)
        roi_referencia = aplicar_mascara(imagen_referencia, mascara)
        roi_actual = aplicar_mascara(imagen_actual, mascara)

        # Comparar las regiones (ROI)
        similaridad, _ = calcular_similitud(roi_referencia, roi_actual)
        estado = "ocupado" if similaridad < 0.8 else "vacío"
        print(f"Lugar {i}: Similitud = {similaridad:.2f}, Estado = {estado}")

        # Dibujar los polígonos en la imagen actual
        color = (0, 255, 0) if estado == "vacío" else (0, 0, 255)
        cv2.polylines(imagen_actual,[np.array(vertices, np.int32)],isClosed=True,color=color,thickness=2,)

    cv2.imshow("Estado del estacionamiento", imagen_actual)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

except Exception as e:
    print(f"Error: {e}")
    sys.exit()