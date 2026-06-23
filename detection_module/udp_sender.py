# ChromaVision - Lucía García Bobillo
# UDP Sender: envía información de las piezas (color y posición) al motor de videojuegos por UDP
import socket
import json

import config

# Clase para crear un socket UDP y poder reutilizarlo (en lugar de crear/cerrar uno por cada envío)
class UDP_socket:
    def __init__(self, ip=config.UDP_IP, port=config.UDP_PORT):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # Socket UDP
        self.socket_error_printed = False    # Flag indica si el error de socket ya se ha impreso 1 vez
    
    # Envía la lista de piezas por UDP en formato JSON
    def send_pieces(self, pieces):
        # Se envía incluso si la lista está vacía para que el motor gestione
        # la eliminación de todos los actores cuando no se detectan piezas

        # JSON
        data = {
            "pieces": [
                {
                    "color": p["name"],
                    "x": p["cell"][0],
                    "y": p["cell"][1],
                }
                for p in pieces
            ]
        }
        message = json.dumps(data)

        try:
            self.sock.sendto(message.encode('utf-8'), (self.ip, self.port))
        except OSError as e:
            if not self.socket_error_printed:
                print(f"Error en el envío por socket UDP: {e}")
                self.socket_error_printed = True
    
    def close_socket(self):
        self.sock.close()