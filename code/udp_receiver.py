import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
BUFFER_SIZE = 65535  # Tamaño máximo de un datagrama UDP

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Escuchando mensajes UDP en {UDP_IP}:{UDP_PORT}")

while True:
    try:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        message = data.decode('utf-8')
        print(f"Recibido {len(data)} bytes desde {addr}:")
        print(message)
        print("-" * 50)
    except OSError as e:
        print(f"Error: {e}")