# Detección de colores - Código independiente

import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2
import numpy as np


# HSV -> Hue-X (0-180) Saturation-Y (0-255) Value (0-255) -> Value (20-255) normalmente
# Nombre, lower HSV, upper HSV, color BGR
COLORS = [
    ["Rojo", np.array([0, 200, 20]), np.array([5, 255, 255]), (0, 0, 255)],
    ["Amarillo", np.array([20, 200, 20]), np.array([25, 255, 255]), (0, 255, 255)],
    ["Azul", np.array([105, 200, 20]), np.array([115, 255, 255]), (255, 0, 0)],
    ["Verde", np.array([40, 150, 20]), np.array([100, 255, 255]), (0, 255, 0)],
    ["Negro", np.array([0, 0, 0]), np.array([180, 255, 30]), (105, 105, 105)]
]

MIN_PIECE_AREA = 1000  # Tamaño mínimo del contorno de color detectado
IMG_SCALE = 1 # Ver las ventanas/frames a menor tamaño (0.4)


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

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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

    # Detección de las piezas (colores)
    frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # Convertir el frame de BGR a HSV
    for name, lower, upper, colorBGR in COLORS:
        mask = detect_color(frame, frame_HSV, name, lower, upper, colorBGR)
        mask = cv2.resize(mask, None, fx=IMG_SCALE, fy=IMG_SCALE, interpolation=cv2.INTER_LINEAR)
        cv2.imshow("Mask " + name, mask)

    # Mostrar webcam y máscara
    frame = cv2.resize(frame, None, fx=IMG_SCALE, fy=IMG_SCALE, interpolation=cv2.INTER_LINEAR)
    cv2.imshow("Webcam", frame)

    # STACK IMAGES

    if cv2.waitKey(1) == ord('q'):
        break

stream.release()
cv2.destroyAllWindows()