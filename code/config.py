# Config
import numpy as np

# HSV -> Hue-X (0-180) Saturation-Y (0-255) Value (0-255) -> Value (20-255) normalmente
# Color: Nombre, lower HSV, upper HSV, color BGR
COLORS = [
    ["Rojo", np.array([0, 200, 20]), np.array([10, 255, 255]), (0, 0, 255)],
    ["Amarillo", np.array([15, 180, 20]), np.array([25, 255, 255]), (0, 255, 255)],
    ["Azul", np.array([100, 200, 20]), np.array([120, 255, 255]), (255, 0, 0)],
    ["Verde", np.array([40, 150, 20]), np.array([100, 255, 255]), (0, 255, 0)],
    ["Negro", np.array([0, 0, 0]), np.array([179, 255, 40]), (105, 105, 105)],
    ["Naranja", np.array([8, 150, 120]), np.array([20, 255, 255]), (0, 164, 255)],
    ["Lila", np.array([120, 30, 130]), np.array([180, 90, 255]), (204, 150, 245)]
]
#["Rojo", np.array([0, 200, 20]), np.array([5, 255, 255]), (0, 0, 255)],

BASE_WIDTH_CM = 25.5        # Ancho real de la base en cm
BASE_HEIGHT_CM = 25.5       # Alto real de la base en cm
MIN_PIECE_AREA = 1000       # Tamaño mínimo del contorno de color detectado
IMG_SCALE = 1               # Ver las ventanas/frames a menor tamaño (0.4)
WARP_OUTPUT_SIZE = 800      # Tamaño del lado más largo de la imagen warp
GRID_WIDTH = 16              # 16x16 celdas (base 32x32)
GRID_HEIGHT = 16              # 16x16 celdas (base 32x32)
PERCENT_FILLED_CELL = 0.6    # Porcentaje de relleno de color de la celda para considerarla ocupada