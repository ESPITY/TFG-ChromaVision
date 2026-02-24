import cv2
import numpy as np


# HSV -> Hue-X (0-180) Saturation-Y (0-255) Value (0-255)

# Rango para detectar el color (HSV) -> Value (20-255) normalmente
min = np.array([15, 150, 20])
max = np.array([35, 255, 255])

# Webcam
stream =  cv2.VideoCapture(0)

# Obtener todos los frames
while (True):
    success, frame = stream.read()

    frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # Convertir el frame de BGR a HSV

    mask = cv2.inRange(frame_HSV, min, max) # Máscara del color


    # Obtener la posición del "objeto" y dibujar un cuadrado alrededor
    # Buscar contornos en la máscara (coordenadas y relación entre ellos)
    mask_contours, hierarchy  = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 

    # Posición de los contornos (si hay)
    if len(mask_contours) != 0:
        for mask_contour in mask_contours:
            if cv2.contourArea(mask_contour) > 500: # El contorno tiene que tener un tamaño mínimo
                x, y, w, h = cv2.boundingRect(mask_contour) # Coordenadas del rectángulo (esquina superior izq. e inferior der.)
                cv2.rectangle(frame, pt1=(x, y), pt2=(x + w, y + h), color=(0, 0, 255), thickness=3) # Dibujar rectángulo


    # Mostrar webcam y máscara
    cv2.imshow("Mask", mask)
    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) == ord('q'):
        break

stream.release()
cv2.destroyAllWindows()