import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, Function, Eq, dsolve, Derivative
from sympy.utilities.lambdify import lambdify
from scipy.optimize import curve_fit
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


class ProcesadorDatos:
    def __init__(self, ruta_datos):
        self.ruta_datos = ruta_datos
        self.x_datos = None
        self.y_datos = None
        self.x_norm = None
        self.y_norm = None
        self.x_min = None
        self.x_max = None
        self.y_min = None
        self.y_max = None
        self.cargar_datos()
        self.normalizar_datos()

    def cargar_datos(self):
        with open(self.ruta_datos, 'r') as archivo:
            datos = archivo.read()
        puntos = [list(map(float, linea.split())) for linea in datos.strip().split('\n')]
        self.x_datos, self.y_datos = zip(*puntos)
        self.x_datos = np.array(self.x_datos)
        self.y_datos = np.array(self.y_datos)

    def normalizar_datos(self):
        self.x_min, self.x_max = self.x_datos.min(), self.x_datos.max()
        self.y_min, self.y_max = self.y_datos.min(), self.y_datos.max()
        self.x_norm = (self.x_datos - self.x_min) / (self.x_max - self.x_min)
        self.y_norm = (self.y_datos - self.y_min) / (self.y_max - self.y_min)


class SolucionadorEcuacion:
    def __init__(self, procesador_datos):
        self.x = symbols('x')
        self.y = Function('y')(self.x)
        self.procesador = procesador_datos
        self.ecuacion = None
        self.solucion = None
        self.parametros = None
        self.y_ajustada = None

    def definir_ecuacion(self):
        self.ecuacion = Eq(Derivative(self.y, self.x, self.x) + 4 * Derivative(self.y, self.x) + 4 * self.y, 4 * self.x**2 - 8 * self.x)

    def resolver_ecuacion(self):
        self.solucion = dsolve(self.ecuacion)
        print("Solución general:")
        print(self.solucion)

        y_sol = lambdify([self.x, symbols('C1'), symbols('C2')], self.solucion.rhs)

        def modelo(x, C1, C2):
            return y_sol(x, C1, C2)

        self.parametros, _ = curve_fit(
            lambda x_vals, C1, C2: [modelo(xi, C1, C2) for xi in x_vals],
            self.procesador.x_datos, self.procesador.y_datos
        )
        print(f"Constantes ajustadas: C1 = {self.parametros[0]}, C2 = {self.parametros[1]}")

        self.y_ajustada = [modelo(xi, *self.parametros) for xi in self.procesador.x_datos]


class EntrenadorRedNeuronal:
    def __init__(self, procesador_datos):
        self.procesador = procesador_datos
        self.x_tensor = torch.tensor(self.procesador.x_norm, dtype=torch.float32).view(-1, 1)
        self.y_tensor = torch.tensor(self.procesador.y_norm, dtype=torch.float32).view(-1, 1)
        self.dataset = TensorDataset(self.x_tensor, self.y_tensor)
        self.train_loader = DataLoader(self.dataset, batch_size=16, shuffle=True)
        self.modelo = None
        self.criterion = nn.MSELoss()
        self.optimizer = None
        self.y_pred = None

    def crear_modelo(self):
        class RedNeuronal(nn.Module):
            def __init__(self):
                super(RedNeuronal, self).__init__()
                self.fc1 = nn.Linear(1, 64)
                self.fc2 = nn.Linear(64, 64)
                self.fc3 = nn.Linear(64, 1)
                self.relu = nn.ReLU()

            def forward(self, x):
                x = self.relu(self.fc1(x))
                x = self.relu(self.fc2(x))
                x = self.fc3(x)
                return x

        self.modelo = RedNeuronal()
        self.optimizer = torch.optim.Adam(self.modelo.parameters(), lr=0.01)

    def entrenar(self, epocas):
        for epoca in range(epocas):
            for batch_x, batch_y in self.train_loader:
                salidas = self.modelo(batch_x)
                perdida = self.criterion(salidas, batch_y)
                self.optimizer.zero_grad()
                perdida.backward()
                self.optimizer.step()
            print(f"Epoca {epoca+1}/{epocas}, Pérdida: {perdida.item():.4f}")

        # Generar predicciones al final
        x_test = torch.linspace(0, 1, len(self.procesador.x_datos)).view(-1, 1)
        self.y_pred = self.modelo(x_test).detach().numpy()

    def visualizar_resultados(self, y_ajustada):
        x_test_desnorm = self.desnormalizar_x(torch.linspace(0, 1, len(self.procesador.x_datos)))
        y_pred_desnorm = self.desnormalizar_y(self.y_pred)

        fig, axs = plt.subplots(2, 2, figsize=(15, 10))

        # Gráfica 1: Datos Originales
        axs[0, 0].scatter(self.procesador.x_datos, self.procesador.y_datos, color='blue', label='Datos Originales')
        axs[0, 0].set_title("Datos Originales")
        axs[0, 0].legend()
        axs[0, 0].grid()

        # Gráfica 2: Solución Analítica Ajustada
        axs[0, 1].plot(self.procesador.x_datos, y_ajustada, color='red', label='Solución Analítica')
        axs[0, 1].set_title("Solución Analítica Ajustada")
        axs[0, 1].legend()
        axs[0, 1].grid()

        # Gráfica 3: Predicciones de la Red Neuronal
        axs[1, 0].plot(x_test_desnorm, y_pred_desnorm, color='green', label='Red Neuronal')
        axs[1, 0].set_title("Predicciones de la Red Neuronal")
        axs[1, 0].legend()
        axs[1, 0].grid()

        # Gráfica 4: Comparación General
        axs[1, 1].scatter(self.procesador.x_datos, self.procesador.y_datos, color='blue', label='Datos Originales')
        axs[1, 1].plot(self.procesador.x_datos, y_ajustada, color='red', label='Solución Analítica')
        axs[1, 1].plot(x_test_desnorm, y_pred_desnorm, color='green', label='Red Neuronal')
        axs[1, 1].set_title("Comparación General")
        axs[1, 1].legend()
        axs[1, 1].grid()

        plt.tight_layout()
        plt.show()

    def desnormalizar_x(self, x_tensor):
        return x_tensor.numpy().flatten() * (self.procesador.x_max - self.procesador.x_min) + self.procesador.x_min

    def desnormalizar_y(self, y_pred):
        return y_pred.flatten() * (self.procesador.y_max - self.procesador.y_min) + self.procesador.y_min


# ====================== EJECUCIÓN ======================
ruta = "/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/Calculo_IA/proyecto_final/data.txt"
procesador = ProcesadorDatos(ruta)

# Resolver ecuación diferencial
solver = SolucionadorEcuacion(procesador)
solver.definir_ecuacion()
solver.resolver_ecuacion()

# Entrenar red neuronal y graficar resultados
trainer = EntrenadorRedNeuronal(procesador)
trainer.crear_modelo()
trainer.entrenar(epocas=100)
trainer.visualizar_resultados(solver.y_ajustada)