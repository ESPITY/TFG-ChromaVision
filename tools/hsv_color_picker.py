# hsv_color_picker: herramienta auxiliar de cuentagotas. Muestra los valores BGR y HSV del píxel
# seleccionado con el ratón sobre la imagen de la webcam

import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"    # Inicialización más rápida de la webcam

import cv2


# Variable global para almacenar la posición del click
clicked_pixel = None

# Función que se llama al hacer clic en la ventana
def get_pixel_color(event, x, y, flags, param):
    global clicked_pixel
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_pixel = (x, y)

# Abrir webcam
cap = cv2.VideoCapture(0)
cv2.namedWindow("Webcam")
cv2.setMouseCallback("Webcam", get_pixel_color)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convertir a HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    if clicked_pixel is not None:
        x, y = clicked_pixel
        # Obtener valores del píxel
        bgr_color = frame[y, x]       # BGR
        hsv_color = hsv_frame[y, x]   # HSV
        print(f"\nPixel ({x},{y}) - BGR: {bgr_color}, HSV: {hsv_color}")    # Imprimir en consola BGR y HSV

        # Dibujar un círculo donde se hizo click
        cv2.circle(frame, (x, y), 5, (0, 255, 0), 2)

    cv2.imshow("Webcam", frame)

    key = cv2.waitKey(1) & 0xFF
    # Cierre de todas las ventanas pulsando la tecla Escape (27) o pinchando en la X de alguna de las dos ventanas
    if key == 27:
        break
    if cv2.getWindowProperty("Webcam", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()