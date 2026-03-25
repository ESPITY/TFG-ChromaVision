# Main
import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"    # Inicialización más rápida de la webcam

import cv2
import numpy as np

from config import COLORS, IMG_SCALE, WARP_OUTPUT_SIZE
from color_detection import detect_color
from base_detection import detect_base


# Warp de la perspectiva: imagen solo de la base adaptando las esquinas
def base_warp(frame, corners, output_longest_side=WARP_OUTPUT_SIZE):
    (top_left, top_right, bottom_right, bottom_left) = corners

    width_top = np.linalg.norm(top_right - top_left)
    height_right = np.linalg.norm(bottom_right - top_right)
    width_bottom = np.linalg.norm(bottom_right - bottom_left)
    height_left = np.linalg.norm(bottom_left - top_left)

    # Tamaño de la imagen de salida (conservando la relación de aspecto)
    avg_width = int((width_top + width_bottom) / 2)
    avg_height = int((height_right + height_left) / 2)

    if avg_width < 1 or avg_height < 1: # Evitar división por cero
        return frame

    scale = output_longest_side / max(avg_width, avg_height)
    output_width, output_height = int(avg_width * scale), int(avg_height * scale)

    # Esquinas de la imagen final (sentido horario: TL, TR, BR, BL)
    output_corners = np.float32([[0, 0], [output_width - 1, 0], [output_width - 1, output_height - 1], [0, output_height - 1]])

    # Transformacion de perspectiva
    matrix = cv2.getPerspectiveTransform(np.array(corners), output_corners)
    frame_warped = cv2.warpPerspective(frame, matrix, (output_width, output_height))

    return frame_warped


print("Inciando webcam...")

# Webcam
stream =  cv2.VideoCapture(0)

if not stream.isOpened():
    print("Error accediendo a la webcam")
    exit()

# Configurar, fps, altura y ancho de frames de la webcam
stream.set(cv2.CAP_PROP_FPS , 30.0)
stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

#stream.set(cv2.CAP_PROP_AUTOFOCUS, 0)
#stream.set(cv2.CAP_PROP_FOCUS, 5)

# Obtener todos los frames
while (True):
    success, frame = stream.read()

    if not success:
        break

    # 1. Detección de la base (HoughLines)
    frame_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Convertir el frame de BGR a escala de grises
    frame_base = frame.copy()
    base = detect_base(frame_base, frame_grey)

    frame_base = cv2.resize(frame_base, None, fx=IMG_SCALE, fy=IMG_SCALE, interpolation=cv2.INTER_LINEAR)
    cv2.imshow("Base", frame_base)

    # 2. Perspectiva/Warp
    frame_warped = None
    if base is not None:
        corners = base['corners']
        frame_warped = base_warp(frame.copy(), corners)

        frame_warped = cv2.resize(frame_warped, None, fx=IMG_SCALE, fy=IMG_SCALE, interpolation=cv2.INTER_LINEAR)
        cv2.imshow("Warped", frame_warped)

    # Detección de las piezas (colores)
    frame_colors = frame_warped if base is not None else frame.copy()   # Si no se detecta la base se usará el frame sin warp perspective
    frame_HSV = cv2.cvtColor(frame_colors, cv2.COLOR_BGR2HSV) # Convertir el frame de BGR a HSV
    for name, lower, upper, colorBGR in COLORS:
        mask = detect_color(frame_colors, frame_HSV, name, lower, upper, colorBGR)
        #mask = cv2.resize(mask, None, fx=IMG_SCALE, fy=IMG_SCALE, interpolation=cv2.INTER_LINEAR)
        #cv2.imshow("Mask " + name, mask)
    frame_colors = cv2.resize(frame_colors, None, fx=IMG_SCALE, fy=IMG_SCALE, interpolation=cv2.INTER_LINEAR)
    cv2.imshow("Colores", frame_colors)

    # Mostrar webcam
    frame = cv2.resize(frame, None, fx=IMG_SCALE, fy=IMG_SCALE, interpolation=cv2.INTER_LINEAR)
    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) == ord('q'):
        break

stream.release()
cv2.destroyAllWindows()