import cv2
import sys
import numpy as np
import os
import time
import urllib.request
import paho.mqtt.client as mqtt  # Biblioteca para MQTT

# Rutas de imágenes
IMG_PATH = "/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/iots/fotos/"
IMG_REF = os.path.join(IMG_PATH, "vacio_normalized.jpeg")
IMAGES_TEST = [
    os.path.join(IMG_PATH, "tres_normalized.jpeg"),
    os.path.join(IMG_PATH, "cinco_normalized.jpeg"),
    os.path.join(IMG_PATH, "seis_normalized.jpeg")
]

# Configuración ESP32-CAM
ESP32_URL = "http://172.20.10.2/capture"

# Coordenadas de las ROIs
ANCHO = 700
ALTO = 300
LUGARES_ESTACIONAMIENTO = [
    (24, 352, ANCHO, ALTO),
    (39, 876, ANCHO, ALTO),
    (34, 1388, ANCHO, ALTO),
    (1047, 375, ANCHO, ALTO),
    (1030, 896, ANCHO, ALTO),
    (1041, 1376, ANCHO, ALTO),
]

# Parámetros ajustables
UMBRAL_PIXELES = 60
UMBRAL_OCUPADO = 18  # PORCENTAJE MÍNIMO PARA DETECTAR OCUPACIÓN

# Configuración MQTT
mqtt_broker = "a93ced358b004f36b2d791f6c69aba07.s1.eu.hivemq.cloud"
mqtt_port = 8883
mqtt_username = "SantRR2"
mqtt_password = "Arbolito123"
mqtt_topics = [f"lugar_{i}" for i in range(1, 7)]  # Tópicos para los lugares

# Inicializar cliente MQTT
client = mqtt.Client()
client.username_pw_set(mqtt_username, mqtt_password)
client.tls_set()

# Intentar conexión con MQTT
try:
    client.connect(mqtt_broker, mqtt_port, 60)
    client.loop_start()
    print("[INFO] Conectado al broker MQTT")
except Exception as e:
    print(f"[ERROR] No se pudo conectar al broker MQTT: {e}")


def cargar_imagen_vacio():
    """Verifica si la imagen de referencia existe, de lo contrario permite capturarla."""
    if not os.path.exists(IMG_REF):
        print("[INFO] No se encontró la imagen de referencia. Capturando ahora...")
        capturar_imagen(IMG_REF)
    return cv2.imread(IMG_REF, cv2.IMREAD_GRAYSCALE)


def capturar_imagen(destino):
    """Captura una imagen desde la ESP32-CAM y la guarda en el destino."""
    while True:
        try:
            print("[INFO] Posiciona la cámara. Presiona 'Espacio' para capturar.")
            response = urllib.request.urlopen(ESP32_URL)
            image_np = np.array(bytearray(response.read()), dtype=np.uint8)
            image = cv2.imdecode(image_np, -1)
            cv2.imshow("Capturar Imagen", image)
            if cv2.waitKey(1) & 0xFF == ord(' '):  # Capturar con espacio
                cv2.imwrite(destino, image)
                print(f"[INFO] Imagen guardada como: {destino}")
                break
        except Exception as e:
            print(f"[ERROR] No se pudo capturar la imagen: {e}")
    cv2.destroyAllWindows()


def cargar_imagen_actual(modo, img_path=None):
    """Carga una imagen en función del modo seleccionado."""
    if modo == "prueba" and img_path:
        return cv2.imread(img_path, cv2.IMREAD_COLOR)
    elif modo == "streaming":
        try:
            response = urllib.request.urlopen(ESP32_URL)
            image_np = np.array(bytearray(response.read()), dtype=np.uint8)
            return cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        except Exception as e:
            print(f"[ERROR] No se pudo obtener la imagen actual: {e}")
            return None
    return None


def analizar_lugar(roi_ref, roi_actual, area_total):
    """Analiza un ROI y devuelve el porcentaje de píxeles blancos y la diferencia binaria."""
    diferencia = cv2.absdiff(roi_ref, roi_actual)
    _, diferencia_binaria = cv2.threshold(diferencia, UMBRAL_PIXELES, 255, cv2.THRESH_BINARY)
    pixeles_blancos = cv2.countNonZero(diferencia_binaria)
    porcentaje_blancos = (pixeles_blancos / area_total) * 100
    return porcentaje_blancos, diferencia_binaria


def dibujar_resultados(imagen, x, y, w, h, estado, color):
    """Dibuja resultados en la imagen: rectángulo y transparencia."""
    overlay = imagen.copy()
    cv2.rectangle(overlay, (x, y), (x+w, y+h), color, -1)  # Relleno
    cv2.addWeighted(overlay, 0.5, imagen, 0.5, 0, imagen)  # Transparencia
    cv2.rectangle(imagen, (x, y), (x+w, y+h), color, 4)  # Contorno grueso
    return imagen


def procesar_estacionamiento(img_ref, img_actual_color, img_actual_gray):
    """Procesa cada lugar de estacionamiento, calcula estado y dibuja resultados."""
    for i, (x, y, w, h) in enumerate(LUGARES_ESTACIONAMIENTO, start=1):
        roi_ref = img_ref[y:y+h, x:x+w]
        roi_actual = img_actual_gray[y:y+h, x:x+w]
        area_total = w * h

        porcentaje_blancos, diferencia_binaria = analizar_lugar(roi_ref, roi_actual, area_total)
        estado = "Ocupado🔴" if porcentaje_blancos > UMBRAL_OCUPADO else "Disponible🟢"
        color = (0, 0, 255) if "Ocupado" in estado else (102, 255, 102)

        # Publicar resultados a MQTT
        mqtt_estado = "ocupado" if "Ocupado" in estado else "vacío"
        client.publish(mqtt_topics[i-1], mqtt_estado)
        print(f"[MQTT] Publicado en {mqtt_topics[i-1]}: {mqtt_estado}")

        # Imprimir resultados
        print(f"[RESULTADO] Lugar {i}: {estado} ({porcentaje_blancos:.2f}%)")

        # Dibujar resultados
        img_actual_color = dibujar_resultados(img_actual_color, x, y, w, h, estado, color)
        cv2.imshow(f"Lugar {i} - Diferencia Binaria", diferencia_binaria)

    return img_actual_color


# Main
if __name__ == "__main__":
    print("Selecciona el modo:")
    print("1. Modo de prueba (imágenes locales)")
    print("2. Streaming en vivo (ESP32-CAM)")
    opcion = input("Elige una opción (1 o 2): ")

    img_ref = cargar_imagen_vacio()

    if opcion == "1":
        print("[INFO] Modo de prueba seleccionado.")
        for img_path in IMAGES_TEST:
            img_actual_color = cargar_imagen_actual("prueba", img_path)
            img_actual_gray = cv2.cvtColor(img_actual_color, cv2.COLOR_BGR2GRAY)
            img_actual_color = procesar_estacionamiento(img_ref, img_actual_color, img_actual_gray)
            cv2.imshow("Estado del Estacionamiento", img_actual_color)
            if cv2.waitKey(0) & 0xFF == ord('q'):
                break
    elif opcion == "2":
        print("[INFO] Modo de streaming seleccionado.")
        while True:
            img_actual_color = cargar_imagen_actual("streaming")
            if img_actual_color is None:
                time.sleep(2)
                continue
            img_actual_gray = cv2.cvtColor(img_actual_color, cv2.COLOR_BGR2GRAY)
            img_actual_color = procesar_estacionamiento(img_ref, img_actual_color, img_actual_gray)
            cv2.imshow("Estado del Estacionamiento", img_actual_color)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    else:
        print("[ERROR] Opción no válida. Saliendo.")
        sys.exit()

    cv2.destroyAllWindows()