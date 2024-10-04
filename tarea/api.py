import random

from .socket import MySocket
from .const import *

def conectar(ip: str | None = None, port: int | None = None) -> MySocket:
    match (ip, port):
        case (None, None):
            soc = MySocket(LOCALHOST, DEFAULT_SERVER_PORT)
            soc.wait_connection()
            return soc

        case (str(), int()):
            rand_port = random.randrange(CLIENT_PORT_LOWER, CLIENT_PORT_HIGHER)
            soc = MySocket(LOCALHOST, rand_port)
            soc.try_connection(LOCALHOST, DEFAULT_SERVER_PORT)
            return soc

        case _:
            raise TypeError(f"Argumentos invalidos en función 'conectar', \
son de tipo ({type(ip)}, {type(port)}) y deben ser de tipo ({type(str())}, {type(int())}) \
o ({type(None)}, {type(None)})")

def enviar(socket: MySocket, msg: str):
    socket.send_all(msg)

def recibir(socket: MySocket) -> str:
    return socket.recieve_all()

def cerrar(socket: MySocket):
    socket.end_connection()
