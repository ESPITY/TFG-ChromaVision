# Detección de base (HoughLines)
import cv2
import numpy as np
from itertools import combinations  # Combinaciones de posibles líneas perpendiculares

from config  import MIN_BASE_AREA_RATIO

# Detecta la base
def detect_base(frame):
    frame_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Convertir el frame de BGR a escala de grises
    frame_blur  = cv2.bilateralFilter(frame_grey, 20, 30, 30) # Reducir el ruido manteniendo bordes nítidos
    ret, otsu_binary = cv2.threshold(frame_blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) # Convertir la imagen a binario

    # Morphological Operation - Opening (erosion/dilation) - Eliminar ruido
    kernel = np.ones((5, 5), np.uint8)
    otsu_binary = cv2.morphologyEx(otsu_binary, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    edges = cv2.Canny(otsu_binary, 10, 20)

    # Aumentar el grosor de los bordes
    kernel = np.ones((3, 3), np.uint8) 
    edges = cv2.dilate(edges, kernel, iterations=1)

    # HOUGH LINES (Resolución - rho: 1px, theta: 1º) (Threshold: mín nº de intersecciones para considerar una línea)
    lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=150)

    if lines is None:
        draw_base(frame, None)
        return None
    
    unique_lines = remove_line_duplicates(lines)    # Eliminar líneas duplicadas

    if len(unique_lines) < 4:   # Tras limpiar duplicados no hay 4 líneas únicas
        draw_base(frame, None)
        return None

    clusters = cluster_lines_by_angle(unique_lines)        # Agrupar líneas en dos grupos según theta

    if len(clusters) != 2:  # Tras agrupar 2 clusters no hay
        return None
    
    cluster1, cluster2 = clusters
    
    if len(cluster1) < 2 or len(cluster2) < 2:  # Alguno de los dos clusters no tiene 2 líneas
        draw_base(frame, None)
        return None

    best_rectangle = None
    max_area = 0
    # Calcular el área mínima que debe tener el rectángulo (según % que ocupa del frame)
    frame_h, frame_w = frame.shape[:2]
    min_area = frame_w * frame_h * MIN_BASE_AREA_RATIO

    # Combinaciones de líneas (2 de cada cluster): recorre todas las posibles
    for (cl1_line1, cl1_line2) in combinations(cluster1, 2):
        for (cl2_line1, cl2_line2) in combinations(cluster2, 2):
            # Comprobar perpendicularidad
            if not (are_lines_perpendicular(cl1_line1, cl2_line1) and 
                    are_lines_perpendicular(cl1_line1, cl2_line2) and 
                    are_lines_perpendicular(cl1_line2, cl2_line1) and 
                    are_lines_perpendicular(cl1_line2, cl2_line2)):
                continue

            # Esquinas
            corners = [
                get_line_intersection(cl1_line1, cl2_line1),
                get_line_intersection(cl1_line1, cl2_line2),
                get_line_intersection(cl1_line2, cl2_line1),
                get_line_intersection(cl1_line2, cl2_line2)
            ]
            
            # Comprobar que todas las esquinas existen y que están dentro del frame
            if None in corners or not all(is_point_inside_frame(c, frame) for c in corners):
                continue

            corners_sorted = sort_corners_clockwise(corners)  # Ordenar esquinas
            area = rectangle_area(corners_sorted)   # Calcular área
            
            # Quedarse con el rectángulo de mayor área
            if area > max_area and area >= min_area:
                max_area = area
                best_rectangle = {
                    'lines' : [cl1_line1, cl1_line2, cl2_line1, cl2_line2],
                    'corners' : corners_sorted,
                    'area' : area
                }

    draw_base(frame, best_rectangle)

    return best_rectangle

# Dibujar
def draw_base(frame, best_rectangle):
    if best_rectangle is None:
        cv2.putText(frame, "Base NO detectada", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return

    cv2.putText(frame, "Base detectada", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # 4. Dibujar las 4 líneas del rectángulo - Morado
    for rectangle_line in best_rectangle['lines']:
        draw_line(frame, rectangle_line, (255, 0, 170), 2)

    # 5. Dibujar el contorno del rectángulo - Naranja
    corners = best_rectangle['corners']
    corners_array = np.array(corners, dtype=np.int32)
    cv2.polylines(frame, [corners_array], True, (0, 200, 255), 3)
    
    # 6. Dibujar las esquinas y numerar - Azul/Blanco
    for i, corner in enumerate(corners):
        corner_int = (int(np.round(corner[0])), int(np.round(corner[1])))
        cv2.circle(frame, corner_int, 8, (255, 200, 0), -1)

# Eliminar duplicados, conservar las líneas superiores con más intersecciones (50 y 5º)
def remove_line_duplicates(lines, rho_tolerance=50, theta_tolerance=np.radians(10)):
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
            rho_diff = abs(rho - other_rho)
            theta_diff = abs(theta - other_theta)
            theta_diff = min(theta_diff, np.pi - theta_diff)
            
            if rho_diff < rho_tolerance and theta_diff < theta_tolerance:
                is_similar = True
                break   # Ya existe una línea similar
        
        if not is_similar:
            unique_lines.append((orig_rho, orig_theta))
            unique_norm_lines.append((rho, theta))
    
    return unique_lines

# Agrupar líneas por ángulo según theta con kmeans
def cluster_lines_by_angle(lines, k=2):
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

# Comprobar si 2 líneas son perpendiculares (margen de 5ª)
def are_lines_perpendicular(line1, line2, tolerance=np.radians(5)):
    theta1 = line1[1]
    theta2 = line2[1]
    
    theta_diff = abs(theta1 - theta2)
    theta_diff = min(theta_diff, np.pi - theta_diff)  # Normalizar [0, pi/2]
    
    perp_diff = abs(theta_diff - np.pi/2)   # Resta 90º

    return perp_diff < tolerance

# Interseción de 2 lineas
def get_line_intersection(line1, line2):
    rho1, theta1 = line1
    rho2, theta2 = line2

    A = np.array([
        [np.cos(theta1), np.sin(theta1)],
        [np.cos(theta2), np.sin(theta2)]
    ])

    b = np.array([rho1, rho2])

    try:
        x0, y0 = np.linalg.solve(A, b)
        #x0, y0 = int(np.round(x0)), int(np.round(y0))
        return (float(x0), float(y0))
    except:
        return None

# Comprobar si un punto está dentro de la imagen (esquina)
def is_point_inside_frame(point, frame):
    x, y = point
    h, w = frame.shape[:2]
    return 0 <= x < w and 0 <= y < h

# Ordenar las esquinas de la base detectada (rectángulo) - sentido horario
def sort_corners_clockwise(corners):
    points = np.array(corners, dtype="float32")

    points_sum = points.sum(axis=1)                     # Sumamos coordenadas X e Y
    top_left = points[np.argmin(points_sum)]
    bottom_right = points[np.argmax(points_sum)]

    points_diff = np.diff(points, axis=1)   
    top_right = points[np.argmin(points_diff)]
    bottom_left = points[np.argmax(points_diff)]

    return [top_left, top_right, bottom_right, bottom_left]

# Calcula el área del rectángulo
def rectangle_area(corners):
    width = np.linalg.norm(corners[1] - corners[0])
    height = np.linalg.norm(corners[3] - corners[0])
    
    return width * height

# Dibuja una línea infinita
def draw_line(frame, line, color=(0, 0, 255), thickness=1):
    rho, theta = line

    a = np.cos(theta)
    b = np.sin(theta)

    x0 = a * rho    # rho * cos(tetha)
    y0 = b * rho    # rho * sen(tetha)

    # Longitud de la línea: hipotenusa según el teorema de Pitágoras
    length = np.hypot(frame.shape[0], frame.shape[1])

    # 1000 es la longitud de la línea
    x1 = int(x0 + length * (-b))    # (r * cos(theta) - length * sin(theta))
    y1 = int(y0 + length * (a))     # (rs * in(theta) + length * cos(theta))

    x2 = int(x0 - length * (-b))    # (r * cos(theta) + length * sin(theta))
    y2 = int(y0 - length * (a))     # (r * sin(theta) - length * cos(theta))

    cv2.line(frame, (x1, y1), (x2, y2), color, thickness)