import cv2
import numpy as np


# HSV -> Hue-X (0-180) Saturation-Y (0-255) Value (0-255)

# Rango para detectar el color (HSV) -> Value (20-255) normalmente
# Rojo: d50f07 - (2, 96.7, 83.5)
r_lower = np.array([0, 200, 20])
r_upper = np.array([5, 255, 255])
# Amarillo: ffd322 - (48, 86, 100)
y_lower = np.array([20, 200, 20])
y_upper = np.array([25, 255, 255])
# Azul: 0058b7 - (211, 100, 71)
b_lower = np.array([105, 200, 20])
b_upper = np.array([115, 255, 255])
# Verde: 33823d - (128, 60.8, 51)
g_lower = np.array([40, 150, 20])
g_upper = np.array([100, 255, 255])
# Negro: 141616 - (180, 9.1, 8.6)
n_lower = np.array([0, 0, 0])
n_upper = np.array([180, 255, 30])

# Webcam
stream =  cv2.VideoCapture(0)

# Obtener todos los frames
while (True):
    success, frame = stream.read()

    frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # Convertir el frame de BGR a HSV

    mask = cv2.inRange(frame_HSV, n_lower, n_upper) # Máscara del color


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