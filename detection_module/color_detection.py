# ChromaVision - Lucía García Bobillo
# Detección de piezas (colores y posición)
import cv2
import numpy as np

import config

# Obtiene las máscaras de cada color {color: máscara}
def get_masks(frame):
    frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)   # Convertir el frame de BGR a HSV
    masks = {}
    for name, lower, upper, _ in config.COLORS:
        # En HSV el Hue es circular. Si el rango de color cruza el límite (H_lower > H_upper)
        # se divide en dos rangos/máscaras válidas (extremos de Hue) y se combinan (suman)
        if lower[0] > upper[0]:
            lower1 = np.array([lower[0], lower[1], lower[2]])
            upper1 = np.array([179, upper[1], upper[2]])
            mask1 = cv2.inRange(frame_HSV, lower1, upper1)

            lower2 = np.array([0, lower[1], lower[2]])
            upper2 = np.array([upper[0], upper[1], upper[2]])
            mask2 = cv2.inRange(frame_HSV, lower2, upper2)

            mask = cv2.bitwise_or(mask1, mask2)
        else:
            mask = cv2.inRange(frame_HSV, lower, upper)
        masks[name] = mask

    return masks

# Detecta las piezas en cada celda de la cuadrícula
def detect_pieces_grid(frame, masks):    
    frame_h, frame_w = frame.shape[:2]
    cell_w = frame_w / config.GRID_WIDTH
    cell_h = frame_h / config.GRID_HEIGHT
    
    pieces = []
    # Recorrer cada celda por índices de celda
    for row in range(config.GRID_HEIGHT):
        for col in range(config.GRID_WIDTH):
            x1 = int(col * cell_w)
            y1 = int(row * cell_h)
            x2 = int((col + 1) * cell_w)
            y2 = int((row + 1) * cell_h)

            cell_area = (x2 - x1) * (y2 - y1)   # A = a*b
            min_pixels = int(cell_area * config.PERCENT_FILLED_CELL)
            
            best_color = None
            max_pixels = 0

            # Evaluar cada color (comprobar el área ocupada por cada color y escoger el máx)
            for name, mask in masks.items():
                roi = mask[y1:y2, x1:x2]        # Región de Interés: celda de la imagen recortada
                pixels = cv2.countNonZero(roi)  # Imagen binaria => contar píxeles blancos
                if pixels > max_pixels and pixels > min_pixels:
                    max_pixels = pixels
                    best_color = name

            if best_color:
                colorBGR = next((c[3] for c in config.COLORS if c[0] == best_color), (0, 0, 0))
                pieces.append({
                    "name": best_color,
                    "cell": (col, row),
                    "colorBGR": colorBGR
                })

    draw_pieces_grid(frame, pieces, draw_grid=config.SHOW_PIECES_GRID)

    return pieces

# Dibuja la cuadrícula (líneas moradas) y las piezas (círculo relleno del color detectado)
def draw_pieces_grid(frame, pieces, draw_grid=config.SHOW_PIECES_GRID):
    frame_h, frame_w = frame.shape[:2]
    cell_w = frame_w / config.GRID_WIDTH
    cell_h = frame_h / config.GRID_HEIGHT

    # Dibujar cuadrícula
    if draw_grid:
        for i in range(1, config.GRID_WIDTH):
            x = int(i * cell_w)
            cv2.line(frame, (x, 0), (x, frame_h), (255, 0, 170), 1)
        for i in range(1, config.GRID_HEIGHT):
            y = int(i * cell_h)
            cv2.line(frame, (0, y), (frame_w, y), (255, 0, 170), 1)

    # Dibujar piezas
    for p in pieces:
        # Centro de la celda en píxeles
        col, row = p["cell"]
        cx = int((col + 0.5) * cell_w)
        cy = int((row + 0.5) * cell_h)

        cv2.circle(frame, (cx, cy), 10, p["colorBGR"], -1)
        cv2.circle(frame, (cx, cy), 10, (0, 0, 0), 2)