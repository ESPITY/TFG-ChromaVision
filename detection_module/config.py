# ChromaVision - Lucía García Bobillo
# Config: crea un archivo JSON cuando se ejecuta que permite modificar los valores por defecto
import sys
import os
import numpy as np
import json
import time
    
# Valores de configuración por defecto
DEFAULT_CONFIG = {
    # HSV -> Hue-X (0-180) Saturation-Y (0-255) Value-Z (0-255)
    # Color: nombre, lowerHSV, upperHSV, colorBGR
    "COLORS": [
        ["Rojo", [0, 200, 20], [9, 255, 255], [0, 0, 255]],
        ["Amarillo", [19, 120, 50], [38, 255, 255], [0, 255, 255]],
        ["Azul", [100, 150, 20], [120, 255, 255], [255, 190, 0]],
        ["Verde", [40, 130, 20], [100, 255, 255], [0, 255, 0]],
        ["Negro", [0, 0, 0], [179, 255, 35], [120, 120, 120]],
        ["Naranja", [9, 150, 120], [19, 255, 255], [0, 125, 255]],
        ["Rosa", [125, 40, 125], [15, 150, 255], [190, 130, 250]]
    ],
    "WINDOW_SCALE": 1.0,            # Escalar el tamaño de las ventanas
    "WARP_OUTPUT_SIZE": 800,        # Tamaño del lado más largo de la imagen base_warped
    "GRID_WIDTH": 16,               # 16x16 celdas (base 32x32 studs)
    "GRID_HEIGHT": 16,
    "PERCENT_FILLED_CELL": 0.6,     # % de relleno de color de la celda para considerarla ocupada
    "MIN_BASE_AREA_RATIO": 0.05,    # % mínimo del frame que debe ocupar la base
    "SHOW_PIECES_GRID": True,       # Mostrar la cuadrícula de la ventana "Piezas"
    "UDP_IP": "127.0.0.1",          # IP de la conexión por socket UDP
    "UDP_PORT": 5005                # Puerto de la conexión por socket UDP
}

# Mostrar mensaje de estatus del guardado de la configuración (durante X segundos)
STATUS_CONFIG_MSG_SUCCESS = "Configuracion guardada"
STATUS_CONFIG_MSG_ERROR = "Error: usada configuracion por defecto"
STATUS_CONFIG_MSG_TIME = 2.0
status_config_msg = ""
status_expire = 0.0

def set_status_config_msg(message):
    global status_config_msg, status_expire
    status_config_msg = message
    status_expire = time.time() + STATUS_CONFIG_MSG_TIME

# Guardar la configuración en un JSON
def save_config(config_path, data):
    # Escribir cada color en una línea
    colors_lines = []
    for color in data["COLORS"]:
        color_json = json.dumps(color, separators=(', ', ': '))
        colors_lines.append("        " + color_json)  # Indentación
    colors_block = "[\n" + ",\n".join(colors_lines) + "\n    ]"

    # Formatear el resto de parámetros
    other_data = {key: value for key, value in data.items() if key != "COLORS"}
    other_data_json = json.dumps(other_data, indent=4, ensure_ascii=False)

    # JSON final: juntar COLORS y el resto de parámetros detnro de llaves
    final_json = "{\n" + '    "COLORS": ' + colors_block + ",\n" + other_data_json[1:]

    # Guardar el JSON final en "config.json"
    with open(config_path, "w", encoding="utf-8") as file:
        file.write(final_json)

# Asigna las variables del diccionario de "config.json"
def apply_config(config_dict):
    global COLORS, WINDOW_SCALE, WARP_OUTPUT_SIZE, GRID_WIDTH, GRID_HEIGHT
    global PERCENT_FILLED_CELL, MIN_BASE_AREA_RATIO, SHOW_PIECES_GRID
    global UDP_IP, UDP_PORT

    COLORS = []
    for color in config_dict["COLORS"]:
        name = color[0]
        lower_HSV = np.array(color[1])
        upper_HSV = np.array(color[2])
        color_BGR = tuple(color[3])
        COLORS.append([name, lower_HSV, upper_HSV, color_BGR])

    WINDOW_SCALE = float(config_dict["WINDOW_SCALE"])
    WARP_OUTPUT_SIZE = int(config_dict["WARP_OUTPUT_SIZE"])
    GRID_WIDTH = int(config_dict["GRID_WIDTH"])
    GRID_HEIGHT = int(config_dict["GRID_HEIGHT"])
    PERCENT_FILLED_CELL = float(config_dict["PERCENT_FILLED_CELL"])
    MIN_BASE_AREA_RATIO = float(config_dict["MIN_BASE_AREA_RATIO"])
    SHOW_PIECES_GRID = bool(config_dict["SHOW_PIECES_GRID"])
    UDP_IP = str(config_dict["UDP_IP"])
    UDP_PORT = int(config_dict["UDP_PORT"])

# Carga la configuración desde "config.json", o lo crea con los valores por defecto si no existe/no válido
def load_config(show_success_message=False):
    # Obtener la ruta de "config.json" sumándole la dirección del script/ejecutable
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")

    # Intentar leer el archivo "config.json"
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config_dict = json.load(file)

        # Comprobar si los datos leídos tienen estructura de diccionario
        if not isinstance(config_dict, dict):
            raise ValueError("Estructura de JSON incorrecta")
        apply_config(config_dict)   # Lanzará un error si los valores no son correctos

        if show_success_message:
            set_status_config_msg(STATUS_CONFIG_MSG_SUCCESS)
            print("Configuración actualizada desde 'config.json'")

        return True

    # Si algo falla al leer "config.json"
    except Exception as e:
        if os.path.exists(config_path):
            set_status_config_msg(STATUS_CONFIG_MSG_ERROR)
            print(f"Configuración no válida ({e}) => Usando valores por defecto")
        else:
            print("No se encontró 'config.json' => Creando archivo con valores por defecto")

        apply_config(DEFAULT_CONFIG)
        # Fallos en el guardado de "config.json" (no existe/no válido) => valores por defecto 
        try:
            save_config(config_path, DEFAULT_CONFIG)
        except Exception:
            pass

        return False

# Inicializar al importar
load_config()