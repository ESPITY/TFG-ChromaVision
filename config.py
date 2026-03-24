# Config
import numpy as np

# HSV -> Hue-X (0-180) Saturation-Y (0-255) Value (0-255) -> Value (20-255) normalmente
# Color: Nombre, lower HSV, upper HSV, color BGR
COLORS = [
    ["Rojo", np.array([0, 200, 20]), np.array([5, 255, 255]), (0, 0, 255)],
    ["Amarillo", np.array([20, 200, 20]), np.array([25, 255, 255]), (0, 255, 255)],
    ["Azul", np.array([105, 200, 20]), np.array([115, 255, 255]), (255, 0, 0)],
    ["Verde", np.array([40, 150, 20]), np.array([100, 255, 255]), (0, 255, 0)],
    ["Negro", np.array([0, 0, 0]), np.array([180, 255, 30]), (105, 105, 105)]
]

BASE_SIZE_MM = 250  # Tamaño de la base
MIN_PIECE_AREA = 1000  # Tamaño mínimo del contorno de color detectado
IMG_SCALE = 1 # Ver las ventanas/frames a menor tamaño (0.4)