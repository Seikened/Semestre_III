import cv2
import requests
import numpy as np

# Reemplaza <IP_CAM> con la IP de tu ESP32-CAM
url = 'http://172.20.10.2/capture'

while True:
    try:
        response = requests.get(url)
        image_array = np.array(bytearray(response.content), dtype=np.uint8)
        frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        cv2.imshow("ESP32-CAM Stream", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except Exception as e:
        print("Error:", e)
        break

cv2.destroyAllWindows()
