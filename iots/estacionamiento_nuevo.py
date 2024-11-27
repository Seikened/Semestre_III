import cv2
import sys
import numpy as np

# Rutas de imágenes
url_base = "/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/iots/fotos/"
vacio = url_base + "vacio_normalized.jpeg"  # Imagen de referencia
tres = url_base + "tres_normalized.jpeg"    # Imagen a analizar
cinco = url_base + "cinco_normalized.jpeg"  # Imagen a analizar
seis = url_base + "seis_normalized.jpeg"    # Imagen a analizar

# Coordenadas de las ROIs (modifica según tus cajones)
ancho = 700
alto = 300
lugares_estacionamiento = [
    (24, 352, ancho, alto),  # Cajón 1
    (39, 876, ancho, alto),  # Cajón 2
    (34, 1388, ancho, alto),  # Cajón 3
    (1047, 375, ancho, alto),  # Cajón 4
    (1030, 896, ancho, alto),  # Cajón 5
    (1041, 1376, ancho, alto)  # Cajón 6
]

# Parámetros ajustables
umbral_diferencia_pixeles = 60  # Sensibilidad al cambio en los píxeles
umbral_porcentaje_ocupado = 18  # Porcentaje mínimo para considerar un lugar como ocupado


def cargar_imagenes(ruta_referencia, ruta_actual):
    """
    Carga las imágenes de referencia y actual.
    Convierte ambas a escala de grises para procesarlas.
    """
    img_ref = cv2.imread(ruta_referencia, cv2.IMREAD_GRAYSCALE)
    img_actual = cv2.imread(ruta_actual, cv2.IMREAD_COLOR)  # Mantener color para visualización
    img_actual_gray = cv2.cvtColor(img_actual, cv2.COLOR_BGR2GRAY)

    if img_ref is None or img_actual_gray is None:
        raise ValueError("No se pudieron cargar las imágenes.")
    if img_ref.shape != img_actual_gray.shape:
        raise ValueError("Las imágenes no tienen el mismo tamaño.")

    return img_ref, img_actual, img_actual_gray


def analizar_lugar(roi_referencia, roi_actual, umbral_pixeles, area_total):
    """
    Compara un ROI de la referencia y uno actual.
    Devuelve el estado basado en el porcentaje de píxeles blancos.
    """
    # Calcular diferencia absoluta entre ROIs
    diferencia = cv2.absdiff(roi_referencia, roi_actual)
    _, diferencia_binaria = cv2.threshold(diferencia, umbral_pixeles, 255, cv2.THRESH_BINARY)

    # Calcular porcentaje de píxeles blancos
    pixeles_blancos = cv2.countNonZero(diferencia_binaria)
    porcentaje_blancos = (pixeles_blancos / area_total) * 100

    return porcentaje_blancos, diferencia_binaria


def dibujar_resultados(imagen, x, y, w, h, estado, color, alpha=0.5):
    """
    Dibuja un rectángulo relleno semitransparente y un borde más grueso alrededor del lugar.
    Muestra el estado del lugar (Ocupado o Disponible).
    """
    overlay = imagen.copy()
    cv2.rectangle(overlay, (x, y), (x+w, y+h), color, -1)  # Relleno
    cv2.addWeighted(overlay, alpha, imagen, 1 - alpha, 0, imagen)  # Aplicar transparencia
    cv2.rectangle(imagen, (x, y), (x+w, y+h), color, thickness=6)  # Contorno
    return imagen


def procesar_estacionamiento(imagen_referencia, imagen_actual, lugares, umbral_pixeles, umbral_ocupado):
    """
    Evalúa cada lugar de estacionamiento, calcula su estado y dibuja resultados.
    """
    for i, (x, y, w, h) in enumerate(lugares, start=1):
        print(f"\n[INFO] Evaluando lugar {i} en ROI: x={x}, y={y}, ancho={w}, alto={h}")

        # Extraer ROIs
        roi_ref = imagen_referencia[y:y+h, x:x+w]
        roi_actual = imagen_actual[y:y+h, x:x+w]
        area_total = w * h

        # Analizar lugar
        porcentaje_blancos, diferencia_binaria = analizar_lugar(roi_ref, roi_actual, umbral_pixeles, area_total)
        estado = "Ocupado🔴" if porcentaje_blancos > umbral_ocupado else "Disponible🟢"

        # Determinar color (verde suave para disponible, rojo para ocupado)
        color = (0, 0, 255) if "Ocupado" in estado else (102, 255, 102)

        # Imprimir resultados en consola
        print(f"[RESULTADO] Lugar {i}:")
        print(f"  Píxeles blancos: {int(porcentaje_blancos * area_total / 100)} ({porcentaje_blancos:.2f}%)")
        print(f"  Estado: {estado}")

        # Dibujar resultados en la imagen
        dibujar_resultados(imagen_actual_color, x, y, w, h, estado, color)
        cv2.putText(imagen_actual_color, f"Lugar {i}: {estado}",
                    (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.imshow(f"Lugar {i} - Diferencia Binaria", diferencia_binaria)  # Opcional


# Main Script
try:
    imagen_referencia, imagen_actual_color, imagen_actual_gray = cargar_imagenes(vacio, seis)
    procesar_estacionamiento(imagen_referencia, imagen_actual_gray, lugares_estacionamiento,
                             umbral_diferencia_pixeles, umbral_porcentaje_ocupado)
    cv2.imshow("Estado del Estacionamiento", imagen_actual_color)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
except ValueError as e:
    print(f"Error: {e}")
    sys.exit()
