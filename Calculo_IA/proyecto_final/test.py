import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, Function, Eq, dsolve
from scipy.optimize import curve_fit
from sympy.utilities.lambdify import lambdify
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

# ======================
# 1. Cargar y visualizar los datos
# ======================
# Dataset proporcionado

ruta = "/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/Calculo_IA/proyecto_final/data.txt"

with open(ruta, 'r') as file:
    data = file.read()

# Procesar los datos
points = [list(map(float, line.split())) for line in data.strip().split('\n')]
x_data, y_data = zip(*points)

# Normalizar datos
x_data = np.array(x_data)
y_data = np.array(y_data)
x_min, x_max = x_data.min(), x_data.max()
y_min, y_max = y_data.min(), y_data.max()

x_norm = (x_data - x_min) / (x_max - x_min)
y_norm = (y_data - y_min) / (y_max - y_min)

# Graficar
plt.figure(figsize=(10, 6))
plt.scatter(x_data, y_data, color='blue', label='Datos')
plt.title("Datos del dataset")
plt.xlabel("x")
plt.ylabel("y")
plt.legend()
plt.grid(True)
plt.show()

# ======================
# 2. Resolver la ecuación diferencial
# ======================
# Variables simbólicas
x = symbols('x')
y = Function('y')

# Ecuación diferencial
eq = Eq(y(x).diff(x, x) + 4 * y(x).diff(x) + 4 * y(x), 4 * x**2 - 8 * x)

# Solución general
sol = dsolve(eq)
print("Solución general:")
print(sol)

# ======================
# 3. Ajustar constantes de integración
# ======================
# Convertir la solución simbólica en función evaluable
y_sol = sol.rhs
C1, C2 = symbols('C1 C2')
f = lambdify([x, C1, C2], y_sol)

# Modelo ajustable con constantes
def model(x, C1, C2):
    return f(x, C1, C2)

# Ajustar constantes C1 y C2
params, _ = curve_fit(lambda x_vals, C1, C2: [model(xi, C1, C2) for xi in x_vals], 
                      x_data, y_data)
C1_opt, C2_opt = params
print(f"Constantes ajustadas: C1 = {C1_opt}, C2 = {C2_opt}")

# Graficar solución ajustada
y_adjusted = [model(xi, C1_opt, C2_opt) for xi in x_data]
plt.figure(figsize=(10, 6))
plt.scatter(x_data, y_data, label='Datos', color='blue')
plt.plot(x_data, y_adjusted, label='Solución ajustada', color='red')
plt.title("Ajuste de la solución analítica")
plt.xlabel("x")
plt.ylabel("y")
plt.legend()
plt.grid(True)
plt.show()

# ======================
# 4. Entrenar la red neuronal
# ======================
# Crear tensores normalizados
x_tensor = torch.tensor(x_norm, dtype=torch.float32).view(-1, 1)
y_tensor = torch.tensor(y_norm, dtype=torch.float32).view(-1, 1)
dataset = TensorDataset(x_tensor, y_tensor)
train_loader = DataLoader(dataset, batch_size=16, shuffle=True)

# Definir red neuronal
class NeuralNet(nn.Module):
    def __init__(self):
        super(NeuralNet, self).__init__()
        self.fc1 = nn.Linear(1, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, 1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# Inicializar modelo, pérdida y optimizador
model = NeuralNet()
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

# Entrenamiento
epochs = 100
for epoch in range(epochs):
    for batch_x, batch_y in train_loader:
        # Forward pass
        outputs = model(batch_x)
        loss = criterion(outputs, batch_y)

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}")

# Graficar predicciones
x_test = torch.linspace(0, 1, 100).view(-1, 1)  # Normalizado
y_pred = model(x_test).detach().numpy()
y_pred_desnorm = y_pred * (y_max - y_min) + y_min  # Desnormalizar

plt.figure(figsize=(10, 6))
plt.scatter(x_data, y_data, label='Datos Originales', color='blue')
plt.plot(x_data, y_adjusted, label='Solución Analítica', color='red')
plt.plot(x_test.numpy() * (x_max - x_min) + x_min, y_pred_desnorm, label='Red Neuronal', color='green')
plt.title("Comparación de Modelos")
plt.xlabel("x")
plt.ylabel("y")
plt.legend()
plt.grid(True)
plt.show()
