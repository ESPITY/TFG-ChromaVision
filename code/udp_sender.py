import socket
import json

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# Clase para crear un socket UDP y poder reutilizarlo (en lugar de crear/cerrar uno por cada envío)
class UDP_SENDER:
    def __init__(self, ip="127.0.0.1", port=5005):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # Socket UDP
    
    # Envía la lista de piezas por UDP en formato JSON
    def send_pieces(self, pieces):
        # if not pieces:
        #     return
        
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
        self.sock.sendto(message.encode('utf-8'), (self.ip, self.port))
    
    def close_socket(self):
        self.sock.close()