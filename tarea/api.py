import random

from .socket import MySocket
from .const import *

def conectar(ip: str | None = None, port: int | None = None) -> MySocket:
    match (ip, port):
        case (None, None):
            soc = MySocket(LOCALHOST, DEFAULT_SERVER_PORT)
            soc.wait_connect()
            return soc

        case (str(), int()):
            rand_port = random.randrange(CLIENT_PORT_LOWER, CLIENT_PORT_HIGHER)
            soc = MySocket(LOCALHOST, rand_port)
            soc.try_connect(LOCALHOST, DEFAULT_SERVER_PORT)
            return soc

        case _:
            raise TypeError(f"Argumentos invalidos en función 'conectar', \
son de tipo ({type(ip)}, {type(port)}) y deben ser de tipo ({type(str())}, {type(int())}) \
o ({type(None)}, {type(None)})")

def enviar(socket: MySocket, msg: str):
    pass

def recibir(socket: MySocket, msg: str):
    pass

def cerrar(socker):
    pass
