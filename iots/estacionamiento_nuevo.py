import cv2
import sys
import numpy as np

# Rutas de imágenes
url_base = "/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/iots/fotos/"

# Fotos de prueba
vacio = url_base + "vacio_normalized.jpeg"
tres = url_base + "tres_normalized.jpeg"

# Imagen de referencia (estacionamiento vacío)
foto_referencia = vacio
# Imagen actual para analizar
foto_actual = tres

# Coordenadas de las ROIs (modifica según tus cajones)
ancho = 700
alto = 300
lugares_estacionamiento = [
    (24, 352, ancho, alto),  # Cajón 1
    (39, 876, ancho, alto),  # Cajón 2
    (34, 1388, ancho, alto),  # Cajón 3
    (1047, 375, ancho, alto),  # Cajón 4
    (1030, 896, ancho, alto),  # Cajón 5
    (1041, 1376, ancho, alto)  # Cajón 6
]

# Estados esperados (1 = Ocupado, 0 = Disponible)
estados_esperados = [1, 0, 1, 1, 0, 0]

# Parámetros ajustables
umbral_diferencia_pixeles = 60  # Diferencia mínima en pixeles para ser significativa
umbral_porcentaje_ocupado = 18  # Porcentaje mínimo para considerar un lugar como ocupado

# Cargar imágenes
imagen_referencia = cv2.imread(foto_referencia, cv2.IMREAD_GRAYSCALE)
imagen_actual_color = cv2.imread(foto_actual, cv2.IMREAD_COLOR)  # En color para superponer resultados
imagen_actual = cv2.cvtColor(imagen_actual_color, cv2.COLOR_BGR2GRAY)

if imagen_referencia is None or imagen_actual is None:
    print("Error: No se cargaron las imágenes.")
    sys.exit()

# Validar que las imágenes tengan el mismo tamaño
if imagen_referencia.shape != imagen_actual.shape:
    print("Error: Las imágenes no tienen el mismo tamaño.")
    sys.exit()

# Mostrar información inicial
print(f"[INFO] Dimensiones de la imagen: {imagen_referencia.shape}")

# Variables para la validación
predicciones = []

# Evaluar cada región de interés
for i, (x, y, w, h) in enumerate(lugares_estacionamiento, start=1):
    print(f"\n[INFO] Evaluando lugar {i} en ROI: x={x}, y={y}, ancho={w}, alto={h}")

    # Extraer las ROIs de ambas imágenes
    roi_referencia = imagen_referencia[y:y+h, x:x+w]
    roi_actual = imagen_actual[y:y+h, x:x+w]

    # Calcular diferencia absoluta entre las ROIs
    diferencia = cv2.absdiff(roi_referencia, roi_actual)

    # Aplicar umbral para destacar diferencias significativas
    _, diferencia_binaria = cv2.threshold(diferencia, umbral_diferencia_pixeles, 255, cv2.THRESH_BINARY)

    # Calcular áreas de píxeles blancos y negros
    pixeles_blancos = cv2.countNonZero(diferencia_binaria)
    area_total = w * h
    porcentaje_pixeles_blancos = (pixeles_blancos / area_total) * 100

    # Determinar estado del lugar
    estado_actual = 1 if porcentaje_pixeles_blancos > umbral_porcentaje_ocupado else 0
    predicciones.append(estado_actual)

    # Mostrar resultados en consola
    estado_texto = "Ocupado🔴" if estado_actual == 1 else "Disponible🟢"
    print(f"[RESULTADO] Lugar {i}:")
    print(f"  Píxeles blancos: {pixeles_blancos} ({porcentaje_pixeles_blancos:.2f}%)")
    print(f"  Estado: {estado_texto}")

    # Dibujar resultados en la imagen
    color = (0, 0, 255) if estado_actual == 1 else (0, 255, 0)
    cv2.rectangle(imagen_actual_color, (x, y), (x+w, y+h), color, 2)
    cv2.putText(imagen_actual_color, f"Lugar {i}: {estado_texto}",
                (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

# Mostrar la imagen final
cv2.imshow("Estado del Estacionamiento", imagen_actual_color)

# Validar predicciones
print("\n[VALIDACIÓN]")
correctas = 0
for i, (pred, esperado) in enumerate(zip(predicciones, estados_esperados), start=1):
    if pred == esperado:
        print(f"Lugar {i}: Correcto ✅ (Esperado: {esperado}, Predicho: {pred})")
        correctas += 1
    else:
        print(f"Lugar {i}: Incorrecto ❌ (Esperado: {esperado}, Predicho: {pred})")

# Calcular métricas de validación
total = len(estados_esperados)
precision = correctas / total * 100
print(f"\n[RESULTADO FINAL] Precisión: {precision:.2f}% ({correctas}/{total} lugares correctos)")

cv2.waitKey(0)
cv2.destroyAllWindows()
