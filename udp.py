import socket


def send_pieces_unreal(pieces):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)