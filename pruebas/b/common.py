import socket
import struct
import typing

LOCALHOST = "127.0.0.1"
ASKER_PORT = 51000
RESPONDER_PORT = 50000
BUFF_SIZE = 1080

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

def create_udp_socket(ip: str, port: int):
    soc = socket.socket(family = socket.AF_INET,
                     type = socket.SOCK_DGRAM)

    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind((ip, port))

    return soc

def encode_tcp_message(ip: str, port: int, num: int, body: str) -> bytes:
    msg_ip = ip_str_to_int(ip).to_bytes(4)
    msg_port = port.to_bytes(4)
    msg_num = num.to_bytes(4)
    msg_body = body.encode()
    return msg_ip + msg_port + msg_num + msg_body

def decode_tcp_message(msg: bytes) -> tuple[str, int, int, str]:
    ip = ip_int_to_str(int.from_bytes(msg[0:4]))
    port = int.from_bytes(msg[4:8])

    num = int.from_bytes(msg[8:12])
    body = msg[12:].decode()
    return (ip, port, num, body)

def pack_tcp_message(ip: str, port: int, num: int, body: str) -> bytes:
    return struct.pack("!III", ip_str_to_int(ip), port, num) + body.encode()

def unpack_tcp_message(msg: bytes) -> tuple[str, int, int, str]:
    unpacked = struct.unpack("!III", msg[:12])
    ip = ip_int_to_str(typing.cast(int, unpacked[0]))
    return (ip, unpacked[1], unpacked[2], msg[12:].decode())


