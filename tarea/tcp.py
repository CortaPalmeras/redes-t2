import socket
import struct
import array
import typing

from .const import *

HEADER_SIZE_WORDS = 5
HEADER_SIZE_BYTES = HEADER_SIZE_WORDS * 4
HEADER_SIZE_BITS = HEADER_SIZE_BYTES * 8

def flags_to_str(flags: int) -> str:
    res = ''
    if flags & CWR:
        res += 'CWR + '
    if flags & ECE:
        res += 'ECE + '
    if flags & URG:
        res += 'URG + '
    if flags & ACK:
        res += 'ACK + '
    if flags & PSH:
        res += 'PSH + '
    if flags & RST:
        res += 'RST + '
    if flags & SYN:
        res += 'SYN + '
    if flags & FIN:
        res += 'FIN + '

    if res != '':
        return res[:-3]

    return res

class Segment(typing.NamedTuple):
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    seq_num: int
    ack_num: int
    flags: int
    window: int
    data: str

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

def pack_segment(src_ip: str, dst_ip: str,
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


def unpack_segment(src_ip: str, dst_ip:str, segment: bytes) -> Segment | None:
    """
    Lee los bytes de un segmento TCP, revisa que calce el checksum y extrae los datos
    del header.
    """
    if len(segment) < HEADER_SIZE_BYTES:
        return None

    header_no_checksum = segment[:16]
    pseudo_header = build_pseudo_header(src_ip, dst_ip, len(segment))
    computed_checksum = checksum(pseudo_header + header_no_checksum
                                 + (0).to_bytes(2) + segment[18:])

    recieved_checksum = int.from_bytes(segment[16:18])

    if (recieved_checksum != computed_checksum):
        return None

    (src_port, dst_port,
    seq_num, ack_num,
    data_off, flags, window) = typing.cast(tuple[int,int,int,int,int,int,int], 
                                           struct.unpack("!HHIIBBH", header_no_checksum))

    data_off = data_off >> 4
    data = segment[(data_off) * 4:].decode()

    return Segment(src_ip, dst_ip, src_port, dst_port, seq_num, ack_num, flags, window, data)

