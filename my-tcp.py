import socket as skt
import typing

IP = "127.0.0.1"
DEFAULT_SERVER_PORT = 11111
BUFF_SIZE = 1080

next_usable_port = DEFAULT_SERVER_PORT


def conectar(ip: str | None = None, port: int | None = None) -> MyTcpServer:
    if ip == None and port == None:

    elif isinstance(ip, str) and isinstance(port, int):


    else:
        raise TypeError(f"Argumentos invalidos en función 'conectar', \
son de tipo ({type(ip)}, {type(port)}) y deben ser de tipo (str, int) o (NoneType, NoneType)")


