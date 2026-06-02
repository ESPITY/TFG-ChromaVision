# Config
import numpy as np

# HSV -> Hue-X (0-180) Saturation-Y (0-255) Value (0-255) -> Value (20-255) normalmente
# Color: Nombre, lower HSV, upper HSV, color BGR
COLORS = [
    ["Rojo", np.array([0, 200, 20]), np.array([10, 255, 255]), (0, 0, 255)],
    ["Amarillo", np.array([15, 180, 20]), np.array([25, 255, 255]), (0, 255, 255)],
    ["Azul", np.array([100, 200, 20]), np.array([120, 255, 255]), (255, 190, 0)],
    ["Verde", np.array([40, 150, 20]), np.array([100, 255, 255]), (0, 255, 0)],
    ["Negro", np.array([0, 0, 0]), np.array([179, 255, 40]), (120, 120, 120)],
    ["Naranja", np.array([8, 150, 120]), np.array([20, 255, 255]), (0, 125, 255)],
    ["Rosa", np.array([120, 30, 130]), np.array([180, 90, 255]), (190, 130, 250)]
]

WINDOW_SCALE = 1                # Ver las ventanas/frames a menor tamaño (0.4)
WARP_OUTPUT_SIZE = 800          # Tamaño del lado más largo de la imagen warp
GRID_WIDTH = 16                 # 16x16 celdas (base 32x32)
GRID_HEIGHT = 16                # 16x16 celdas (base 32x32)
PERCENT_FILLED_CELL = 0.6       # Porcentaje de relleno de color de la celda para considerarla ocupada
MIN_BASE_AREA_RATIO = 0.05      # % mínimo del frame que debe ocupar la base (5%)