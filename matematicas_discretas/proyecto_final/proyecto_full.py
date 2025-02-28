import networkx as nx
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import haversine_distances
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
from collections import defaultdict
import random

# Google maps
api = "tu_api_key"
gmaps = googlemaps.Client(key=api)


# ======================================================================================================================
class Servicio:
    id = 0

    def __init__(
        self,
        id=None,
        tipo=None,
        tiempo=None,
        ubicacion=None,
        color=None,
        bloqueado=None,
        flotilla=None,
        dia=None,
    ):
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
        self.dia = dia
        self.color = color
        self.bloqueado = bloqueado
        self.flotilla = flotilla
        self.cluster_id = None
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

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))

    def load_data(self, servicios):
        dia_color_map = {
            "#a567bf": "Lunes",
            "#ec7063": "Martes",
            "#138d75": "Miércoles",
            "#2e86c1": "Jueves",
            "#515a5a": "Viernes",
            "#f39c12": "Sábado",
        }

        for data in servicios:
            color_hex = data["color"]
            color_dia = dia_color_map.get(color_hex, "Día desconocido")

            servicio = Servicio(
                id=data["id"],
                tipo=data["tipo"],
                tiempo=data["tiempo"],
                ubicacion=tuple(data["ubicacion"]),
                color=self.hex_to_rgb(color_hex),
                dia=color_dia,
                bloqueado=data["bloqueado"],
                flotilla=data["flotilla"],
            )
            self.agregar_servicio(servicio)
        print("Datos cargados con días asignados.")

        # Validar reglas del negocio antes de tratar los datos
        self.validar_reglas_de_negocio()

        # Normalizar las ubicaciones de los servicios
        self.normalizar_ubicaciones()

        # Clusterizar los servicios utilizando KMeans
        self.clusterizar()

        # Crear enlaces entre los servicios basados en la distancia geodésica
        #self.crear_enlace(k=5)

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
        # Filtrar los servicios bloqueados y no bloqueados
        bloqueados = [
            servicio for servicio in self.servicios.values() if servicio.bloqueado
        ]
        no_bloqueados = [
            servicio for servicio in self.servicios.values() if not servicio.bloqueado
        ]
        # Mapas de días y clusters
        self.dias_de_la_semana = [
            "Lunes",
            "Martes",
            "Miércoles",
            "Jueves",
            "Viernes",
            "Sábado",
        ]
        self.dia_cluster_id_map = {
            dia: idx for idx, dia in enumerate(self.dias_de_la_semana)
        }
        self.cluster_id_to_dia = {
            idx: dia for dia, idx in self.dia_cluster_id_map.items()
        }
        n_clusters_total = len(self.dias_de_la_semana)

        # Asignar colores a clusters
        colores = plt.cm.rainbow(np.linspace(0, 1, n_clusters_total))
        self.cluster_id_color_map = {
            cluster_id: tuple(colores[cluster_id][:3])
            for cluster_id in range(n_clusters_total)
        }

        # Asignar cluster_id y color a servicios bloqueados
        carga_por_dia = defaultdict(int)
        dias_ocupados = set()
        for servicio in bloqueados:
            dia = servicio.dia
            cluster_id = self.dia_cluster_id_map.get(dia)
            servicio.cluster_id = cluster_id
            servicio.color = self.cluster_id_color_map[cluster_id]
            carga_por_dia[dia] += servicio.tiempo
            dias_ocupados.add(dia)
            

        # Determinar días disponibles
        dias_disponibles = [
            dia for dia in self.dias_de_la_semana if dia not in dias_ocupados
        ]
        n_clusters = len(dias_disponibles)

        if n_clusters == 0:
            # Si todos los días están ocupados, asignamos los clusters a los días tratando de equilibrar la carga
            dias_disponibles = self.dias_de_la_semana
            n_clusters = len(dias_disponibles)

        # Clusterizar servicios no bloqueados utilizando KMeans
        if no_bloqueados:
            coords = np.array([servicio.ubicacion for servicio in no_bloqueados])
            coords_rad = np.radians(coords)

            # Aplicar KMeans
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            kmeans.fit(coords)
            labels = kmeans.labels_

            # Agrupar servicios por labels
            clusters_no_bloqueados = defaultdict(list)
            for idx, servicio in enumerate(no_bloqueados):
                label = labels[idx]
                clusters_no_bloqueados[label].append(servicio)

            # Asignar clusters a días disponibles considerando la carga de trabajo
            carga_clusters = []
            for label, servicios_cluster in clusters_no_bloqueados.items():
                carga_cluster = sum(s.tiempo for s in servicios_cluster)
                carga_clusters.append((label, carga_cluster))

            # Ordenar días por carga actual (ascendente)
            dias_ordenados = sorted(
                self.dias_de_la_semana, key=lambda dia: carga_por_dia.get(dia, 0)
            )

            # Asignar clusters a días para equilibrar la carga
            for i, (label, carga_cluster) in enumerate(
                sorted(carga_clusters, key=lambda x: x[1], reverse=True)
            ):
                dia = dias_ordenados[i % len(dias_ordenados)]
                cluster_id = self.dia_cluster_id_map[dia]
                color = self.cluster_id_color_map[cluster_id]
                carga_por_dia[dia] += carga_cluster
                for servicio in clusters_no_bloqueados[label]:
                    servicio.cluster_id = cluster_id
                    servicio.color = color
                    servicio.dia = dia
        else:
            print("No hay servicios no bloqueados para clusterizar.")

        # Crear subgrafos
        print("-" * 50)
        print("Antes de cargar los grafos van algunas estadisticas de la data:")
        print(f"Total de servicios: {len(self.servicios)}")
        print(f"Total de servicios bloqueados: {len(bloqueados)}")
        print(f"Total de servicios no bloqueados: {len(no_bloqueados)}")
        print(f"Total de días ocupados: {len(dias_ocupados)}")
        print(f"Total de días disponibles: {len(dias_disponibles)}")
        print(f"Tasa de bloqueados/no bloqueados: {len(bloqueados) / len(no_bloqueados)}")
        print(f"Tasa de no bloqueados/bloqueados: {len(no_bloqueados) / len(bloqueados)}")
        print(f"Porcentaje de bloqueados y no bloqueados: {len(bloqueados) / len(self.servicios) * 100:.2f}% / {len(no_bloqueados) / len(self.servicios) * 100:.2f}%")
        print(f"Porcentaje de días ocupados y disponibles: {len(dias_ocupados) / len(self.dias_de_la_semana) * 100:.2f}% / {len(dias_disponibles) / len(self.dias_de_la_semana) * 100:.2f}%")
        print("-" * 50)
        
        self.crear_subgrafo()
        print("Servicios clusterizados y subgrafos creados correctamente.")

    def crear_subgrafo(self):
        """Creamos un subgrafo por cada cluster_id"""
        for servicio in self.servicios.values():
            cluster_id = servicio.cluster_id
            if cluster_id not in self.subgrafos_por_dia:
                # Si no existe el subgrafo, lo creamos
                self.subgrafos_por_dia[cluster_id] = SubGrafo(
                    cluster_id, servicio.color
                )
            # Agregamos el servicio al subgrafo correspondiente
            self.subgrafos_por_dia[cluster_id].agregar_servicio(servicio)

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

    # ============================================= lógica de reglas de negocio ==================================================================

    def validar_reglas_de_negocio(self):
        self.validar_bloqueos()
        self.validar_tiempos()
        self.add_cedis()

    # ======== Validamos si un servicio esta bloqueado si es asi se tiene que armar las rutas sin optimas pero la sigerencia es no tomar estos datos forzados ya que no favorece al altgorimo

    def validar_bloqueos(self):
        """Validar que el servicio no este bloqueado y si es asi entonces no podemos modificar su color (dia de la semana) forzando a que sea un color en especifico (día de la semana)"""
        servivio = None
        self.asignar_nuevo_color(servivio)

    def asignar_nuevo_color(self, servicio):
        """Busca un nuevo color para un servicio el cual esta bloqueado a un color (día) pero el algoritmo sugiere cambiarlo de color entonces no se puede"""
        pass

    # ======== Validamos que una cantidad de servicios por color/día no superen el total de horas operativas y si es asi creamos otra cuadrilla y se la asignamos a los servicios
    def validar_tiempos(self, max_tiempo=8):
        self.validar_tiempos

    def reasignar_exceso(self, subgrafo, exceso):
        pass

    # ======== Siempre una ruta de alguna cuadrilla de algun día sale de la central la cual debemos añadir al inicio de cada cluster/color/día, es decir, hacer un ciclo y que el inicio y el fin sea CEDIS y
    def add_cedis(self):
        cedis = {
            "id": 0,
            "tipo": "CEDIS",
            "tiempo": 30,  # El tiempo de preparación del material en CEDIS
            "ubicacion": [21.107472, -101.620611],
            "color": None,
            "bloqueado": False,
            "flotilla": None,
        }
        cedis_json = json.dumps(cedis)

    # ============================================= renderización visual =========================================================================
    def vizualizar(self):
        # self.matriz_de_adyacencia()
        self.visualizar_cluster_interactivo()
        #self.visualizar_grafo_interactivo()

    def matriz_de_adyacencia(self):
        sns.heatmap(self.matriz_de_distancias, cmap="coolwarm", annot=False)
        plt.title("Matriz de distancias")
        plt.xlabel("Servicios")
        plt.ylabel("Servicios")
        plt.show()

    def visualizar_cluster_interactivo(self):
        """Visualiza los clústeres de forma interactiva con Plotly."""
        data = {
            "Latitud": [servicio.ubicacion[0] for servicio in self.servicios.values()],
            "Longitud": [servicio.ubicacion[1] for servicio in self.servicios.values()],
            "ID": [servicio.id for servicio in self.servicios.values()],
            "Tipo": [servicio.tipo for servicio in self.servicios.values()],
            "Tiempo": [servicio.tiempo for servicio in self.servicios.values()],
            "Día": [
                self.cluster_id_to_dia.get(servicio.cluster_id)
                for servicio in self.servicios.values()
            ],
            "Estado": [
                "Bloqueado" if servicio.bloqueado else "Desbloqueado"
                for servicio in self.servicios.values()
            ],
        }
        df = pd.DataFrame(data)

        fig = px.scatter(
            df,
            x="Longitud",
            y="Latitud",
            color="Día",  # Colorea por días
            symbol="Estado",  # Diferencia por bloqueados/desbloqueados
            hover_data=["ID", "Tipo", "Tiempo", "Día", "Estado"],
            title="Clusterización Interactiva por Día",
        )
        fig.update_traces(
            marker=dict(size=12, opacity=0.8, line=dict(width=1, color="DarkSlateGrey"))
        )
        fig.show()

    def visualizar_grafo_interactivo(self):
        """Visualiza el grafo de servicios de forma interactiva con Pyvis, coloreando por clúster."""
        net = Network(notebook=True, bgcolor="#ffffff", font_color="black")

        # Añadir todos los nodos al grafo con colores por clúster
        for i, servicio in enumerate(self.servicios.values()):
            # Convertir RGB a hexadecimal
            color_hex = "#%02x%02x%02x" % (
                int(servicio.color[0] * 255),
                int(servicio.color[1] * 255),
                int(servicio.color[2] * 255),
            )
            # Configurar estilos para nodos bloqueados
            if servicio.bloqueado:
                net.add_node(
                    servicio.id,
                    label=f"Bloqueado: {servicio.id}",
                    title=(
                        f"Tipo: {servicio.tipo}<br>"
                        f"Tiempo: {servicio.tiempo} horas<br>"
                        f"Ubicación: {servicio.ubicacion}<br>"
                        f"Estado: Bloqueado"
                    ),
                    color=color_hex,
                    size=50,  # Más grande
                    borderWidth=3,  # Borde más grueso
                )
            else:
                net.add_node(
                    servicio.id,
                    label=f"{servicio.id}",
                    title=(
                        f"Tipo: {servicio.tipo}<br>"
                        f"Tiempo: {servicio.tiempo} horas<br>"
                        f"Ubicación: {servicio.ubicacion}<br>"
                        f"Estado: Desbloqueado"
                    ),
                    color=color_hex,
                    size=25,  # Tamaño normal
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
    def __init__(self, cluster_id, color):
        self.cluster_id = cluster_id
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
# ========================================== Iniciamos con la configuración ============================================
# ======================================================================================================================

# Extraemos la información de el archivo.json


def loads_dataset(size):
    ruta = "/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/Mates_IA/proyecto_final/"
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
            # print(servicios)
    except FileNotFoundError:
        print("El archivo no existe.")
        servicios = []
    except json.JSONDecodeError:
        print("Error al decodificar el archivo JSON.")
        servicios = []

    return servicios


# =================

# Crear una instancia del grafo con los servicios cargados


# cantidad_servicios = [30, 60, 240, 2880]
# prefijos = ["_s", "_m", "_g", "_xl"]
# Cargar los datos de los servicios en el grafo | Para el tamaño pon "s", "m", "g" o "xl"

# Crear grafos para cada tamaño de dataset
tamanos = ["s", "m", "g", "xl"]
for tamano in tamanos:
    print(f"{"-"*50} Procesando un dataset de tamaño {tamano} {"-" * 50}")
    grafo = Grafo()
    grafo.load_data(loads_dataset(tamano))
    grafo.vizualizar()




print("RENDERIZACIÓN TERMINADA PUEDES VER LOS RESULTADOS EN LOS ARCHIVOS HTML")

# semana_chamba.mapa_con_rutas_optimas(gmaps)
