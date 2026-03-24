# Main
import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"    # Inicialización más rápida de la webcam

import cv2
import numpy as np

from config import COLORS, IMG_SCALE
from color_detection import detect_color
from base_detection import detect_base


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

    # Detección de la base (HoughLines)
    frame_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Convertir el frame de BGR a escala de grises
    frame_base = frame.copy()
    base = detect_base(frame_base, frame_grey)
    frame_base = cv2.resize(frame_base, None, fx=IMG_SCALE, fy=IMG_SCALE, interpolation=cv2.INTER_LINEAR)
    cv2.imshow("Base", frame_base)

    # Detección de las piezas (colores)
    frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # Convertir el frame de BGR a HSV
    frame_colors = frame.copy()
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