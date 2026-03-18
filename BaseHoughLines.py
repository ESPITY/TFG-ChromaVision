# Detección de base (HoughLines)
import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2
import numpy as np

# Detecta la base
def detect_base(frame, frame_grey):
    frame_blur  = cv2.bilateralFilter(frame_grey, 20, 30, 30) # Reducir el ruido manteniendo bordes nítidos
    cv2.imshow("Blur", frame_blur)

    ret, otsu_binary = cv2.threshold(frame_blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) # Convertir la imagen a binario
    cv2.imshow("OTSU Binary", otsu_binary)
    edges = cv2.Canny(otsu_binary, 10, 20)
    cv2.imshow("Edges", edges)

    # Aumentar el grosor de los bordes
    kernel = np.ones((3, 3), np.uint8) 
    edges = cv2.dilate(edges, kernel, iterations=1)
    cv2.imshow("Edges", edges)

    # HOUGH LINES (Resolución - rho: 1px, theta: 1º) (Threshold: mín nº de intersecciones para considerar una línea)
    lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=150)

    if lines is not None:
        unique_lines = hough_lines_duplicates(lines)    # Eliminar líneas duplicadas
        clusters = segmented_lines(unique_lines)        # Agrupar líneas en dos grupos según theta

        print(f"Líneas detectadas: {len(lines)}")   # Array de r y theta
        print(f"Líneas unicas: {len(unique_lines)}")   # Array de r y theta

        if len(unique_lines) < 4:
            print("Insuficientes líneas únicas")
            return None

        #for line in lines:  # (N, rho, theta)
            #rho, theta = line[0]

        #for rho, theta in unique_lines:

        cluster_colors = color_cluster_lines(clusters)
        for cluster_color, cluster in zip(cluster_colors, clusters):
            for rho, theta in cluster:
                a = np.cos(theta)
                b = np.sin(theta)

                x0 = a * rho    # rho * cos(tetha)
                y0 = b * rho    # rho * sen(tetha)

                # 1000 es la longitud de la línea
                x1 = int(x0 + 10000 * (-b))    # (r * cos(theta) - 1000 * sin(theta))
                y1 = int(y0 + 10000 * (a))     # (rs * in(theta) + 1000 * cos(theta))

                x2 = int(x0 - 10000 * (-b))    # (r * cos(theta) + 1000 * sin(theta))
                y2 = int(y0 - 10000 * (a))     # (r * sin(theta) - 1000 * cos(theta))

                cv2.line(frame, (x1, y1), (x2, y2), cluster_color, 2)

# Eliminar duplicados, conservar las líneas superiores con más intersecciones (50 y 5º)
def hough_lines_duplicates(lines, umbral_rho=50, umbral_theta=np.pi/36):
    unique_lines = []
    unique_norm_lines = []  # líneas únicas normalizadas para comparar

    for line in lines:
        rho, theta = line[0]

        orig_rho, orig_theta = rho, theta
        
        # Normalizar: rho >= 0, theta [0, π)
        if rho < 0:
            rho = -rho
            theta = theta - np.pi
        theta = theta % np.pi

        is_similar = False
        
        # Buscar si hay una línea similar ya guardada
        for other_rho, other_theta in unique_norm_lines:
            diff_rho = abs(rho - other_rho)
            diff_theta = abs(theta - other_theta)
            diff_theta = min(diff_theta, np.pi - diff_theta)
            
            if diff_rho < umbral_rho and diff_theta < umbral_theta:
                is_similar = True
                break   # Ya existe una línea similar
        
        if not is_similar:
            unique_lines.append((orig_rho, orig_theta))
            unique_norm_lines.append((rho, theta))
    
    return unique_lines

# Agrupar líneas por ángulo según theta con kmeans
def segmented_lines(lines, k=2):
    # Ángulos [0, pi]
    angles = np.array([theta for rho, theta in lines])
    # Coordenadas del ángulo (multiplicado por 2)
    pts = np.float32([[np.cos(2*theta), np.sin(2*theta)] for theta in angles])

    # Criteria: type of termination criteria, max_iter, epsilon (required accuracy)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    flags = cv2.KMEANS_RANDOM_CENTERS   # Obtención de centros iniciales
    attempts = 10
    compactness, labels, centers = cv2.kmeans(pts, k, None, criteria, attempts,flags)

    labels = labels.flatten()   # Array
    clusters = [[] for _ in range(k)]   # [[], []]
    # zip para recorrer dos listas a la vez y agrupar valores de cada una
    for label, line in zip(labels, lines):
        clusters[label].append(line)

    return clusters

# Asignar color a cada cluster según theta (V = rojo | H = verde)
def color_cluster_lines(clusters):
    cluster_colors = []

    for cluster in clusters:
        # Comprobar cuantas lineas de cada grupo son verticales u horizontales
        vertical_count = 0
        horizontal_count = 0

        for rho, theta in cluster:
            if abs(np.sin(theta)) < 1e-6:  # Menor que 0 (evitar división por 0)
                vertical_count += 1
            else:
                m = -np.cos(theta) / np.sin(theta)
                if abs(m) > 1:
                    vertical_count += 1
                else:
                    horizontal_count += 1

        if vertical_count > horizontal_count:
            cluster_colors.append((0, 0, 255))
        elif horizontal_count > vertical_count:
            cluster_colors.append((0, 255, 0))
        else:
            cluster_colors.append((0, 255, 255))
            
    return cluster_colors


stream =  cv2.VideoCapture(0)

stream.set(cv2.CAP_PROP_FPS , 30.0)
stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

while (True):
    success, frame = stream.read()

    frame_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Convertir el frame de BGR a escala de grises
    detect_base(frame, frame_grey)
    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) == ord('q'):
        break

stream.release()
cv2.destroyAllWindows()