import numpy as np
from math import exp
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.metrics import mean_squared_error

class ClaseEDO:
    def __init__(self):
        # Modelo de TensorFlow con una capa oculta
        inputs = tf.keras.Input(shape=(1,))
        hidden = tf.keras.layers.Dense(units=10, activation='relu')(inputs)  # Capa oculta
        outputs = tf.keras.layers.Dense(units=1)(hidden)
        self.modelo = tf.keras.Model(inputs=inputs, outputs=outputs)
        
        # Compilación del modelo
        self.modelo.compile(
            optimizer=tf.keras.optimizers.Adam(0.1),
            loss='mean_squared_error'
        )
    
    def f(self, t, y):
        return -2* t *y
    
    def euler(self, t0, y0, h, n):
        t = np.zeros(n+1)
        y = np.zeros(n+1)
        t[0], y[0] = t0, y0
        for k in range(n):
            y[k+1] = y[k] + h * self.f(t[k], y[k])
            t[k+1] = t[k] + h
        return t, y
    
    def eulermod(self, t0, y0, h, n):
        t = np.zeros(n+1)
        y = np.zeros(n+1)
        t[0], y[0] = t0, y0
        for k in range(n):
            y0 = y[k] + h * self.f(t[k], y[k])
            y[k+1] = y[k] + (h / 2) * (self.f(t[k], y[k]) + self.f(t[k] + h, y0))
            t[k+1] = t[k] + h
        return t, y
    
    def runge_kutta(self, t0, y0, h, n):
        t = np.zeros(n+1)
        y = np.zeros(n+1)
        t[0], y[0] = t0, y0
        for k in range(n):
            k1 = self.f(t[k], y[k])
            k2 = self.f(t[k] + h / 2, y[k] + (h / 2) * k1)
            k3 = self.f(t[k] + h / 2, y[k] + (h / 2) * k2)
            k4 = self.f(t[k] + h, y[k] + h * k3)
            y[k+1] = y[k] + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
            t[k+1] = t[k] + h
        return t, y
    
    def entrenar(self, epochs=1000, edoType="runge_kutta"):
        print(f"Entrenando modelo con el método {edoType}")
        if edoType == "euler":
            t, y = self.euler(0, 1, 0.01, 100)
        elif edoType == "eulermod":
            t, y = self.eulermod(0, 1, 0.01, 100)
        elif edoType == "runge_kutta":
            t, y = self.runge_kutta(0, 1, 0.01, 100)
        else:
            print("Método no válido")
            return
        
        # Normalización de los datos
        t = (t - t.mean()) / t.std()
        y = (y - y.mean()) / y.std()
        
        # Entrenamiento del modelo
        self.historial = self.modelo.fit(t, y, epochs=epochs, verbose=False)
        print("Modelo entrenado con éxito")
    
    def predecir(self, t):
        return self.modelo.predict(np.array([[t]]))[0][0]

# Crear instancia de la clase EDO
edo = ClaseEDO()

# Entrenar el modelo con el método de Runge-Kutta
edo.entrenar(epochs=2000, edoType="runge_kutta")

# Predicción para t=0.5
t_valor = 0
t_vals, y_num = edo.runge_kutta(0, 1, 0.01, 100)  # Generar la solución numérica con Runge-Kutta

# Normalizar t_valor antes de predecir
t_valor_normalizado = (t_valor - t_vals.mean()) / t_vals.std()
prediccion = edo.predecir(t_valor_normalizado)
prediccion_sin_normalizar = edo.predecir(t_valor)
# Denormalización para comparar resultados
prediccion_denormalizada = prediccion * y_num.std() + y_num.mean()

print(f"Predicción numérica para t={t_valor}: {y_num[int(t_valor/0.01)]}")
print(f"Predicción del modelo para t={t_valor}: {prediccion_denormalizada}")
print(f"Predicción del modelo para t={t_valor} sin normalizar: {prediccion_sin_normalizar}")

# Asegurarse de que y_pred tenga el mismo tamaño que y_num
y_pred = [edo.predecir((ti - t_vals.mean()) / t_vals.std()) * y_num.std() + y_num.mean() for ti in t_vals]  # Usar t_vals en lugar de np.linspace

# Calcular y mostrar MSE
mse = mean_squared_error(y_num, y_pred)
print(f"MSE entre la solución numérica y el modelo: {mse}")

# Graficar resultados
plt.plot(t_vals, y_num, label='Solución numérica')
plt.plot(t_vals, y_pred, label='Predicción del modelo', linestyle='dashed')
plt.xlabel('t')
plt.ylabel('y')
plt.title('Comparación entre la solución numérica y la predicción del modelo')
plt.legend()
plt.show()
