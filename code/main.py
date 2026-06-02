# Main
import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"    # Inicialización más rápida de la webcam

import cv2
import numpy as np
import time

import config
from color_detection import get_masks, detect_pieces_grid
from base_detection import detect_base
from base_warp import base_warp
from udp_sender import UDP_socket


def main():
    print("Iniciando webcam...")

    # Webcam
    stream =  cv2.VideoCapture(0)
    if not stream.isOpened():
        print("Error accediendo a la webcam")
        exit()

    # Configurar: fps, altura y ancho de frames de la webcam y nº de frames almacenados en el buffer
    stream.set(cv2.CAP_PROP_FPS , 30.0)
    stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    stream.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    udp = UDP_socket()    # Instanciar un socket UDP para enviar las piezas

    # Obtener todos los frames
    while (True):
        success, frame = stream.read()
        if not success:
            break

        # 1. Detección de la base (HoughLines)
        frame_base = frame.copy()
        base = detect_base(frame_base)

        frame_base_resized = cv2.resize(frame_base, None, fx=config.WINDOW_SCALE, fy=config.WINDOW_SCALE, interpolation=cv2.INTER_LINEAR)
        if config.status_config_msg and time.time() < config.status_expire:
            cv2.putText(frame_base_resized, config.status_config_msg, (30, frame_base_resized.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.imshow("Base", frame_base_resized)

        # 2. Perspectiva/Warp
        if base is not None:
            corners = base['corners']
            frame_warped = base_warp(frame.copy(), corners, output_longest_side=config.WARP_OUTPUT_SIZE)

            masks = get_masks(frame_warped)
            pieces = detect_pieces_grid(frame_warped, masks)

            frame_pieces = frame_warped.copy()  # Si se ha detectado base mostrar el frame con warp y piezas
            
            udp.send_pieces(pieces)
        else:
            # Imagen por defecto de la ventana "Piezas" (cuando no se detecta base)
            default_pieces_img = np.zeros((config.WARP_OUTPUT_SIZE, config.WARP_OUTPUT_SIZE, 3), dtype=np.uint8)
            text = "Base NO detectada"
            font_face = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1
            font_color = (0, 0, 255)
            thickness = 2
            text_width, text_height = cv2.getTextSize(text, font_face, font_scale, thickness)[0]
            center_text_coordinates = (int(config.WARP_OUTPUT_SIZE / 2) - int(text_width / 2), int(config.WARP_OUTPUT_SIZE / 2) + int(text_height / 2))
            cv2.putText(default_pieces_img, text, center_text_coordinates, font_face, font_scale, font_color, thickness)

            frame_pieces = default_pieces_img.copy()  # Si no se ha detectado la base mostrar una imagen por defecto

        frame_pieces_resized = cv2.resize(frame_pieces, None, fx=config.WINDOW_SCALE, fy=config.WINDOW_SCALE, interpolation=cv2.INTER_LINEAR)
        if config.status_config_msg and time.time() < config.status_expire:
            cv2.putText(frame_pieces_resized, config.status_config_msg, (30, frame_pieces_resized.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.imshow("Piezas", frame_pieces_resized)

        key = cv2.waitKey(1) & 0xFF
         # Recargar los valores de configuración al pulsar la tecla r/R
        if key == ord('r') or key == ord('R'):
            config.load_config(show_success_message=True)
        # Cierre de todas las ventanas pulsando la tecla Escape (27) o pinchando en la X de alguna de las dos ventanas
        if key == 27:
            break
        if cv2.getWindowProperty("Base", cv2.WND_PROP_VISIBLE) < 1 or cv2.getWindowProperty("Piezas", cv2.WND_PROP_VISIBLE) < 1:
            break

    udp.close_socket()
    stream.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()