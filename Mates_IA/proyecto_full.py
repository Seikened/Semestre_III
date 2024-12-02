#
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
import numpy as np
import json
import matplotlib.cm as cm
from geopy.distance import geodesic
import seaborn as sns
import plotly.express as px
import pandas as pd
from pyvis.network import Network
import folium
import googlemaps

# Google maps
api = "AIzaSyAAc24cJ503tMShX7R5La2p5NAOs6luPWc"
gmaps = googlemaps.Client(key=api)

# ======================================================================================================================
class Servicio:
    id = 0
    
    
    def __init__(self, id=None, tipo=None, tiempo=None, ubicacion=None, color=None, bloqueado=None, flotilla=None):
        """
        Vecinos {
            id_vecino: distancia,
            ...
        }
        """
        self.id = id if id is not None else Servicio.id
        self.tipo = tipo
        self.tiempo = tiempo
        self.ubicacion = ubicacion  # (latitud, longitud)
        self.color = color
        self.bloqueado = bloqueado
        self.flotilla = flotilla
        self.vecinos = {}  # Vecinos locales/del mismo clúster
        Servicio.id += 1
    
    
    def agregar_vecino(self, id_vecino, distancia):
        """La distancia es el peso de la arista"""
        self.vecinos[id_vecino] = distancia
    
    def __str__(self):
        return f"Servicio {self.id} de tipo {self.tipo} con tiempo {self.tiempo} en {self.ubicacion} y color {self.color}"


class Grafo:
    
    
    def __init__(self):
        self.servicios = {}  # {id: Servicio}
        self.subgrafos_por_dia = {}  # Subgrafos: {color: SubGrafo}
        self.dias_de_la_semana = [
            "Lunes",
            "Martes",
            "Miércoles",
            "Jueves",
            "Viernes",
            "Sábado",
        ]
    
    
    def agregar_servicio(self, servicio):
        self.servicios[servicio.id] = servicio
    
    
    def load_data(self, servicios):
        for data in servicios:
            servicio = Servicio(
                id=data["id"],
                tipo=data["tipo"],
                tiempo=data["tiempo"],
                ubicacion=tuple(data["ubicacion"]),
                color=data["color"],
                bloqueado=data["bloqueado"],
                flotilla=data["flotilla"],
            )
            self.agregar_servicio(servicio)
        
        # Normalizar las ubicaciones de los servicios
        self.normalizar_ubicaciones()
        
        # Clusterizar los servicios utilizando KMeans
        self.clusterizar()
        
        # Crear enlaces entre los servicios basados en la distancia geodésica
        self.crear_enlace(k=5)
        
        print("Grafo cargado correctamente.")
    
    
    def normalizar_ubicaciones(self):
        # Normalizar las ubicaciones con geopy para las distancias y los grados
        for servicio in self.servicios.values():
            if servicio.ubicacion:
                lat, lon = servicio.ubicacion
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    servicio.ubicacion = (float(lat), float(lon))
                else:
                    raise ValueError(
                        "Las coordenadas deben estar en el rango de latitud y longitud"
                    )
        print("Ubicaciones normalizadas correctamente.")
    
    
    def clusterizar(self):
        """Clústeres de servicios con KMeans para asignar colores"""
        ubicaciones = np.array(
            [servicio.ubicacion for servicio in self.servicios.values()]
        )
        
        kmeans = KMeans(n_clusters=len(self.dias_de_la_semana), random_state=0).fit(
            ubicaciones
        )
        labels = kmeans.labels_
        
        colores = cm.rainbow(np.linspace(0, 1, len(self.dias_de_la_semana)))
        
        # Asignamos color al cluster iterando cada servicio
        for i, servicio in enumerate(self.servicios.values()):
            servicio.color = tuple(colores[labels[i]])
        
        self.crear_subgrafo()
        print("Servicios clusterizados correctamente.")
    
    
    def crear_subgrafo(self):
        """Creamos un subgrafo por cada día basado en los colores de los servicios"""
        
        for servicio in self.servicios.values():
            if servicio.color not in self.subgrafos_por_dia:
                # Si no existe el subgrafo, lo creamos
                self.subgrafos_por_dia[servicio.color] = SubGrafo(servicio.color)
            # Agregamos el servicio al subgrafo correspondiente
            self.subgrafos_por_dia[servicio.color].agregar_servicio(servicio)
    
    
    def crear_enlace(self, k=3):
        """Creamos los enlaces de cada servicio con su k vecino mas cercano y aqui utilizamos la distancia geodesica (km)"""
        servicios = list(self.servicios.values())
        numero_servicios = len(servicios)
        self.matriz_de_distancias = np.zeros((numero_servicios, numero_servicios))
        
        for i in range(numero_servicios):
            for j in range(numero_servicios):
                # No ponemos el que esta igualito a el en posicion
                if i != j:
                    self.matriz_de_distancias[i][j] = geodesic(
                        servicios[i].ubicacion, servicios[j].ubicacion
                    ).kilometers
        
        # Calculamos la cercania con los servicios mas cercanos a k vecinos
        vecinos = NearestNeighbors(n_neighbors=k + 1, metric="precomputed").fit(
            self.matriz_de_distancias
        )
        distancias, indices = vecinos.kneighbors(self.matriz_de_distancias)
        
        # Enzalamos los servicios
        # En los servicios obtenemos idx: indice del servicio, servicio: objeto servicio
        for idx, servicio in enumerate(servicios):
            # print(f"Servicio: {servicio.id}, Vecinos: {indices[idx]}")
            # En los indices obtenemos neighbor_idx: {vecino,distancia}
            for neighbor_idx in indices[idx][1:]:
                # print(f'Vecino: {servicios[neighbor_idx].id}')
                vecino = servicios[neighbor_idx]
                distancia = distancias[idx][list(indices[idx]).index(neighbor_idx)]
                # Agregamos el vecino
                self.servicios[servicio.id].agregar_vecino(vecino.id, distancia)
        
        print("Enlaces creados correctamente.")

# ============================================= renderización visual =========================================================================
    def matriz_de_adyacencia(self):
        sns.heatmap(self.matriz_de_distancias, cmap="coolwarm", annot=False)
        plt.title("Matriz de distancias")
        plt.xlabel("Servicios")
        plt.ylabel("Servicios")
        plt.show()
    
    
    def visualizar_cluster(self):
        """Visualizamos los clústeres con una gráfica más estética"""
        ubicaciones = np.array(
            [servicio.ubicacion for servicio in self.servicios.values()]
        )
        colores = [servicio.color for servicio in self.servicios.values()]
        etiquetas = [servicio.id for servicio in self.servicios.values()]
        
        plt.figure(figsize=(10, 8))  # Tamaño ajustado para mejor visualización
        scatter = plt.scatter(
            ubicaciones[:, 1],
            ubicaciones[:, 0],
            c=colores,
            s=80,
            edgecolor="black",
            alpha=0.8,
        )
        
        # Añadimos etiquetas a los puntos
        for i, etiqueta in enumerate(etiquetas):
            plt.text(
                ubicaciones[i, 1],
                ubicaciones[i, 0],
                str(etiqueta),
                fontsize=8,
                ha="right",
            )
        
        plt.xlabel("Longitud")
        plt.ylabel("Latitud")
        plt.title("Clusterización de Servicios")
        plt.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.7)
        plt.show()
    
    
    def visualizar_grafo(self):
        """Visualizamos el grafo con mejores posiciones y colores"""
        G = nx.Graph()
        for servicio in self.servicios.values():
            G.add_node(servicio.id, color=servicio.color)
            for vecino, distancia in servicio.vecinos.items():
                G.add_edge(servicio.id, vecino, weight=distancia)
        
        # Usamos las ubicaciones para el layout
        posiciones = {
            servicio.id: (servicio.ubicacion[1], servicio.ubicacion[0])
            for servicio in self.servicios.values()
        }
        
        plt.figure(figsize=(12, 10))
        
        # Nodos con colores
        nodos_colores = [tuple(servicio.color) for servicio in self.servicios.values()]
        nx.draw(
            G,
            pos=posiciones,
            with_labels=True,
            node_color=nodos_colores,
            node_size=500,
            edge_color="gray",
            alpha=0.7,
        )
        
        # Pesos de las aristas
        labels = nx.get_edge_attributes(G, "weight")
        nx.draw_networkx_edge_labels(G, pos=posiciones, edge_labels=labels, font_size=8)
        
        plt.title("Visualización del Grafo")
        plt.show()
    
    
    def visualizar_cluster_interactivo(self):
        """Visualiza los clústeres de forma interactiva con Plotly."""
        data = {
            "Latitud": [servicio.ubicacion[0] for servicio in self.servicios.values()],
            "Longitud": [servicio.ubicacion[1] for servicio in self.servicios.values()],
            "ID": [servicio.id for servicio in self.servicios.values()],
            "Tipo": [servicio.tipo for servicio in self.servicios.values()],
            "Tiempo": [servicio.tiempo for servicio in self.servicios.values()],
            "Color": [servicio.color for servicio in self.servicios.values()],
        }
        df = pd.DataFrame(data)
        
        fig = px.scatter(
            df,
            x="Longitud",
            y="Latitud",
            color="Color",
            hover_data=["ID", "Tipo", "Tiempo"],
            title="Clusterización Interactiva de Servicios",
        )
        fig.update_traces(
            marker=dict(size=12, opacity=0.8, line=dict(width=1, color="DarkSlateGrey"))
        )
        fig.show()
    
    
    def visualizar_grafo_interactivo(self):
        """Visualiza el grafo de servicios de forma interactiva con Pyvis, coloreando por clúster."""
        net = Network(notebook=True, bgcolor="#ffffff", font_color="black")
        
        # Añadir todos los nodos al grafo con colores por clúster
        for servicio in self.servicios.values():
            # Convertir el color de numpy a formato hexadecimal si es necesario
            color_hex = f"#{int(servicio.color[0] * 255):02x}{int(servicio.color[1] * 255):02x}{int(servicio.color[2] * 255):02x}"
        
            net.add_node(
                servicio.id,
                label=f"Servicio {servicio.id}",
                title=(
                    f"Tipo: {servicio.tipo}<br>"
                    f"Tiempo: {servicio.tiempo} horas<br>"
                    f"Ubicación: {servicio.ubicacion}<br>"
                ),
                color=color_hex,  # Usar el color del clúster
                x=servicio.ubicacion[1],
                y=servicio.ubicacion[0],
            )
        
        # Añadir aristas entre nodos existentes
        for servicio in self.servicios.values():
            for vecino_id, distancia in servicio.vecinos.items():
                if vecino_id in self.servicios:  # Verificar si el nodo vecino existe
                    net.add_edge(servicio.id, vecino_id, value=distancia)
                else:
                    print(
                        f"Advertencia: Nodo vecino {vecino_id} no encontrado para el nodo {servicio.id}."
                    )
        
        # Mostrar grafo interactivo en archivo HTML
        net.show("grafo_servicios.html")
    
    
    def mapa_con_rutas_optimas(self, gmaps):
        """Generar un mapa con las rutas óptimas de cada subgrafo."""
        # Crear el mapa centrado en León, Guanajuato
        mapa = folium.Map(location=[21.123619, -101.680496], zoom_start=12)
        
        # Agregar los nodos al mapa
        for servicio in self.servicios.values():
            color_hex = f"#{int(servicio.color[0] * 255):02x}{int(servicio.color[1] * 255):02x}{int(servicio.color[2] * 255):02x}"
            folium.CircleMarker(
                location=servicio.ubicacion,
                radius=7,
                color=color_hex,
                fill=True,
                fill_color=color_hex,
                fill_opacity=0.7,
                popup=folium.Popup(
                    f"""
                    <b>Servicio ID:</b> {servicio.id}<br>
                    <b>Tipo:</b> {servicio.tipo}<br>
                    <b>Tiempo estimado:</b> {servicio.tiempo}<br>
                    <b>Color (Día):</b> {servicio.color}
                    """,
                    max_width=300,
                ),
            ).add_to(mapa)
        
        # Calcular rutas óptimas para cada subgrafo y añadirlas al mapa
        for subgrafo in self.subgrafos_por_dia.values():
            subgrafo.rutas_terrestres(gmaps)
            subgrafo.visualizar_rutas_en_mapa(mapa)
        
        # Guardar el mapa en un archivo HTML
        mapa.save("mapa_rutas_optimas.html")
        print("Mapa generado: mapa_rutas_optimas.html")


#
class SubGrafo:
    def __init__(self, color):
        self.color = color
        self.servicios = {}  # {id: Servicio}
        self.rutas = []  # Ruta óptima de servicios
        self.grafo = nx.Graph()  # Grafo interno del subgrafo
    
    
    def agregar_servicio(self, servicio):
        """Añadir un servicio al subgrafo."""
        self.servicios[servicio.id] = servicio
    
    
    def construir_grafo(self):
        """Construir grafo interno con distancias geodésicas entre nodos."""
        for servicio in self.servicios.values():
            self.grafo.add_node(servicio.id, ubicacion=servicio.ubicacion)
            for vecino_id, distancia in servicio.vecinos.items():
                if vecino_id in self.servicios:
                    self.grafo.add_edge(servicio.id, vecino_id, weight=distancia)
    
    
    def calcular_ruta_optima(self):
        """Calcular el ciclo más corto que pasa por todos los nodos del subgrafo."""
        self.construir_grafo()
        # Resolver el problema TSP usando NetworkX
        ciclo_optimo = nx.approximation.traveling_salesman_problem(
            self.grafo, weight="weight", cycle=True
        )
        return ciclo_optimo  # Lista ordenada de nodos en el ciclo
    
    
    def rutas_terrestres(self, gmaps):
        """Calcula rutas terrestres entre nodos según el ciclo óptimo."""
        ciclo_optimo = self.calcular_ruta_optima()
        for i in range(len(ciclo_optimo) - 1):
            origen = self.servicios[ciclo_optimo[i]]
            destino = self.servicios[ciclo_optimo[i + 1]]
            # Solicitar ruta terrestre a Google Maps
            directions = gmaps.directions(
                origin=origen.ubicacion, destination=destino.ubicacion, mode="driving"
            )
            if directions:
                ruta = directions[0]["overview_polyline"]["points"]  # Obtener polilínea
                self.rutas.append(
                    {"origen": origen.id, "destino": destino.id, "ruta": ruta}
                )
    
    
    def visualizar_rutas_en_mapa(self, mapa):
        """Añadir las rutas calculadas al mapa de Folium."""
        color_hex = f"#{int(self.color[0] * 255):02x}{int(self.color[1] * 255):02x}{int(self.color[2] * 255):02x}"
        for ruta in self.rutas:
            # Decodificar polilínea
            puntos = googlemaps.convert.decode_polyline(ruta["ruta"])
            # Añadir línea al mapa
            folium.PolyLine(
                locations=[(p["lat"], p["lng"]) for p in puntos],
                color=color_hex,
                weight=5,
                opacity=0.7,
            ).add_to(mapa)


# ======================================================================================================================
# Extraemos la información de el archivo.json

def loads_dataset(size):
    ruta = "/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/Mates_IA/"
    match size:
        case "s":
            archino_nombre = "servicios_s.json"
        case "m":
            archino_nombre = "servicios_m.json"
        case "g":
            archino_nombre = "servicios_g.json"
        case "xl":
            archino_nombre = "servicios_xl.json"
        case _:
            archino_nombre = "servicios_s.json"
    
    full_path = ruta + archino_nombre
    
    try:
        with open(full_path, "r") as archivo:
            servicios = json.load(archivo)
            print("Archivo cargado correctamente.")
            print(servicios)
    except FileNotFoundError:
        print("El archivo no existe.")
        servicios = []
    except json.JSONDecodeError:
        print("Error al decodificar el archivo JSON.")
        servicios = []
    
    return servicios



# Crear una instancia del grafo con los servicios cargados
semana_chamba = Grafo()

# Cargar los datos de los servicios en el grafo | Para el tamaño pon "s", "m", "g" o "xl"
semana_chamba.load_data(loads_dataset("s"))

# # Visualizar los clústeres de servicios en una gráfica estática
# semana_chamba.visualizar_cluster()

# # Visualizar el grafo de servicios en una gráfica estática
# semana_chamba.visualizar_grafo()

# # Visualizar los clústeres de servicios en una gráfica interactiva
semana_chamba.visualizar_cluster_interactivo()

# # Visualizar el grafo de servicios en una gráfica interactiva
semana_chamba.visualizar_grafo_interactivo()


semana_chamba.mapa_con_rutas_optimas(gmaps)