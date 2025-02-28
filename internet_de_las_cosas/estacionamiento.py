import cv2
import os
import json
import sys
import numpy as np
from skimage.metrics import structural_similarity as ssim


def cargar_imagen(ruta, escala_grises=False):
    """Carga una imagen desde una ruta específica."""
    flag = cv2.IMREAD_GRAYSCALE if escala_grises else cv2.IMREAD_COLOR
    imagen = cv2.imread(ruta, flag)
    if imagen is None:
        raise ValueError(f"No se pudo cargar la imagen desde {ruta}")
    print(f"[INFO] Imagen cargada desde {ruta}, dimensiones: {imagen.shape}")
    return imagen


def preprocesar_imagen(imagen):
    """Aplica preprocesamiento a la imagen para resaltar diferencias."""
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    desenfoque = cv2.GaussianBlur(gris, (5, 5), 0)
    print(f"[INFO] Imagen preprocesada, dimensiones: {gris.shape}, promedio de intensidad: {np.mean(gris):.2f}")
    return desenfoque


def calcular_diferencia_pixeles(roi1, roi2, umbral_pixeles=30):
    """Calcula la diferencia por píxeles entre dos regiones."""
    diff = cv2.absdiff(roi1, roi2)
    _, diff_bin = cv2.threshold(diff, umbral_pixeles, 255, cv2.THRESH_BINARY)
    porcentaje_diferencia = np.sum(diff_bin > 0) / np.prod(diff_bin.shape)
    print(f"[DEBUG] Diferencia de píxeles calculada: {porcentaje_diferencia:.2%}")
    return porcentaje_diferencia


def calcular_similitud_estructural(roi1, roi2):
    """Calcula la similitud estructural entre dos ROIs."""
    if len(roi1.shape) == 3:
        roi1 = cv2.cvtColor(roi1, cv2.COLOR_BGR2GRAY)
    if len(roi2.shape) == 3:
        roi2 = cv2.cvtColor(roi2, cv2.COLOR_BGR2GRAY)

    # Verificar si las ROIs son lo suficientemente grandes
    if roi1.shape[0] < 7 or roi1.shape[1] < 7:
        print("[WARN] ROI demasiado pequeña para SSIM, ignorando.")
        return 0  # Similitud mínima si no cumple el tamaño

    sim, _ = ssim(roi1, roi2, full=True, win_size=7)
    print(f"[DEBUG] Similitud estructural calculada: {sim:.4f}")
    return sim

def comparar_histogramas(roi1, roi2, metodo=cv2.HISTCMP_CORREL):
    """Compara los histogramas de dos imágenes y devuelve una métrica de similitud."""
    hist1 = cv2.calcHist([roi1], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([roi2], [0], None, [256], [0, 256])
    cv2.normalize(hist1, hist1)
    cv2.normalize(hist2, hist2)
    similitud = cv2.compareHist(hist1, hist2, metodo)
    print(f"[DEBUG] Similitud de histogramas: {similitud:.4f}")
    return similitud

def diferencia_acumulada(roi1, roi2, umbral=50):
    """Suma las diferencias absolutas para evaluar cambios."""
    diff = cv2.absdiff(roi1, roi2)
    total_diferencia = np.sum(diff)
    print(f"[DEBUG] Diferencia acumulada: {total_diferencia}")
    return total_diferencia

def detectar_area_ocupada(roi):
    """Detecta contornos y calcula el área ocupada dentro de una ROI."""
    _, thresh = cv2.threshold(roi, 50, 255, cv2.THRESH_BINARY)
    contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    area_total = sum(cv2.contourArea(contorno) for contorno in contornos)
    print(f"[DEBUG] Área ocupada detectada: {area_total}")
    return area_total

def calcular_gradiente_sobel(roi):
    """Calcula el gradiente utilizando el operador de Sobel."""
    grad_x = cv2.Sobel(roi, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(roi, cv2.CV_64F, 0, 1, ksize=3)
    gradiente = cv2.magnitude(grad_x, grad_y)
    total_gradiente = np.sum(gradiente)
    print(f"[DEBUG] Gradiente total: {total_gradiente}")
    return total_gradiente

def detectar_coches_hog(roi):
    """Usa un detector preentrenado basado en HOG (Histogram of Oriented Gradients)."""
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())  # Puedes usar un detector de coches preentrenado
    (rects, _) = hog.detectMultiScale(roi, winStride=(4, 4), padding=(8, 8), scale=1.05)
    print(f"[DEBUG] Coches detectados: {len(rects)}")
    return len(rects)


def crear_mascara(imagen_shape, vertices):
    """Crea una máscara binaria para un polígono definido por vértices."""
    if len(vertices) == 0:
        raise ValueError("Los vértices de la máscara están vacíos.")
    mascara = np.zeros(imagen_shape[:2], dtype=np.uint8)
    vertices = np.array(vertices, np.int32)
    cv2.fillPoly(mascara, [vertices], 255)
    porcentaje_cubierto = np.sum(mascara > 0) / np.prod(mascara.shape)
    print(f"[INFO] Máscara creada, porcentaje de área cubierta: {porcentaje_cubierto:.2%}")
    return mascara


def aplicar_mascara(imagen, mascara):
    """Aplica una máscara binaria a una imagen."""
    resultado = cv2.bitwise_and(imagen, imagen, mask=mascara)
    print(f"[INFO] Máscara aplicada, dimensiones del resultado: {resultado.shape}")
    return resultado


def guardar_coordenadas(ruta_archivo, coordenadas):
    """Guarda las coordenadas de los cajones en un archivo JSON."""
    with open(ruta_archivo, "w") as archivo:
        json.dump(coordenadas, archivo, indent=4)
    print(f"Coordenadas guardadas en {ruta_archivo}")


def cargar_coordenadas(ruta_archivo):
    """Carga las coordenadas de los cajones desde un archivo JSON."""
    if os.path.exists(ruta_archivo):
        with open(ruta_archivo, "r") as archivo:
            return json.load(archivo)
    else:
        print("No se encontraron coordenadas guardadas. Realiza el setup inicial.")
        return []


# Ruta del archivo para guardar coordenadas
archivo_coordenadas = "lugares_estacionamiento.json"

# Cargar las coordenadas guardadas o realizar setup inicial
lugares_estacionamiento = cargar_coordenadas(archivo_coordenadas)

if not lugares_estacionamiento:  # Si no hay coordenadas, ejecutar setup inicial
    print("No se encontraron coordenadas. Realiza el setup inicial.")
    imagen = cargar_imagen(
        "/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/iots/fotos/vacio_normalized.jpeg"
    )
    vertices_cajon = []

    def seleccionar_cajones(event, x, y, flags, param):
        global vertices_cajon, lugares_estacionamiento, imagen
        if event == cv2.EVENT_LBUTTONDOWN:
            vertices_cajon.append((x, y))
            cv2.circle(imagen, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow("Setup de cajones", imagen)
            if len(vertices_cajon) == 4:  # Completar cajón
                lugares_estacionamiento.append(vertices_cajon.copy())
                cv2.polylines(
                    imagen,
                    [np.array(vertices_cajon, np.int32)],
                    isClosed=True,
                    color=(255, 0, 0),
                    thickness=2,
                )
                vertices_cajon = []  # Reiniciar para el siguiente cajón

    cv2.imshow("Setup de cajones", imagen)
    cv2.setMouseCallback("Setup de cajones", seleccionar_cajones)
    cv2.waitKey(0)
    guardar_coordenadas(archivo_coordenadas, lugares_estacionamiento)
    cv2.destroyAllWindows()

# Imágenes para probar
foto_referencia = (
    "/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/iots/fotos/vacio_normalized.jpeg"
)
foto_actual = (
    "/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/iots/fotos/cinco_normalized.jpeg"
)



# Función para consolidar resultados entre métodos
def consolidar_resultados(resultados_metodo):
    """Combina resultados de todos los métodos para una predicción final."""
    votos = [sum(lugar) for lugar in zip(*resultados_metodo)]
    predicciones_finales = [1 if votos[i] > len(resultados_metodo) // 2 else 0 for i in range(len(votos))]
    return predicciones_finales

# Lista esperada de estados (0: vacío, 1: ocupado)
estado_esperado = [1, 0, 1, 1, 1, 1]  # Modifica esta lista según el caso

try:
    # Cargar imágenes
    imagen_referencia = cargar_imagen(foto_referencia, escala_grises=False)
    imagen_actual = cargar_imagen(foto_actual, escala_grises=False)

    # Preprocesar imágenes
    imagen_referencia_pre = preprocesar_imagen(imagen_referencia)
    imagen_actual_pre = preprocesar_imagen(imagen_actual)

    # Métodos disponibles
    metodos = [
        {
            "nombre": "Diferencia de píxeles",
            "funcion": calcular_diferencia_pixeles,
            "argumentos": lambda roi_referencia, roi_actual: (roi_referencia, roi_actual),
            "umbral": lambda x: x > 0.05,
        },
        {
            "nombre": "Similitud estructural (SSIM)",
            "funcion": calcular_similitud_estructural,
            "argumentos": lambda roi_referencia, roi_actual: (roi_referencia, roi_actual),
            "umbral": lambda x: x < 0.9,
        },
        {
            "nombre": "Similitud de histogramas",
            "funcion": comparar_histogramas,
            "argumentos": lambda roi_referencia, roi_actual: (roi_referencia, roi_actual),
            "umbral": lambda x: x < 0.5,
        },
        {
            "nombre": "Área ocupada",
            "funcion": detectar_area_ocupada,
            "argumentos": lambda roi_referencia, roi_actual: (roi_actual,),
            "umbral": lambda x: x > 5000,
        },
        {
            "nombre": "Gradiente Sobel",
            "funcion": calcular_gradiente_sobel,
            "argumentos": lambda roi_referencia, roi_actual: (roi_actual,),
            "umbral": lambda x: x > 1e6,
        },
    ]

    # Evaluar el estacionamiento método por método
    resultados_totales = []
    for metodo in metodos:
        print(f"\n[INFO] Evaluando todo el estacionamiento con el método: {metodo['nombre']}")

        # Crear una copia de la imagen para este método
        imagen_metodo = imagen_actual.copy()
        resultados_metodo = []

        for i, vertices in enumerate(lugares_estacionamiento, start=1):
            print(f"\n[INFO] Evaluando lugar {i} con el método {metodo['nombre']}...")

            # Crear máscara y aplicar
            mascara = crear_mascara(imagen_referencia.shape, vertices)
            roi_referencia = aplicar_mascara(imagen_referencia_pre, mascara)
            roi_actual = aplicar_mascara(imagen_actual_pre, mascara)

            # Ejecutar el método con los argumentos correctos
            argumentos = metodo["argumentos"](roi_referencia, roi_actual)
            resultado = metodo["funcion"](*argumentos)

            # Decidir estado
            estado = 1 if metodo["umbral"](resultado) else 0
            resultados_metodo.append(estado)  # Almacenar el estado (0 o 1)
            print(f"[RESULTADO] Lugar {i}: Resultado = {resultado:.4f}, Estado = {'ocupado' if estado == 1 else 'vacío'}")

            # Dibujar en la imagen
            color = (0, 255, 0) if estado == 0 else (0, 0, 255)
            cv2.polylines(
                imagen_metodo,
                [np.array(vertices, np.int32)],
                isClosed=True,
                color=color,
                thickness=2,
            )
            cv2.putText(imagen_metodo, f"Lugar {i}: {'ocupado' if estado == 1 else 'vacío'}",
                        (vertices[0][0], vertices[0][1] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

        # Mostrar el resultado visual de este método
        cv2.imshow(f"Resultado - {metodo['nombre']}", imagen_metodo)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Guardar resultados del método
        resultados_totales.append(resultados_metodo)

        # Validación de resultados
        aciertos = sum(1 for pred, esp in zip(resultados_metodo, estado_esperado) if pred == esp)
        total = len(estado_esperado)
        precision = aciertos / total
        print(f"\n[VALIDACIÓN] Método: {metodo['nombre']}")
        print(f" - Predicciones: {resultados_metodo}")
        print(f" - Estado esperado: {estado_esperado}")
        print(f" - Precisión: {precision:.2%}")

    # Consolidar resultados finales entre métodos
    predicciones_finales = consolidar_resultados(resultados_totales)
    print("\n[RESULTADO FINAL] Consolidado de todos los métodos:")
    print(f" - Predicciones finales: {predicciones_finales}")
    print(f" - Estado esperado: {estado_esperado}")

    # Calcular precisión final
    aciertos_finales = sum(1 for pred, esp in zip(predicciones_finales, estado_esperado) if pred == esp)
    precision_final = aciertos_finales / len(estado_esperado)
    print(f" - Precisión final: {precision_final:.2%}")

except Exception as e:
    print(f"Error: {e}")
    sys.exit()
