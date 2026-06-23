# ChromaVision - Lucía García Bobillo
# Warp de perspectiva de la imagen del área de la base
import cv2
import numpy as np

import config

# Warp de la perspectiva: imagen solo de la base adaptando las esquinas
def base_warp(frame, corners, output_longest_side=config.WARP_OUTPUT_SIZE):
    (top_left, top_right, bottom_right, bottom_left) = corners

    width_top = np.linalg.norm(top_right - top_left)
    height_right = np.linalg.norm(bottom_right - top_right)
    width_bottom = np.linalg.norm(bottom_right - bottom_left)
    height_left = np.linalg.norm(bottom_left - top_left)

    # Tamaño de la imagen de salida (conservando la relación de aspecto)
    avg_width = int((width_top + width_bottom) / 2)
    avg_height = int((height_right + height_left) / 2)

    if avg_width < 1 or avg_height < 1:   # Evitar división por cero
        return frame

    scale = output_longest_side / max(avg_width, avg_height)
    output_width, output_height = int(avg_width * scale), int(avg_height * scale)

    # Esquinas de la imagen final (sentido horario: TL, TR, BR, BL)
    output_corners = np.float32([[0, 0], [output_width - 1, 0], [output_width - 1, output_height - 1], [0, output_height - 1]])

    # Transformación de perspectiva
    matrix = cv2.getPerspectiveTransform(np.array(corners), output_corners)
    frame_warped = cv2.warpPerspective(frame, matrix, (output_width, output_height))

    return frame_warped