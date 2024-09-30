import socket
import random
import struct
import typing
import array

LOCALHOST = "127.0.0.1"
DEFAULT_SERVER_PORT = 8081
BUFF_SIZE = 1080

CLIENT_PORT_LOWER = 2 ** 15
CLIENT_PORT_HIGHER = 2 ** 16

CWR = 0b10000000
ECE = 0b01000000
URG = 0b00100000
ACK = 0b00010000
PSH = 0b00001000
RST = 0b00000100
SYN = 0b00000010
FIN = 0b00000001

def checksum(data: bytes) -> int:
    """ 
    Calcula el checksum de un paquete como se describe
    en la especificación de del protocolo TCP.
    """
    if len(data) % 2 != 0:
        data += b'\0'

    res = sum(array.array("H", data))
    res = (res >> 16) + (res & 0xffff)
    res += res >> 16

    return (~res) & 0xffff

def build_pseudo_header(src_ip: str, dst_ip: str, size: int):
    return struct.pack("!4s4sBBH",
                       socket.inet_aton(src_ip),
                       socket.inet_aton(dst_ip),
                       0, socket.IPPROTO_TCP, size)

def pack_tcp_segment(src_ip: str, dst_ip: str,
                    src_port: int, dst_port: int, sec_num: int, 
                    ack_num: int, flags: int, window: int,
                    data: str) -> bytes:
    """
    Construye un segmento de TCP acorde a la especificación, sin incluir opciones.
    """
    header_no_checksum = struct.pack("!HHIIBBHHH",
                                     src_port, dst_port,
                                     sec_num,
                                     ack_num,
                                     (5 << 4), flags, window)

    header = header_no_checksum + (0).to_bytes(4) # checksum y urgent pointer

    byte_data = data.encode()

    pseudo_header = build_pseudo_header(src_ip, dst_ip, len(header) + len(byte_data))

    segment_checksum = checksum(pseudo_header + header + byte_data)

    header = header_no_checksum + segment_checksum.to_bytes(2) + (0).to_bytes(2)

    return header + byte_data


def unpack_tcp_segment(src_ip: str, dst_ip:str, segment: bytes)\
                       -> tuple[int, int, int, int, int, str] | None:
    header_no_checksum = segment[:16]

    pseudo_header = build_pseudo_header(src_ip, dst_ip, len(segment))

    recieved_checksum = int.from_bytes(segment[16:18])
    computed_checksum = checksum(pseudo_header + header_no_checksum + (0).to_bytes(2) + segment[18:])
    
    if __debug__: 
        print(f"recieved_checksum: {recieved_checksum}")
        print(f"computed_checksum: {computed_checksum}")

    if (recieved_checksum != computed_checksum):
        return None

    (src_port, __, sec_num, ack_num,
     data_off, flags, window) = struct.unpack("!HHIIBBHHH", header_no_checksum)

    data = segment[(data_off >> 4):].decode()

    return (src_port, sec_num, ack_num, flags, window, data)


def create_udp_socket(ip: str, port: int) -> socket.SocketType:
    soc = socket.socket(family = socket.AF_INET,
                        type = socket.SOCK_DGRAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind((ip, port))
    return soc

class MySocket:
    def __init__(self, ip: str, port: int) -> None:
        self.socket: socket.SocketType = create_udp_socket(ip, port)

    def wait_connect(self):
        _ = self.socket.recv(1024)

    def try_connect(self, ip: str, port: int) -> None:
        byte_n = self.socket.sendto(syn1.encode(), (ip, port))

        if byte_n ==

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

