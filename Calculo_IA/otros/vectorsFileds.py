import numpy as np
import matplotlib.pyplot as plt

# Vector field


# f(x,y) = x^2 + y^2



fx = lambda x, y: np.cos(y)
fy = lambda x, y: -x

xRange = 10
yRange = 10

separaciones = 20

x = np.linspace(-xRange, xRange, separaciones)
y = np.linspace(-yRange, yRange, separaciones)


X, Y = np.meshgrid(x, y)


angulo = np.arctan2(Y, X)
magnitud = np.sqrt(X**2 + Y**2)





# U es la componente en x que se obtiene de la funcion fx
U = fx(X,Y)

# V es la componente en y que se obtiene de la funcion fy
V = fy(X,Y) 

plt.quiver(X, Y, U, V)
plt.show()
