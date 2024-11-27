import cv2
import os
import json
import sys
import numpy as np
from skimage.metrics import structural_similarity as ssim


def cargar_imagen(ruta, escala_grises=False):
    """Carga una imagen desde una ruta específica."""
    flag = cv2.IMREAD_GRAYSCALE if escala_grises else cv2.IMREAD_COLOR
    imagen = cv2.imread(ruta, flag)
    if imagen is None:
        raise ValueError(f"No se pudo cargar la imagen desde {ruta}")
    print(f"[INFO] Imagen cargada desde {ruta}, dimensiones: {imagen.shape}")
    return imagen


def preprocesar_imagen(imagen):
    """Aplica preprocesamiento a la imagen para resaltar diferencias."""
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    desenfoque = cv2.GaussianBlur(gris, (5, 5), 0)
    print(f"[INFO] Imagen preprocesada, dimensiones: {gris.shape}, promedio de intensidad: {np.mean(gris):.2f}")
    return desenfoque


def calcular_diferencia_pixeles(roi1, roi2, umbral_pixeles=30):
    """Calcula la diferencia por píxeles entre dos regiones."""
    diff = cv2.absdiff(roi1, roi2)
    _, diff_bin = cv2.threshold(diff, umbral_pixeles, 255, cv2.THRESH_BINARY)
    porcentaje_diferencia = np.sum(diff_bin > 0) / np.prod(diff_bin.shape)
    print(f"[DEBUG] Diferencia de píxeles calculada: {porcentaje_diferencia:.2%}")
    return porcentaje_diferencia


def crear_mascara(imagen_shape, vertices):
    """Crea una máscara binaria para un polígono definido por vértices."""
    if len(vertices) == 0:
        raise ValueError("Los vértices de la máscara están vacíos.")
    mascara = np.zeros(imagen_shape[:2], dtype=np.uint8)
    vertices = np.array(vertices, np.int32)
    cv2.fillPoly(mascara, [vertices], 255)
    porcentaje_cubierto = np.sum(mascara > 0) / np.prod(mascara.shape)
    print(f"[INFO] Máscara creada, porcentaje de área cubierta: {porcentaje_cubierto:.2%}")
    return mascara


def aplicar_mascara(imagen, mascara):
    """Aplica una máscara binaria a una imagen."""
    resultado = cv2.bitwise_and(imagen, imagen, mask=mascara)
    print(f"[INFO] Máscara aplicada, dimensiones del resultado: {resultado.shape}")
    return resultado


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
    imagen = cargar_imagen(
        "/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/iots/fotos/vacio_normalized.jpeg"
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
    "/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/iots/fotos/vacio_normalized.jpeg"
)
foto_actual = (
    "/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/iots/fotos/seis_normalized.jpeg"
)

try:
    # Cargar imágenes
    imagen_referencia = cargar_imagen(foto_referencia, escala_grises=False)
    imagen_actual = cargar_imagen(foto_actual, escala_grises=False)

    # Validar que las imágenes sean del mismo tamaño
    if imagen_referencia.shape != imagen_actual.shape:
        raise ValueError("Las imágenes de referencia y actual no tienen el mismo tamaño.")

    # Preprocesar imágenes
    imagen_referencia_pre = preprocesar_imagen(imagen_referencia)
    imagen_actual_pre = preprocesar_imagen(imagen_actual)

    # Guardar preprocesadas para depuración
    cv2.imwrite("referencia_preprocesada.jpeg", imagen_referencia_pre)
    cv2.imwrite("actual_preprocesada.jpeg", imagen_actual_pre)

    # Evaluar cada lugar de estacionamiento
    for i, vertices in enumerate(lugares_estacionamiento, start=1):
        mascara = crear_mascara(imagen_referencia.shape, vertices)

        roi_referencia = aplicar_mascara(imagen_referencia_pre, mascara)
        roi_actual = aplicar_mascara(imagen_actual_pre, mascara)

        # Comparar las regiones (ROI)
        porcentaje_diferencia = calcular_diferencia_pixeles(roi_referencia, roi_actual)
        estado = "ocupado" if porcentaje_diferencia > 0.05 else "vacio"
        print(f"[RESULTADO] Lugar {i}: Diferencia = {porcentaje_diferencia:.2%}, Estado = {estado}")

        # Dibujar los polígonos en la imagen actual
        color = (0, 255, 0) if estado == "vacio" else (0, 0, 255)
        cv2.polylines(
            imagen_actual,
            [np.array(vertices, np.int32)],
            isClosed=True,
            color=color,
            thickness=2,
        )
        # Mostrar texto en la imagen
        cv2.putText(imagen_actual, f"Lugar {i}: {estado}", (vertices[0][0], vertices[0][1] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

    # Mostrar resultado final
    cv2.imshow("Estado del estacionamiento", imagen_actual)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

except Exception as e:
    print(f"Error: {e}")
    sys.exit()
