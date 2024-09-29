import socket
import random
import struct
import typing

LOCALHOST = "127.0.0.1"
DEFAULT_SERVER_PORT = 8081
BUFF_SIZE = 1080

CLIENT_PORT_LOWER = 2 ** 15
CLIENT_PORT_HIGHER = 2 ** 16

def ip_str_to_int(ip: str) -> int:
    octets = ip.split('.')
    octet1 = int(octets[0]) << 24
    octet2 = int(octets[1]) << 16
    octet3 = int(octets[2]) << 8
    octet4 = int(octets[3])
    return octet1 | octet2 | octet3 | octet4

def ip_int_to_str(ip: int) -> str:
    octet1= (ip >> 24) & 0xff
    octet2= (ip >> 16) & 0xff
    octet3= (ip >> 8) & 0xff
    octet4= ip & 0xff
    return str(octet1) + '.' +\
           str(octet2) + '.' +\
           str(octet3) + '.' +\
           str(octet4)

def pack_tcp_message(ip: str, port: int, num: int, body: str) -> bytes:
    return struct.pack("!III", ip_str_to_int(ip), port, num) + body.encode()

def unpack_tcp_message(msg: bytes) -> tuple[str, int, int, str]:
    unpacked = struct.unpack("!III", msg[:12])
    ip = ip_int_to_str(typing.cast(int, unpacked[0]))
    return (ip, unpacked[1], unpacked[2], msg[12:].decode())

def create_udp_socket(ip: str, port: int) -> socket.SocketType:
    soc = socket.socket(family = socket.AF_INET,
                        type = socket.SOCK_DGRAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind((ip, port))
    return soc

class MySocket:
    def __init__(self, ip: str, port: int) -> None:
        self.socket: socket.SocketType = create_udp_socket(ip, port)

    def try_connect(self, ip: str, port: int) -> None:
        _ = self.socket.sendto("Hello, world!".encode(), (ip, port))

def conectar(ip: str | None = None, port: int | None = None) -> MySocket:
    match (ip, port):
        case (None, None):
            return MySocket(LOCALHOST, DEFAULT_SERVER_PORT)

        case (str(), int()):
            rand_port = random.randrange(CLIENT_PORT_LOWER, CLIENT_PORT_HIGHER)
            soc = MySocket(LOCALHOST, rand_port)
            soc.try_connect(LOCALHOST, DEFAULT_SERVER_PORT)
            return soc

        case _:
            raise TypeError(f"Argumentos invalidos en función 'conectar', \
son de tipo ({type(ip)}, {type(port)}) y deben ser de tipo ({type(str())}, {type(int())}) \
o ({type(None)}, {type(None)})")


    
