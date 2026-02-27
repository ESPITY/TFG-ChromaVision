import cv2
import numpy as np


# HSV -> Hue-X (0-180) Saturation-Y (0-255) Value (0-255)

# Rango para detectar el color (HSV) -> Value (20-255) normalmente
# Nombre, lower HSV, upper HSV, color BGR
COLORS = [
    ["Rojo", np.array([0, 200, 20]), np.array([5, 255, 255]), (0, 0, 255)],
    ["Amarillo", np.array([20, 200, 20]), np.array([25, 255, 255]), (0, 255, 255)],
    ["Azul", np.array([105, 200, 20]), np.array([115, 255, 255]), (255, 0, 0)],
    ["Verde", np.array([40, 150, 20]), np.array([100, 255, 255]), (0, 255, 0)],
    ["Negro", np.array([0, 0, 0]), np.array([180, 255, 30]), (0, 0, 0)]
]

MIN_AREA = 500  # Tamaño mínimo del contorno de color detectado

def detect_color (frame, frame_HSV, name, lower, upper, colorBGR):
    mask = cv2.inRange(frame_HSV, lower, upper) # Máscara del color

    # Obtener la posición del "objeto" y dibujar un cuadrado alrededor
    # Buscar contornos en la máscara (coordenadas y relación entre ellos)
    mask_contours, hierarchy  = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 

    # Posición de los contornos (si hay)
    if len(mask_contours) != 0:
        for mask_contour in mask_contours:
            if cv2.contourArea(mask_contour) > MIN_AREA: # El contorno tiene que tener un tamaño mínimo
                x, y, w, h = cv2.boundingRect(mask_contour) # Coordenadas del rectángulo (esquina superior izq. e inferior der.)
                cv2.rectangle(frame, pt1=(x, y), pt2=(x + w, y + h), color=colorBGR, thickness=3) # Dibujar rectángulo
                cv2.putText(frame, name,(x, y-10), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=colorBGR, thickness=2)
    
    return mask



# Webcam
stream =  cv2.VideoCapture(0)

if not stream.isOpened():
    print("Error accediendo a la webcam")
    exit()

# Obtener todos los frames
while (True):
    success, frame = stream.read()

    if not success:
        break

    frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # Convertir el frame de BGR a HSV

    for name, lower, upper, colorBGR in COLORS:
        mask = detect_color(frame, frame_HSV, name, lower, upper, colorBGR)
        cv2.imshow("Mask " + name, mask)

    # Mostrar webcam y máscara
    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) == ord('q'):
        break

stream.release()
cv2.destroyAllWindows()