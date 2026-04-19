# Detección de color

import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2
import numpy as np

from config import COLORS, MIN_PIECE_AREA   #, IMG_SCALE


# Detectar todos los colores
def detect_all_colors(frame, cm_px_width=None, cm_px_height=None):
    frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # Convertir el frame de BGR a HSV

    all_pieces = []
    for color in COLORS:
        mask, pieces = detect_color(frame, frame_HSV, color, cm_px_width, cm_px_height)
        all_pieces.extend(pieces)

        #mask = cv2.resize(mask, None, fx=IMG_SCALE, fy=IMG_SCALE, interpolation=cv2.INTER_LINEAR)
        #cv2.imshow("Mask " + name, mask)

    return all_pieces

# Función de detección de color
def detect_color (frame, frame_HSV, color, cm_px_width=None, cm_px_height=None):
    name, lower, upper, colorBGR = color
    mask = cv2.inRange(frame_HSV, lower, upper) # Máscara del color
    pieces = []

    # Obtener la posición del "objeto" y dibujar un cuadrado alrededor
    # Buscar contornos en la máscara (coordenadas y relación entre ellos)
    mask_contours, hierarchy  = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 

    # Posición de los contornos (si hay)
    if len(mask_contours) != 0:
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
                    angle = angle + 90

                 # Dibujar
                box = cv2.boxPoints(rect)
                box = np.intp(box)

                cv2.drawContours(frame, [box], 0, colorBGR, 2)
                cv2.circle(frame, (cx, cy), 5, colorBGR, -1)

                # Imprimir posición en px o coordenadas dependiendo de si se detectó la base
                if cm_px_width is not None and cm_px_height is not None:
                    x_cm = cx * cm_px_width
                    y_cm = cy * cm_px_height
                    texto = f"Pos: ({x_cm:.2f}, {y_cm:.2f})"    # Ang: {int(angle)}
                    center_cm = (x_cm, y_cm)
                else:
                    texto = f"Pos: ({cx}, {cy})"    # Ang: {int(angle)}
                    center_cm = None

                cv2.putText(frame, texto, (cx - 50, cy - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colorBGR, 2)

                #x, y, w, h = cv2.boundingRect(mask_contour) # Coordenadas del rectángulo (esquina superior izq. e inferior der.)
                #cv2.rectangle(frame, pt1=(x, y), pt2=(x + w, y + h), color=colorBGR, thickness=3) # Dibujar rectángulo
                #cv2.putText(frame, name,(x, y-10), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=colorBGR, thickness=2)

                pieces.append({
                    "name": name,
                    "center_px": (cx, cy),
                    "center_cm": center_cm,
                    "angle": angle,
                    "colorBGR": colorBGR
                })
    
    return mask, pieces