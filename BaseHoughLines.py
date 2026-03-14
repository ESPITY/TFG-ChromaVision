# HoughLine
import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2
import numpy as np

def detect_base(frame, frame_grey):
    frame_blur  = cv2.bilateralFilter(frame_grey, 20, 30, 30) # Reducir el sonido manteniendo bordes nítidos
    cv2.imshow("Blur", frame_blur)

    ret, otsu_binary = cv2.threshold(frame_grey,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) # Convertir la imagen a binario
    cv2.imshow("OTSU Binary", otsu_binary)
    edges = cv2.Canny(otsu_binary, 10, 20)
    cv2.imshow("Edges", edges)

    # Aumentar el grosor de los bordes
    kernel = np.ones((3, 3), np.uint8) 
    edges = cv2.dilate(edges, kernel, iterations=1)
    cv2.imshow("Edges", edges)

    # HOUGH LINES (Resolución - rho: 1px, theta: 1º) (Threshold: mín de votos para considerar una línea)
    lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=150)

    if lines is not None:
        print(f"Líneas detectadas: {len(lines)}")   # Array de r y theta

        for line in lines:  # (N, rho, theta)
            rho, theta = line[0]
            print(line)

            a = np.cos(theta)
            b = np.sin(theta)

            x0 = a * rho    # rho * cos(tetha)
            y0 = b * rho    # rho * sen(tetha)

            # 1000 es la longitud de la línea
            x1 = int(x0 + 1000 * (-b))    # (r * cos(theta) - 1000 * sin(theta))
            y1 = int(y0 + 1000 * (a))     # (rs * in(theta) + 1000 * cos(theta))

            x2 = int(x0 - 1000 * (-b))    # (r * cos(theta) + 1000 * sin(theta))
            y2 = int(y0 - 1000 * (a))     # (r * sin(theta) - 1000 * cos(theta))

            cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

stream =  cv2.VideoCapture(0)

stream.set(cv2.CAP_PROP_FPS , 30.0)
stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

while (True):
    success, frame = stream.read()

    frame_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Convertir el frame de BGR a escala de grises
    detect_base(frame, frame_grey)
    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) == ord('q'):
        break

stream.release()
cv2.destroyAllWindows()