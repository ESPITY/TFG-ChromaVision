# Detección de color

import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2
import numpy as np

from config import COLORS, GRID_WIDTH, GRID_HEIGHT, PERCENT_FILLED_CELL, BASE_WIDTH_CM, BASE_HEIGHT_CM   #, IMG_SCALE

# Obtiene las máscaras de cada color {color: máscara}
def get_masks(frame):
    frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # Convertir el frame de BGR a HSV
    masks = {}
    for name, lower, upper, _ in COLORS:
        mask = cv2.inRange(frame_HSV, lower, upper)
        masks[name] = mask

        #mask = cv2.resize(mask, None, fx=IMG_SCALE, fy=IMG_SCALE, interpolation=cv2.INTER_LINEAR)
        #cv2.imshow("Mask " + name, mask)
    return masks

# Detecta las piezas en cada celda de la cuadrícula
def detect_pieces_grid(frame, masks, cm_px, debug=False):    
    frame_h, frame_w = frame.shape[:2]
    cell_w = frame_w / GRID_WIDTH
    cell_h = frame_h / GRID_HEIGHT
    
    pieces = []

    # Recorrer cada celda por índices (no coordenadas de píxeles)
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            x1 = int(col * cell_w)
            y1 = int(row * cell_h)
            x2 = int((col + 1) * cell_w)
            y2 = int((row + 1) * cell_h)

            cell_area = (x2 - x1) * (y2 - y1)   # A = a*b
            min_pixels = int(cell_area * PERCENT_FILLED_CELL)
            
            best_color = None
            max_pixels = 0
            # Evaluar cada color
            for name, mask in masks.items():
                roi = mask[y1:y2, x1:x2]    # Región de Interés: celda de la imagen recortada
                pixels = cv2.countNonZero(roi)  # Imagen binaria => contar píxeles blancos
                if pixels > max_pixels and pixels > min_pixels:
                    max_pixels = pixels
                    best_color = name

            if best_color:
                # Centro de la celda en píxeles
                cx = int((col + 0.5) * cell_w)
                cy = int((row + 0.5) * cell_h)

                # Centro de la celda en píxeles en cm (conversión)
                x_cm = round(cx * cm_px[0], 2)
                y_cm = round(cy * cm_px[1], 2)

                # Posición de la pieza en la cuadrícula (quitarlo si se prefieren cm)
                cell_width_cm = BASE_WIDTH_CM / GRID_WIDTH
                cell_height_cm = BASE_HEIGHT_CM / GRID_HEIGHT
                cell_x = int(x_cm / cell_width_cm)
                cell_y = int(y_cm / cell_height_cm)

                colorBGR = next((c[3] for c in COLORS if c[0] == best_color), (0, 0, 0))
                pieces.append({
                    "name": best_color,
                    "center_px": (cx, cy),
                    "center_cm": (x_cm, y_cm),
                    "cell": (cell_x, cell_y),
                    "angle": 0,
                    "colorBGR": colorBGR
                })

    if debug:
        draw_pieces_grid(frame, pieces)

    return pieces

# Dibuja la cuadrícula (líneas moradas) y las piezas
def draw_pieces_grid(frame, pieces, draw_grid=True):
    if draw_grid:
        frame_h, frame_w = frame.shape[:2]
        cell_w = frame_w / GRID_WIDTH
        cell_h = frame_h / GRID_HEIGHT
        for i in range(1, GRID_WIDTH):
            x = int(i * cell_w)
            cv2.line(frame, (x, 0), (x, frame_h), (255, 0, 170), 1)
        for i in range(1, GRID_HEIGHT):
            y = int(i * cell_h)
            cv2.line(frame, (0, y), (frame_w, y), (255, 0, 170), 1)

    # Dibujar piezas
    for p in pieces:
        cx, cy = p["center_px"]
        cv2.circle(frame, (cx, cy), 10, p["colorBGR"], -1)
        cv2.circle(frame, (cx, cy), 10, (0, 0, 0), 2)
        #cv2.putText(frame, p["name"], (cx-20, cy-15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, p["colorBGR"], 2)