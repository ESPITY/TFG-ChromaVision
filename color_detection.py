# Detección de color

import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2
import numpy as np

from config import MIN_PIECE_AREA


# Función de detección de color
def detect_color (frame, frame_HSV, name, lower, upper, colorBGR):
    mask = cv2.inRange(frame_HSV, lower, upper) # Máscara del color

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

                texto = f"Pos: ({cx},{cy}) Ang: {int(angle)}"
                cv2.putText(frame, texto, (cx - 50, cy - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colorBGR, 2)

                #x, y, w, h = cv2.boundingRect(mask_contour) # Coordenadas del rectángulo (esquina superior izq. e inferior der.)
                #cv2.rectangle(frame, pt1=(x, y), pt2=(x + w, y + h), color=colorBGR, thickness=3) # Dibujar rectángulo
                #cv2.putText(frame, name,(x, y-10), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=colorBGR, thickness=2)
    
    return mask