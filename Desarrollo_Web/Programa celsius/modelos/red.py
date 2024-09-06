import tensorflow as tf
import numpy as np


class ModeloCelsiusFahrenheit:
    def __init__(self):
        self.cap = tf.keras.layers.Dense(units = 1, input_shape = [1])
        self.modelo = tf.keras.Sequential([self.cap])
        self.modelo.compile(
            optimizer = tf.keras.optimizers.Adam(0.1),
            loss = 'mean_squared_error'
        )

    def entrenar(self, epochs=1000):
        celsius = np.arange(-100, 101, 1, dtype=float)  # Array de -100 a 100 grados Celsius
        fahrenheit = (celsius * 9/5) + 32  # Conversión a Fahrenheit
        self.historial = self.modelo.fit(celsius, fahrenheit, epochs = epochs, verbose = False)

    def predecir(self, celsius):
        return self.modelo.predict(np.array([[celsius]]))[0][0]

    def obtener_pesos(self):
        return self.cap.get_weights()
    



if __name__ == '__main__':
    modelo = ModeloCelsiusFahrenheit()
    modelo.entrenar()
    print(modelo.predecir(100))
    print(modelo.obtener_pesos())