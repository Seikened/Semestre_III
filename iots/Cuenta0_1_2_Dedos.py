import cv2
import mediapipe as mp
import paho.mqtt.client as mqtt  # Instalar biblioteca para poder comunicar con el broker MQTT
import urllib.request  # Para poder leer la imagen desde un link url
import numpy as np
import time

ruta_certificado = (
    "/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/iots/root_ca.pem"
)

# Leer el contenido del certificado para verificar que se carga correctamente
with open(ruta_certificado, "r") as cert_file:
    contenido_certificado = cert_file.read()

# Imprimir solo una parte del certificado para confirmar que está cargado
print("Contenido del certificado (parcial):")
print(contenido_certificado[:100] + "\n...\n" + contenido_certificado[-100:])

# Configurar MQTT
mqtt_broker = "a93ced358b004f36b2d791f6c69aba07.s1.eu.hivemq.cloud"
mqtt_port = 8883
mqtt_topic = "indice"
mqtt_topic = "medio"
mqtt_topic = "anular"
mqtt_topic = "menique"

mqtt_username = "SantRR2"
mqtt_password = "Arbolito123"

# Inicializar cliente MQTT, puerto del broker y TLS para conexiones seguras
client = mqtt.Client()
client.username_pw_set(mqtt_username, mqtt_password)
client.tls_set()


try:
    client.connect(mqtt_broker, mqtt_port, 60)
    client.loop_start()
    print("Conectado al broker MQTT")
except Exception as e:
    print(f"La conexión al broker falló, error: {e}")


# Inicializar MediaPipe Hands, que es el módulo de detección de manos y la biblioteca que dibuja las
# referencias de la mano en la imagen
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Captura el video desde la URL de la ESP32-CAM.
esp32_cam_url = "http://172.20.10.11/capture"


def contar_dedos(hand_landmarks):
    # Dedos: índice, medio
    dedos_ids = [8, 12, 16, 20]

    dedos_levantados_list = [False, False, False, False]

    # Comparar posición de los dedos índice y medio con el punto de referencia (nudillo) y regresa
    # el numero de dedos arriba de la mano derecha. Si la posición del punto de referencia del dedo es más
    # alta que el del nudillo, se considera que el dedo está levantado. se usa el eje y para la comparación.
    for p, id in enumerate(dedos_ids):
        if hand_landmarks.landmark[id].y < hand_landmarks.landmark[id - 2].y:
            if id == 8:
                dedos_levantados_list[0] = True
            elif id == 12:
                dedos_levantados_list[1] = True
            elif id == 16:
                dedos_levantados_list[2] = True
            elif id == 20:
                dedos_levantados_list[3] = True
            else:
                dedos_levantados_list = [False, False, False, False]

    return dedos_levantados_list


while True:
    # Obtener la imagen desde la ESP32-CAM con urllib.request y luego la convierte a una
    # imagen OpenCV que si puede procesar
    response = urllib.request.urlopen(esp32_cam_url)
    image_np = np.array(bytearray(response.read()), dtype=np.uint8)
    image = cv2.imdecode(image_np, -1)

    # Procesa la imagen, la voltea en espejo, convierte de BGR a RGB y dibuja las marcas y conexiones
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    dedoArriba = [False, False, False, False]

    if (
        results.multi_hand_landmarks
    ):  # Si la imagen contiene más de una mano, se ejecuta para cada una
        for hand_landmarks in results.multi_hand_landmarks:
            dedoArriba = contar_dedos(hand_landmarks)
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Publicar el texto correspondiente a la cantidad de dedos levantados
    print(dedoArriba)

    dedos_nombres = ["indice", "medio", "anular", "menique"]
    dedos_topicos = ["indice", "medio", "anular", "menique"]

    for i, estado in enumerate(dedoArriba):
        client.publish(dedos_topicos[i], f"{estado}")
        print(f"Publicando en {dedos_topicos[i]}: {estado}")
    
    time.sleep(1)
    
    #Mostrar la imagen con las manos detectadas
    cv2.imshow("Cuenta dedos ESP32cam", image)
    if cv2.waitKey(15) & 0xFF == 27:  # Presiona 'ESC' para salir
        break

cv2.destroyAllWindows()
