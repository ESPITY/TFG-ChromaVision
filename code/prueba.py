# Mostrar una imagen con el color HSV y otra con el en HSV convertido a BGR
import cv2
import numpy as np

# Tamaño de la imagen
height = 400
width = 600

# Color HSV (OpenCV H:0-179, S:0-255, V:0-255)
h = 120
s = 255
v = 255
    # ["Rojo", np.array([0, 200, 20]), np.array([10, 255, 255]), (0, 0, 255)],
    # ["Amarillo", np.array([15, 200, 20]), np.array([25, 255, 255]), (0, 255, 255)],
    # ["Azul", np.array([100, 200, 20]), np.array([120, 255, 255]), (255, 0, 0)],
    # ["Verde", np.array([40, 150, 20]), np.array([100, 255, 255]), (0, 255, 0)],
    # ["Negro", np.array([0, 0, 0]), np.array([180, 255, 40]), (105, 105, 105)],
    # ["Naranja", np.array([8, 150, 120]), np.array([20, 255, 255]), (0, 164, 255)]

# Crear imagen HSV rellena
image_hsv = np.full((height, width, 3), (h, s, v), dtype=np.uint8)

# Convertir a BGR para mostrar correctamente
image_bgr = cv2.cvtColor(image_hsv, cv2.COLOR_HSV2BGR)

# Mostrar
cv2.imshow("Color HSV", image_hsv)
cv2.imshow("Color HSV en BGR", image_bgr)
cv2.waitKey(0)
cv2.destroyAllWindows()