# Detección de colores

import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2
import numpy as np


# HSV -> Hue-X (0-180) Saturation-Y (0-255) Value (0-255) -> Value (20-255) normalmente
# Nombre, lower HSV, upper HSV, color BGR
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

def detect_base(frame, frame_grey):
    frame_grey  = cv2.bilateralFilter(frame_grey, 20, 30, 30) # Reducir el sonido manteniendo bordes nítidos
    #frame_grey = cv2.GaussianBlur(frame_grey,(5,5),0)
    ret, otsu_binary = cv2.threshold(frame_grey,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) # Convertir la imagen a binario
    edges = cv2.Canny(otsu_binary, 10, 20)

    # Aumentar el grosor de los bordes
    kernel = np.ones((3, 3), np.uint8) 
    edges = cv2.dilate(edges, kernel, iterations=1) 
    #cv2.imshow("dialte", img_dilation)

    # CONTORNO
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True) [:10] # Ordenar todos los contornos por tamaño y seleccionar el más grande (slice list 10)
    biggest = biggest_contour(contours)
    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(edges, [biggest], -1, (0, 255, 0), 3)

    # HOUGH LINES (4 líneas perpendiculares que delimitan la base. Las intersecciones son las 4 esquinas)
    # lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
    # edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    # if lines is not None:
    #     for line in lines:
    #         x1, y1, x2, y2 = line[0]
    #         cv2.line(edges, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    if biggest.size == 0:
        return edges

    # ESQUINAS
    points = biggest.reshape(4, 2)  # 4 listas con 2 cada una = 4 esquinas con X e Y
    input_points = np.zeros((4, 2), dtype="float32")    # Array vacío de floats para las esquinas ordenadas

    points_sum = points.sum(axis=1)                     # Sumamos coordenadas X e Y
    input_points[0] = points[np.argmin(points_sum)]
    input_points[3] = points[np.argmax(points_sum)]

    points_diff = np.diff(points, axis=1)   
    input_points[1] = points[np.argmin(points_diff)]
    input_points[2] = points[np.argmax(points_diff)]

    (top_left, top_right, bottom_right, bottom_left) = input_points
    bottom_width = np.sqrt(((bottom_right[0] - bottom_left[0]) ** 2) + ((bottom_right[1] - bottom_left[1]) ** 2))
    top_width = np.sqrt(((top_right[0] - top_left[0]) ** 2) + ((top_right[1] - top_left[1]) ** 2))
    right_height = np.sqrt(((top_right[0] - bottom_right[0]) ** 2) + ((top_right[1] - bottom_right[1]) ** 2))
    left_height = np.sqrt(((top_left[0] - bottom_left[0]) ** 2) + ((top_left[1] - bottom_left[1]) ** 2))

    # Tamaño de la imagen de salida -> se podrían usar las dimensiones de la base, pero ahora se usa el aspect ratio 1:1
    max_width = max(int(bottom_width), int(top_width))
    # max_height = max(int(right_height), int(left_height))
    max_height = int(max_width * 1)

    # PERSPECTIVA
    # Puntos deseados de la imagen final
    converted_points = np.float32([[0, 0], [max_width, 0], [0, max_height], [max_width, max_height]])

    # Transformacion de perspectiva
    matrix = cv2.getPerspectiveTransform(input_points, converted_points)
    framed = cv2.warpPerspective(frame, matrix, (max_width, max_height))
    cv2.imshow("Framed", framed)

    return edges

# Obtiene el contorno más grande con 4 esquinas (contorno)
def biggest_contour(contours):
    biggest = np.array([])  # contorno y área máxima
    max_area = 0

    for c in contours:
        area = cv2.contourArea(c)
        if area > 1000:
            perimeter = cv2.arcLength(c, True)  # Contorno cerrado
            approx = cv2.approxPolyDP(c, 0.012 * perimeter, True)   # Aproximarlo a otra forma (precisiónm, contorno cerrado)
            if area > max_area and len(approx) == 4:   # Supera el área máxima y tiene 4 esquinas
                biggest = approx
                max_area = area
    return biggest


# Función de detección de color
def detect_color (frame, frame_HSV, name, lower, upper, colorBGR):
    mask = cv2.inRange(frame_HSV, lower, upper) # Máscara del color

    # Obtener la posición del "objeto" y dibujar un cuadrado alrededor
    # Buscar contornos en la máscara (coordenadas y relación entre ellos)
    mask_contours, hierarchy  = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 

    # Posición de los contornos (si hay)
    if len(mask_contours) != 0:
        for mask_contour in mask_contours:
            if cv2.contourArea(mask_contour) > MIN_PIECE_AREA: # El contorno tiene que tener un tamaño mínimo
                # Centro (momentos)
                M = cv2.moments(mask_contour)
                if M["m00"] == 0:
                    continue

                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

                # Orientación
                rect = cv2.minAreaRect(mask_contour)
                (x, y), (w, h), angle = rect

                # Ajuste de ángulo
                if w < h:
                    angle = angle + 90

                 # Dibujar
                box = cv2.boxPoints(rect)
                box = np.intp(box)

                cv2.drawContours(frame, [box], 0, colorBGR, 2)
                cv2.circle(frame, (cx, cy), 5, colorBGR, -1)

                texto = f"Pos: ({cx},{cy}) Ang: {int(angle)}"
                cv2.putText(frame, texto, (cx - 50, cy - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colorBGR, 2)

                #x, y, w, h = cv2.boundingRect(mask_contour) # Coordenadas del rectángulo (esquina superior izq. e inferior der.)
                #cv2.rectangle(frame, pt1=(x, y), pt2=(x + w, y + h), color=colorBGR, thickness=3) # Dibujar rectángulo
                #cv2.putText(frame, name,(x, y-10), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=colorBGR, thickness=2)
    
    return mask

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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

# Obtener todos los frames
while (True):
    success, frame = stream.read()

    if not success:
        break

    # Detección de la base (contorno)
    frame_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Convertir el frame de BGR a escala de grises
    base = detect_base(frame, frame_grey)
    cv2.imshow("Base", base)

    # Detección de las piezas (colores)
    frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # Convertir el frame de BGR a HSV
    for name, lower, upper, colorBGR in COLORS:
        mask = detect_color(frame, frame_HSV, name, lower, upper, colorBGR)
        mask = cv2.resize(mask, None, fx=IMG_SCALE, fy=IMG_SCALE, interpolation=cv2.INTER_LINEAR)
        #cv2.imshow("Mask " + name, mask)

    # Mostrar webcam y máscara
    frame = cv2.resize(frame, None, fx=IMG_SCALE, fy=IMG_SCALE, interpolation=cv2.INTER_LINEAR)
    cv2.imshow("Webcam", frame)

    # STACK IMAGES

    if cv2.waitKey(1) == ord('q'):
        break

stream.release()
cv2.destroyAllWindows()