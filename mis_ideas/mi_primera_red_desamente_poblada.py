# -*- coding: utf-8 -*-
"""mi_primera_red_desamente_poblada.ipynb"""

import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import cv2  # Librería para acceder a la cámara
from tensorflow.keras.utils import to_categorical

# Cargar el dataset MNIST
mnist = tf.keras.datasets.mnist
(x_train, y_train), (x_test, y_test) = mnist.load_data()

# Normalización del procesamiento de datos
x_train = x_train.astype('float32') / 255
x_test = x_test.astype('float32') / 255

# Remodelar los datos para que sean vectores de 784 dimensiones (28x28)
x_train = x_train.reshape(60000, 784)
x_test = x_test.reshape(10000, 784)

# Convertir las etiquetas a categorías (One-Hot Encoding)
y_train = to_categorical(y_train, num_classes=10)
y_test = to_categorical(y_test, num_classes=10)

# Construcción del modelo corregido
model = tf.keras.models.Sequential([
    tf.keras.layers.Input(shape=(784,)),  # Definir la forma de entrada explícitamente
    tf.keras.layers.Dense(128, activation='relu'),  # Añadir una capa oculta más potente
    tf.keras.layers.Dense(64, activation='relu'),   # Otra capa oculta para mejorar el rendimiento
    tf.keras.layers.Dense(10, activation='softmax') # Capa de salida para clasificación
])

model.summary()

# Compilación del modelo
model.compile(loss="categorical_crossentropy",
              optimizer="sgd",  # Se utiliza descenso del gradiente
              metrics=['accuracy'])

# Entrenamiento del modelo
model.fit(x_train, y_train, epochs=5)

# Evaluación del modelo
test_loss, test_acc = model.evaluate(x_test, y_test)

print('Test accuracy:', test_acc)
print(f'{"-"*100}')
print('Test loss:', test_loss)

# ============================================
# USAR LA CÁMARA PARA CAPTURAR UNA IMAGEN, DETECTAR EL NÚMERO Y PREDECIR
# ============================================
def capturar_y_predecir():
    cap = cv2.VideoCapture(0)  # Acceder a la cámara (0 es la cámara por defecto)

    if not cap.isOpened():
        print("No se pudo abrir la cámara. Verifica los permisos de la cámara en macOS.")
        return

    print("Presiona Espacio para capturar la imagen o ESC para salir.")
    while True:
        # Leer el cuadro de la cámara
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar la imagen, intenta de nuevo.")
            continue

        # Eliminar la línea que voltea la imagen horizontalmente
        #frame = cv2.flip(frame, 1)  # El argumento '1' indica un volteo horizontal

        # Dibujar un cuadro de guía para que centres el número
        guide_x, guide_y, guide_w, guide_h = 100, 100, 300, 300
        cv2.rectangle(frame, (guide_x, guide_y), (guide_x + guide_w, guide_y + guide_h), (255, 0, 0), 2)

        # Mostrar el cuadro en una ventana
        cv2.imshow('Presiona Espacio para Capturar la Imagen', frame)

        # Esperar por la tecla 'Espacio' o 'ESC'
        key = cv2.waitKey(1) & 0xFF
        if key == 32:  # Espacio para capturar la imagen
            break
        elif key == 27:  # ESC para salir
            cap.release()
            cv2.destroyAllWindows()
            return

    # Procesar la imagen capturada y recortar dentro del cuadro guía
    cropped = frame[guide_y:guide_y + guide_h, guide_x:guide_x + guide_w]
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)  # Convertir a escala de grises

    # Usar binarización adaptativa en lugar de un umbral fijo
    thresholded = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY_INV, 11, 2)

    # Invertir los colores para que el fondo sea negro y el número sea blanco
    inverted = cv2.bitwise_not(thresholded)

    # Encontrar los contornos
    contours, _ = cv2.findContours(inverted, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        print("No se detectó ningún número. Intenta de nuevo.")
        cap.release()
        cv2.destroyAllWindows()
        return

    # Seleccionar el contorno más grande, que debería ser el número
    contour = max(contours, key=cv2.contourArea)

    # Obtener el rectángulo delimitador del contorno
    x, y, w, h = cv2.boundingRect(contour)

    # Dibujar el rectángulo en la imagen recortada para tener feedback visual
    cv2.rectangle(cropped, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Mostrar la imagen con el rectángulo en una ventana
    cv2.imshow('Área Detectada', cropped)
    cv2.waitKey(0)  # Esperar a que el usuario cierre la ventana

    # Cortar la imagen utilizando el rectángulo delimitador y agregar un margen
    margin = 20  # Margen más amplio para asegurar mejor centrado
    x_start, y_start = max(x - margin, 0), max(y - margin, 0)
    x_end, y_end = min(x + w + margin, inverted.shape[1]), min(y + h + margin, inverted.shape[0])
    cropped_number = inverted[y_start:y_end, x_start:x_end]

    # Cambiar el tamaño de la imagen a 28x28
    resized = cv2.resize(cropped_number, (28, 28), interpolation=cv2.INTER_AREA)

    # Aumentar el contraste (opcional)
    resized = cv2.normalize(resized, None, 0, 255, cv2.NORM_MINMAX)

    # Mostrar la imagen procesada
    plt.imshow(resized, cmap='gray')
    plt.title("Imagen Capturada (Procesada)")
    plt.show()

    # Normalizar y remodelar la imagen para el modelo
    imagen = resized.astype('float32') / 255
    imagen = imagen.reshape(1, 784)

    # Realizar la predicción
    prediccion = model.predict(imagen)
    clase_predicha = np.argmax(prediccion)

    # Mostrar la predicción
    print(f'🔮 Predicción del modelo: {clase_predicha}')
    print(f'📊 Probabilidades para cada clase (0 al 9):')
    for i, prob in enumerate(prediccion[0]):
        print(f'   Clase {i}: {prob * 100:.2f}%')

    # Liberar la cámara y cerrar todas las ventanas
    cap.release()
    cv2.destroyAllWindows()

# Ejecutar la función para capturar y predecir
capturar_y_predecir()
