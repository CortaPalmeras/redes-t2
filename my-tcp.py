import socket as skt
import typing

IP = "127.0.0.1"
DEFAULT_SERVER_PORT = 11111
BUFF_SIZE = 1080

next_usable_port = DEFAULT_SERVER_PORT

def get_server_socket():
    soc = skt.socket(family = skt.AF_INET,
                     type = skt.SOCK_DGRAM)

    soc.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
    soc.bind((IP, next_usable_port))

    global next_usable_port
    next_usable_port += 1


class MyTcpServer(typing.NamedTuple):
    


def conectar(ip: str | None = None, port: int | None = None) -> MyTcpServer:
    if ip == None and port == None:
        soc.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
        soc.bind((IP, PORT))


    elif isinstance(ip, str) and isinstance(port, int):

    else:
        raise TypeError(f"Argumentos invalidos en función 'conectar', \
son de tipo ({type(ip)}, {type(port)}) y deben ser de tipo (str, int) o (None, None)")


