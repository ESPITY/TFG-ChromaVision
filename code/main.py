# Main
import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"    # Inicialización más rápida de la webcam

import cv2
import numpy as np

from config import IMG_SCALE, WARP_OUTPUT_SIZE, BASE_WIDTH_CM, BASE_HEIGHT_CM, COLORS, COLORS_LOCK
from color_detection import get_masks, detect_pieces_contours, detect_pieces_grid
from base_detection import detect_base
from udp_sender import UDP_SENDER
from udp_receiver import UDP_RECEIVER
import threading


# Warp de la perspectiva: imagen solo de la base adaptando las esquinas
def base_warp(frame, corners, output_longest_side=WARP_OUTPUT_SIZE):
    (top_left, top_right, bottom_right, bottom_left) = corners

    width_top = np.linalg.norm(top_right - top_left)
    height_right = np.linalg.norm(bottom_right - top_right)
    width_bottom = np.linalg.norm(bottom_right - bottom_left)
    height_left = np.linalg.norm(bottom_left - top_left)

    # Tamaño de la imagen de salida (conservando la relación de aspecto)
    avg_width = int((width_top + width_bottom) / 2)
    avg_height = int((height_right + height_left) / 2)

    if avg_width < 1 or avg_height < 1: # Evitar división por cero
        return frame

    scale = output_longest_side / max(avg_width, avg_height)
    output_width, output_height = int(avg_width * scale), int(avg_height * scale)

    # Esquinas de la imagen final (sentido horario: TL, TR, BR, BL)
    output_corners = np.float32([[0, 0], [output_width - 1, 0], [output_width - 1, output_height - 1], [0, output_height - 1]])

    # Transformacion de perspectiva
    matrix = cv2.getPerspectiveTransform(np.array(corners), output_corners)
    frame_warped = cv2.warpPerspective(frame, matrix, (output_width, output_height))

    return frame_warped


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

udp_sender = UDP_SENDER()    # Instanciar un socket UDP para enviar las piezas
udp_receiver = UDP_RECEIVER()
# Iniciar receptor UDP en un hilo separado para que la cámara siga funcionando
hilo_receptor = threading.Thread(target=udp_receiver.start_listening, daemon=True)
hilo_receptor.start()

# Obtener todos los frames
while (True):
    success, frame = stream.read()

    if not success:
        break

    # 1. Detección de la base (HoughLines)
    frame_base = frame.copy()
    base = detect_base(frame_base)

    frame_base = cv2.resize(frame_base, None, fx=IMG_SCALE, fy=IMG_SCALE, interpolation=cv2.INTER_LINEAR)
    cv2.imshow("Base", frame_base)

    # 2. Perspectiva/Warp
    frame_warped = None
    cm_px_width = None
    cm_px_height = None
    if base is not None:
        corners = base['corners']
        frame_warped = base_warp(frame.copy(), corners)
        height_warp, width_warp = frame_warped.shape[:2]

        # Conversión píxeles a cm
        cm_px_width = float(BASE_WIDTH_CM / width_warp)
        cm_px_height = float(BASE_HEIGHT_CM / height_warp)
        cm_px = (cm_px_width, cm_px_height)

        masks = get_masks(frame_warped)
        pieces = detect_pieces_grid(frame_warped, masks, cm_px, debug=True)

        frame_warped_show = cv2.resize(frame_warped, None, fx=IMG_SCALE, fy=IMG_SCALE, interpolation=cv2.INTER_LINEAR)
        cv2.imshow("Warped", frame_warped_show)

        #if pieces:
        udp_sender.send_pieces(pieces)
    else:
        # Detección de las piezas (colores)
        frame_colors = frame.copy()   # Si no se detecta la base se usará el frame sin warp perspective
        masks = get_masks(frame)
        pieces = detect_pieces_contours(frame_colors, masks, None, debug=True)

        frame_colors_show = cv2.resize(frame_colors, None, fx=IMG_SCALE, fy=IMG_SCALE, interpolation=cv2.INTER_LINEAR)
        cv2.imshow("Colores", frame_colors_show)

    # Mostrar webcam
    frame_show = cv2.resize(frame, None, fx=IMG_SCALE, fy=IMG_SCALE, interpolation=cv2.INTER_LINEAR)
    cv2.imshow("Webcam", frame_show)

    with COLORS_LOCK:
        print(COLORS)
        print("\n")

    if cv2.waitKey(1) == ord('q'):
        break

udp_sender.close_socket()
udp_receiver.close_socket()

stream.release()
cv2.destroyAllWindows()