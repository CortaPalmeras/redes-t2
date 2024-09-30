import socket
import random
import struct
import array
import typing

LOCALHOST = "127.0.0.1"
DEFAULT_SERVER_PORT = 8081
BUFF_SIZE = 1024

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


def flags_to_str(flags: int) -> str:
    res = ''
    if flags & CWR:
        res += 'CWR,'
    if flags & ECE:
        res += 'ECE,'
    if flags & URG:
        res += 'URG,'
    if flags & ACK:
        res += 'ACK,'
    if flags & PSH:
        res += 'PSH,'
    if flags & RST:
        res += 'RST,'
    if flags & SYN:
        res += 'SYN,'
    if flags & FIN:
        res += 'FIN,'

    if res != '':
        return res[:-1]

    return res


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
                     src_port: int, dst_port: int, 
                     seq_num: int, ack_num: int, 
                     flags: int, window: int, data: str) -> bytes:
    """
    Construye un segmento de TCP acorde a la especificación, sin incluir opciones.
    """
    header_no_checksum = struct.pack("!HHIIBBH",
                                     src_port, dst_port,
                                     seq_num,
                                     ack_num,
                                     (5 << 4), flags, window)

    header = header_no_checksum + (0).to_bytes(4) # checksum y urgent pointer

    byte_data = data.encode()

    pseudo_header = build_pseudo_header(src_ip, dst_ip, len(header) + len(byte_data))

    segment_checksum = checksum(pseudo_header + header + byte_data)

    header = header_no_checksum + segment_checksum.to_bytes(2) + (0).to_bytes(2)

    return header + byte_data

class TCPSegment(typing.NamedTuple):
    src_port: int
    dst_port: int
    seq_num: int
    ack_num: int
    flags: int
    window: int
    data: str

def unpack_tcp_segment(src_ip: str, dst_ip:str, segment: bytes) -> TCPSegment | None:
    """
    Lee los datos de un segmento TCP en formato de bytes, compara el lo compara con 
    el checksum y extrae los siguientes datos en este orden:
     - Puerto fuente
     - Puerto de destino
     - Número de secuencia
     - Número de ACK
     - TCP Flags
     - Tamaño de la ventana
     - Datos del paquete
    """

    header_no_checksum = segment[:16]
    pseudo_header = build_pseudo_header(src_ip, dst_ip, len(segment))
    computed_checksum = checksum(pseudo_header + header_no_checksum
                                 + (0).to_bytes(2) + segment[18:])

    recieved_checksum = int.from_bytes(segment[16:18])

    if (recieved_checksum != computed_checksum):
        if __debug__:
            print(f"recieved_checksum: {recieved_checksum}")
            print(f"computed_checksum: {computed_checksum}")
        return None

    (src_port, dst_port,
    seq_num, ack_num,
    data_off, flags, window) = struct.unpack("!HHIIBBH", header_no_checksum)

    data = segment[(data_off >> 4):].decode()

    if __debug__:
        print(f"seq_num: {seq_num}")
        print(f"ack_num: {ack_num}")
        print(f"flags: {flags_to_str(flags)}")
        print(f"data: {data}")

    return TCPSegment(src_port, dst_port, seq_num, ack_num, flags, window, data)


class MySocket:
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port

        self.socket: socket.SocketType = socket.socket(
            family = socket.AF_INET, type = socket.SOCK_DGRAM)
        self.socket.bind((ip, port))

    def wait_connect(self):
        segment, addr = self.socket.recvfrom(BUFF_SIZE)
        print("Paquete recibido")

        segment_data = unpack_tcp_segment(addr[0], self.ip, segment)

        if segment_data == None:
            print("Paquete botado")
            return

        elif segment_data.flags & SYN:
            print("SYN recibido")

        send_segment = pack_tcp_segment(self.ip, addr[0], 
                                   self.port, segment_data.src_port,
                                   random.randrange(0, 1 << 32), 
                                   segment_data.seq_num + 1,
                                   SYN | ACK, BUFF_SIZE, '')

        _ = self.socket.sendto(send_segment, (addr, segment_data.src_port))
        print("SYN + ACK enviado")

        
    def try_connect(self, ip: str, port: int) -> None:
        seq_num = random.randrange(0, 1 << 32)

        segment = pack_tcp_segment(self.ip, ip, self.port, port,
                                   seq_num, 0,
                                   SYN, BUFF_SIZE, '')

        _ = self.socket.sendto(segment, (ip, port))
        print("SYN enviado")

        segment, (ip, port) = self.socket.recvfrom(BUFF_SIZE)
        print("respuesta recibida")

        segment_data = unpack_tcp_segment(ip, self.ip, segment)

        if segment_data == None:
            print("Paquete botado")
            return

        if (segment_data.flags & SYN) and (segment_data.flags & ACK)\
            and segment_data.ack_num == seq_num + 1:
            print("SYN + ACK recibido")



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

