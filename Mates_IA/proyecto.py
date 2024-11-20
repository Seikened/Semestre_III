import networkx as nx
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
import numpy as np
import json
import matplotlib.cm as cm
from pathlib import Path



# Obtener la ruta del archivo JSON
ruta_archivo = Path(__file__).parent
print(ruta_archivo)
ruta = str(ruta_archivo / 'servicios_aleatorios.json')
print(ruta)
# Cargar los datos de servicios desde el archivo JSON
with open(ruta, "r") as archivo:
    servicios = json.load(archivo)

# Crear el grafo y agregar los nodos con sus atributos
grafo = nx.Graph()
for servicio in servicios:
    grafo.add_node(
        servicio['id'],
        tipo=servicio['tipo'],
        tiempo=servicio['tiempo'],
        ubicacion=servicio['ubicacion'],
        color=servicio['color'],
        bloqueado=servicio['bloqueado'],
        flotilla=servicio['flotilla']
    )

# Obtener las ubicaciones de los servicios
ubicaciones = nx.get_node_attributes(grafo, 'ubicacion')
nodos = list(grafo.nodes())
ubicaciones_array = np.array([ubicaciones[nodo] for nodo in nodos])

# Definir el número de vecinos más cercanos (k)
k = 5  # Puedes ajustar este valor según tus necesidades

# Encontrar los k vecinos más cercanos para cada punto
neigh = NearestNeighbors(n_neighbors=k+1)  # k+1 porque incluye el punto mismo
neigh.fit(ubicaciones_array)
distances, indices = neigh.kneighbors(ubicaciones_array)

# Añadir aristas al grafo basadas en los vecinos más cercanos
for idx, nodo in enumerate(nodos):
    for neighbor_idx in indices[idx][1:]:  # Omitir el primer vecino (es el mismo nodo)
        neighbor_node = nodos[neighbor_idx]
        distancia_calculada = distances[idx][list(indices[idx]).index(neighbor_idx)]
        grafo.add_edge(
            nodo,
            neighbor_node,
            peso=distancia_calculada
        )

# Agrupar los servicios utilizando KMeans
n_clusters = 6  # Ajusta este valor según tus necesidades
kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(ubicaciones_array)
labels = kmeans.labels_

# Asignar los clusters a los nodos del grafo
for idx, nodo in enumerate(nodos):
    grafo.nodes[nodo]['cluster'] = labels[idx]

# Visualización de los clusters en un scatter plot
colores = cm.rainbow(np.linspace(0, 1, n_clusters))

plt.figure(figsize=(10, 6))
for i in range(n_clusters):
    cluster_points = ubicaciones_array[labels == i]
    plt.scatter(cluster_points[:, 1], cluster_points[:, 0], color=colores[i], label=f'Cluster {i+1}')
plt.legend()
plt.xlabel('Longitud')
plt.ylabel('Latitud')
plt.title('Clustering de Servicios')
plt.show()

# Visualización del grafo con clusters
plt.figure(figsize=(12, 8))

# Crear un diccionario de posiciones para los nodos
posiciones = {nodo: (ubicaciones[nodo][1], ubicaciones[nodo][0]) for nodo in nodos}  # (longitud, latitud)

# Dibujar los nodos por cluster
for i in range(n_clusters):
    cluster_nodos = [nodo for nodo in nodos if grafo.nodes[nodo]['cluster'] == i]
    nx.draw_networkx_nodes(
        grafo,
        pos=posiciones,
        nodelist=cluster_nodos,
        node_color=[colores[i]],
        node_size=50,
        alpha=0.8,
        label=f'Cluster {i+1}'
    )

# Dibujar las aristas
nx.draw_networkx_edges(grafo, pos=posiciones, alpha=0.2, width=0.5)

plt.legend(scatterpoints=1)
plt.title('Grafo de Servicios Clusterizados')
plt.axis('off')
plt.show()
