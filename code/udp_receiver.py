import socket
import json
import threading
import numpy as np
from config import COLORS, COLORS_LOCK, update_color_range   # Asegúrate de tener update_color_range

UDP_IP = "127.0.0.1"
UDP_PORT = 5006

class UDP_RECEIVER:
    def __init__(self, ip="127.0.0.1", port=5006):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True

    def start_listening(self):
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(1.0)
        print(f"Servidor UDP escuchando en {self.ip}:{self.port}")
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                msg = json.loads(data.decode('utf-8'))
                print(msg)
                self.process_command(msg)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error: {e}")

    def close_socket(self):
        self.running = False
        self.sock.close()

    # Convierte HSV del motor (H:0-360, S:0-1, V:0-1) a OpenCV (H:0-179, S:0-255, V:0-255)
    def hsv_to_opencv(self, h, s, v):
        h_opencv = int(h / 2)
        s_opencv = int(s * 255)
        v_opencv = int(v * 255)
        return (
            max(0, min(180, h_opencv)),
            max(0, min(255, s_opencv)),
            max(0, min(255, v_opencv))
        )

    def process_command(self, msg):
        cmd = msg.get('command')
        if cmd == 'set_multiple_ranges':
            colors_list = msg.get('colors', [])
            if not colors_list:
                print("Comando 'set_multiple_ranges' sin lista de colores")
                return

            new_colors = []
            for color_data in colors_list:
                name = color_data.get('name')
                if not name:
                    print("Color sin nombre, omitido")
                    continue

                # Extraer valores individuales (formato que envía Unreal)
                lower_h = color_data.get('lower_h', 0)
                lower_s = color_data.get('lower_s', 0.0)
                lower_v = color_data.get('lower_v', 0.0)
                upper_h = color_data.get('upper_h', 360)
                upper_s = color_data.get('upper_s', 1.0)
                upper_v = color_data.get('upper_v', 1.0)

                # Convertir a OpenCV ranges
                lower = self.hsv_to_opencv(lower_h, lower_s, lower_v)
                upper = self.hsv_to_opencv(upper_h, upper_s, upper_v)

                # Color BGR para depuración (opcional, a partir de r,g,b si existen)
                r = color_data.get('r', 255)
                g = color_data.get('g', 255)
                b = color_data.get('b', 255)
                bgr = (int(b), int(g), int(r))  # OpenCV usa BGR

                new_colors.append([name, np.array(lower, dtype=np.int32), np.array(upper, dtype=np.int32), bgr])

            if new_colors:
                with COLORS_LOCK:
                    COLORS.clear()
                    COLORS.extend(new_colors)
                print(f"Lista completa de colores actualizada: {len(new_colors)} colores recibidos")
                # Opcional: imprimir los rangos para depuración
                for c in new_colors:
                    print(f"   {c[0]}: lower={c[1]}, upper={c[2]}")
            else:
                print("No se recibieron colores válidos")

        else:
            print(f"Comando desconocido: {cmd}")


# Para probar de forma independiente
if __name__ == "__main__":
    receptor = UDP_RECEIVER()
    try:
        receptor.start_listening()
    except KeyboardInterrupt:
        receptor.close_socket()
        print("Cerrado")