import json
import random
import numpy as np

# Coordenadas aproximadas del centro de León, Guanajuato
centro_lat = 21.1291
centro_lon = -101.6737

# Radio aproximado en kilómetros para generar ubicaciones dentro de León
radio_km = 10

# Tipos de servicio y sus tiempos asociados en minutos
tipos_servicio = {
    "instalación sencilla": 120,
    "instalación avanzada": 150,
    "instalación completa": 180,
    "mantenimiento completo": 60,
    "mantenimiento sencillo": 15,
    "mantenimiento de hidro": 15,
    "entrega de mercancía mayor": 30,
    "entrega de mercancía menor": 10,
    "revisión por garantía": 30,
    "revisión por garantía de instalaciones externas": 30,
    "revisión externa": 30,
    "revisión para instalar": 20
}

colores = [
    "#a567bf",  # Morado (Lunes)
    "#ec7063",  # Rojo pastel (Martes)
    "#138d75",  # Verde oscuro (Miércoles)
    "#2e86c1",  # Azul oceano (Jueves)
    "#515a5a",  # Gris (Viernes)
    "#f39c12",  # Naranja (Sábado)
]

# Función para generar una ubicación aleatoria dentro de un radio en kilómetros
def generar_ubicacion_aleatoria(centro_lat, centro_lon, radio_km):
    radio_grados = radio_km / 111  # Aproximadamente 111 km por grado
    u = random.random()
    v = random.random()
    w = radio_grados * np.sqrt(u)
    t = 2 * np.pi * v
    x = w * np.cos(t)
    y = w * np.sin(t)
    nueva_lat = centro_lat + y
    nueva_lon = centro_lon + x / np.cos(np.radians(centro_lat))
    return nueva_lat, nueva_lon

# Función para calcular el número de flotillas dinámicamente
def calcular_flotillas(cantidad_servicios, base=30, flotillas_base=4):
    return max(1, (cantidad_servicios * flotillas_base) // base)

# Función para generar un conjunto de datos de servicios
def generar_servicios(cantidad, flotillas):
    servicios = []
    for i in range(cantidad):
        tipo = random.choice(list(tipos_servicio.keys()))
        tiempo = tipos_servicio[tipo]
        lat, lon = generar_ubicacion_aleatoria(centro_lat, centro_lon, radio_km)
        flotilla_asignada = (i % flotillas) + 1  # Asignación balanceada entre flotillas
        servicio = {
            "id": i + 1,
            "tipo": tipo,
            "tiempo": tiempo,
            "ubicacion": [lat, lon],
            "color": random.choice(colores),
            "bloqueado": random.choice([True, False]),
            "flotilla": flotilla_asignada
        }
        servicios.append(servicio)
    return servicios

# Generar conjuntos de datos
cantidad_servicios = [30, 60, 240, 2880]
prefijos = ["_s", "_m", "_g", "_xl"]

for tam, prefijo in zip(cantidad_servicios, prefijos):
    cantidad_flotillas = calcular_flotillas(tam)
    servicios = generar_servicios(tam, cantidad_flotillas)
    nombre_archivo = f"servicios{prefijo}.json"
    with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
        json.dump(servicios, archivo, indent=4, ensure_ascii=False)
    print(f"Archivo '{nombre_archivo}' generado con {tam} servicios y {cantidad_flotillas} flotillas.")