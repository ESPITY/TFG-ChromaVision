# Config
import numpy as np
import threading

# HSV -> Hue-X (0-180) Saturation-Y (0-255) Value (0-255) -> Value (20-255) normalmente
# Color: Nombre, lower HSV, upper HSV, color BGR
COLORS = [
    ["Rojo", np.array([0, 200, 20]), np.array([10, 255, 255]), (0, 0, 255)],
    ["Amarillo", np.array([15, 200, 20]), np.array([25, 255, 255]), (0, 255, 255)],
    ["Azul", np.array([100, 200, 20]), np.array([120, 255, 255]), (255, 0, 0)],
    ["Verde", np.array([40, 150, 20]), np.array([100, 255, 255]), (0, 255, 0)],
    ["Negro", np.array([0, 0, 0]), np.array([179, 255, 40]), (105, 105, 105)],
    ["Naranja", np.array([8, 150, 120]), np.array([20, 255, 255]), (0, 164, 255)]
]

BASE_WIDTH_CM = 25.5        # Ancho real de la base en cm
BASE_HEIGHT_CM = 25.5       # Alto real de la base en cm
MIN_PIECE_AREA = 1000       # Tamaño mínimo del contorno de color detectado
IMG_SCALE = 1               # Ver las ventanas/frames a menor tamaño (0.4)
WARP_OUTPUT_SIZE = 800      # Tamaño del lado más largo de la imagen warp
GRID_WIDTH = 16              # 16x16 celdas (base 32x32)
GRID_HEIGHT = 16              # 16x16 celdas (base 32x32)
PERCENT_FILLED_CELL = 0.6    # Porcentaje de relleno de color de la celda para considerarla ocupada


# Actualiza la lista de colores en tiempo de ejecución (UDP Reciever)
COLORS_LOCK = threading.Lock()
def update_color_range(name, lower_hsv, upper_hsv, bgr_color=None):
    with COLORS_LOCK:
        for i, c in enumerate(COLORS):
            if c[0] == name:
                c[1] = np.array(lower_hsv, dtype=np.int32)
                c[2] = np.array(upper_hsv, dtype=np.int32)
                if bgr_color:
                    c[3] = bgr_color
                print(f"[Config] Color '{name}' actualizado a HSV {lower_hsv} - {upper_hsv}")
                return
        # Si no existe, añadir nuevo color
        COLORS.append([name, np.array(lower_hsv), np.array(upper_hsv), bgr_color or (255,255,255)])
        print(f"[Config] Nuevo color '{name}' añadido")