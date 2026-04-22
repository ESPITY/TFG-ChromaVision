# Detección de color

import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2
import numpy as np

from config import COLORS, MIN_PIECE_AREA, GRID_WIDTH, GRID_HEIGHT, PERCENT_FILLED_CELL   #, IMG_SCALE

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

# Detección de piezas por contornos (colores)
def detect_pieces_contours (frame, masks, cm_px=None, debug=False):
    pieces = []

    # Obtener la posición del "objeto" (contornos) y dibujar un cuadrado alrededor
    # Buscar contornos en la máscara (coordenadas y relación entre ellos)
    for name, mask in masks.items():
        mask_contours, _  = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
        
        for mask_contour in mask_contours:
            if cv2.contourArea(mask_contour) > MIN_PIECE_AREA: # El contorno tiene que tener un tamaño mínimo
                # Centro (momentos)
                M = cv2.moments(mask_contour)
                if M["m00"] == 0:
                    continue

                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

                # Orientación
                rect = cv2.minAreaRect(mask_contour)
                (x, y), (w, h), angle = rect

                # Ajuste de ángulo
                if w < h:
                    angle += 90

                box = cv2.boxPoints(rect)
                box = np.intp(box)
                colorBGR = next((c[3] for c in COLORS if c[0] == name), (0,0,0))

                # Imprimir posición en px o cm dependiendo de si se detectó la base (siempre será px)
                center_cm = (cx * cm_px[0], cy * cm_px[1]) if cm_px is not None else None

                # POSICIÓN EN CM O CELDA?
                pieces.append({
                    "name": name,
                    "center_px": (cx, cy),
                    "center_cm": center_cm,
                    "angle": angle,             # QUITARLO?, NO ES FIABLE
                    "colorBGR": colorBGR,
                    "box": box              # Dibujar el contorno
                })

    if debug:
        draw_pieces_contours(frame, pieces)
    
    return pieces

# Dibuja el rectángulo de cada pieza, su centro y su información
def draw_pieces_contours(frame, pieces):
    for p in pieces:
        if p.get("box") is not None:
            cv2.drawContours(frame, [p['box']], 0, p['colorBGR'], 2)

        cv2.circle(frame, p['center_px'], 5, p['colorBGR'], -1)

        # Imprime el nombre pero puede ser la posición en px o cm, sustituir el nombre por texto
        # if p.get("center_cm") is not None:
        #     texto = f"Pos: ({p['center_cm'][0]:.2f}, {p['center_cm'][1]:.2f})"
        # else:
        #     texto = f"Pos: ({p['center_px'][0]:.2f}, {p['center_px'][1]:.2f})"

        cv2.putText(frame, p['name'], (p['center_px'][0] - 50, p['center_px'][1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, p["colorBGR"], 2)

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
                # Conversión a cm
                x_cm = cx * cm_px[0]
                y_cm = cy * cm_px[1]

                colorBGR = next((c[3] for c in COLORS if c[0] == best_color), (0, 0, 0))
                pieces.append({
                    "name": best_color,
                    "center_px": (cx, cy),
                    "center_cm": (x_cm, y_cm),
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
        cv2.circle(frame, (cx, cy), 6, p["colorBGR"], -1)
        cv2.putText(frame, p["name"], (cx-20, cy-15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, p["colorBGR"], 2)