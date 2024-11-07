from pyvis.network import Network
import networkx as nx
import numpy as np

# Crear un grafo con NetworkX
G = nx.Graph()

# Lista de matemáticos con sus años de nacimiento y muerte
matematicos = [
    {"nombre": "Leonhard Euler", "nacimiento": 1707, "muerte": 1783},
    {"nombre": "Carl Friedrich Gauss", "nacimiento": 1777, "muerte": 1855},
    {"nombre": "Évariste Galois", "nacimiento": 1811, "muerte": 1832},
    {"nombre": "Joseph Fourier", "nacimiento": 1768, "muerte": 1830},
    {"nombre": "Georg Cantor", "nacimiento": 1845, "muerte": 1918},
    {"nombre": "Ada Lovelace", "nacimiento": 1815, "muerte": 1852},
    {"nombre": "George Boole", "nacimiento": 1815, "muerte": 1864},
    {"nombre": "Charles Babbage", "nacimiento": 1791, "muerte": 1871},
    {"nombre": "Augustin-Louis Cauchy", "nacimiento": 1789, "muerte": 1857},
    {"nombre": "Sophie Germain", "nacimiento": 1776, "muerte": 1831},
    {"nombre": "Pierre-Simon Laplace", "nacimiento": 1749, "muerte": 1827},
    {"nombre": "Johann Lambert", "nacimiento": 1728, "muerte": 1777}
]

# Etiquetas para los nodos
etiquetas = {
    0: 'Euler', 
    1: 'Gauss', 
    2: 'Galois', 
    3: 'Fourier', 
    4: 'Cantor', 
    5: 'Lovelace', 
    6: 'Boole', 
    7: 'Babbage', 
    8: 'Cauchy', 
    9: 'Germain', 
    10: 'Laplace', 
    11: 'Lambert'
}

# Matriz de adyacencia que representa si los matemáticos fueron contemporáneos
matriz_adyacencia = np.array([
    [0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0],
    [1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
    [0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0],
    [1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1],
    [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1],
    [1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0]
])

# Crear grafo a partir de la matriz de adyacencia
grafo_matriz = nx.from_numpy_array(matriz_adyacencia)

# Relabel nodes to have meaningful labels
nx.relabel_nodes(grafo_matriz, etiquetas, copy=False)

# Crear la red de PyVis
net = Network(height='600px', width='100%', bgcolor='#222222', font_color='white')

# Añadir nodos y aristas desde el grafo de NetworkX a la red de PyVis
net.from_nx(grafo_matriz)

# Configuraciones de físicas avanzadas
net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=200, spring_strength=0.01)

# Opciones adicionales de visualización (sin comentarios)
net.set_options("""
var options = {
  "nodes": {
    "shape": "dot",
    "scaling": {
      "min": 10,
      "max": 50,
      "label": {
        "enabled": true
      }
    }
  },
  "edges": {
    "color": {
      "inherit": true
    },
    "smooth": {
      "type": "continuous"
    }
  },
  "physics": {
    "enabled": true,
    "forceAtlas2Based": {
      "gravitationalConstant": -50,
      "centralGravity": 0.005,
      "springLength": 230,
      "springConstant": 0.18
    },
    "minVelocity": 0.75,
    "solver": "forceAtlas2Based",
    "timestep": 0.35,
    "adaptiveTimestep": true
  }
}
""")

# Mostrar el grafo interactivo
net.show("grafo_avanzado.html", notebook=False)