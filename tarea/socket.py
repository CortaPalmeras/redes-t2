import socket
import typing
import random

from . import tcp
from .const import *


class MySocketError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class MySocket:
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port

        self.socket: socket.SocketType = socket.socket(
            family = socket.AF_INET, type = socket.SOCK_DGRAM)

        self.socket.settimeout(DEFAULT_TIMEOUT)
        self.socket.bind((ip, port))

        self.con_ip = None
        self.con_port = 0

        self.seq_num = -1
        self.ack_num = -1


    def send_segment(self, ip: str, port:int, seq_num: int, 
                     ack_num: int, flags:int, data: str) -> int:
        ''' 
        Función de conveniencia para empaquetar y enviar datos como un
        segmento de TCP
        '''
        segment = tcp.pack_segment(self.ip, ip,
                                   self.port, port,
                                   seq_num, ack_num,
                                   flags, BUFF_SIZE, data)

        if __debug__:
            print("Paquete enviado")
            print(f"  src_port: {self.port}")
            print(f"  dst_port: {port}")
            print(f"  seq_num: {seq_num}")
            print(f"  ack_num: {ack_num}")
            print(f"  flags: {tcp.flags_to_str(flags)}") 
        return self.socket.sendto(segment, (ip, port))

    def recieve_segment(self) -> tcp.Segment:
        ''' Función de conveniencia para recibir un segmento de TCP '''
        while True:
            recieved = self.socket.recvfrom(BUFF_SIZE)
            segment_raw = recieved[0]
            ip = typing.cast(str, recieved[1][0])

            segment = tcp.unpack_segment(ip, self.ip, segment_raw)

            if segment == None:
                if __debug__:
                    print("Paquete descartado")

            else:
                if __debug__:
                    print("Paquete recibido")
                    print(f"  src_port: {segment.src_port}") 
                    print(f"  dst_port: {segment.dst_port}")
                    print(f"  seq_num: {segment.seq_num}")
                    print(f"  ack_num: {segment.ack_num}")
                    print(f"  flags: {tcp.flags_to_str(segment.flags)}") 
                return segment

    def try_connection(self, ip: str, port: int) -> None:
        ''' Hace que es socket intente conectarse a otro a traves de un 3-way handhsake '''

        if self.con_ip != None:
            raise MySocketError(f"No se puede llamar a '{self.try_connection.__name__}' con un socket conectado")

        while True:
            seq_num = random.randrange(0, 1 << 32)

            segment = self.send_segment(ip, port, seq_num, 0, SYN, '')

            try:
                segment = self.recieve_segment()
            except TimeoutError:
                continue

            if segment.flags != (SYN | ACK) \
                or segment.ack_num != seq_num + 1:
                continue

            self.seq_num = seq_num + 1
            self.ack_num = segment.seq_num + 1
            self.con_ip = segment.src_ip
            self.con_port = segment.src_port

            _ = self.send_segment(ip, port, self.seq_num, self.ack_num, ACK, '')

            if __debug__:
                print("Conección establecida")
            break

    def wait_connection(self) -> None:
        ''' Hace que es socket espere una conección, realiza un 3-way handhsake '''
        if self.con_ip != None:
            raise MySocketError(f"No se puede llamar a '{self.wait_connection.__name__}' con un socket conectado")

        tries: dict[tuple[str, int], tuple[int, int]] = dict()

        while True:
            try:
                segment = self.recieve_segment()
            except TimeoutError:
                continue

            if segment.flags == SYN:
                # si recibo SYN devuelvo SYN + ACK y lo añado a la lista de intentos
                seq_num = random.randrange(0, 1 << 32)
                ack_num = segment.seq_num + 1
                _ = self.send_segment(segment.src_ip, segment.src_port, seq_num,
                                      ack_num, SYN | ACK, '')

                tries[(segment.src_ip, segment.src_port)] = (seq_num + 1, ack_num)

            elif segment.flags & ACK \
                and (segment.src_ip, segment.src_port) in tries.keys():
                # si recibo un ACK, la fuente debe estár en la lista de intentos

                seq_num, ack_num = tries[segment.src_ip, segment.src_port]

                if segment.seq_num != ack_num:
                    # si el numero de segmento no calza con el esperado 
                    # se envia un ack vacío con el numero esperado
                    _ = self.send_segment(segment.src_ip, segment.src_port,
                                          seq_num, ack_num, ACK, "")
                    continue

                self.con_ip = segment.src_ip
                self.con_port = segment.src_port
                self.seq_num = seq_num
                self.ack_num = ack_num

                break

        if __debug__:
            print("Conección establecida")


    def recieve_all(self) -> str:
        ''' El socket recibe datos y los concatena hasta recibir una string vacía '''
        if self.con_ip == None:
            raise MySocketError(f"No se puede llamar a '{self.recieve_all.__name__}' con un socket desconectado")

        res: list[str] = list()

        while True:
            try:
                segment = self.recieve_segment()
            except TimeoutError:
                continue

            if segment.src_ip != self.con_ip \
                or segment.src_port != self.con_port:
                if __debug__:
                    print("Dirección incorrecta")
                    print(f"segment: {segment.src_ip}, self: {self.con_ip}")
                    print(f"segment: {segment.src_port}, self: {self.port}")
                continue

            if segment.flags & FIN:
                return ''.join(res)

            if segment.seq_num != self.ack_num:
                if __debug__: print("numero de secuencia incorrecto")
                _ = self.send_segment(self.con_ip, self.con_port,
                                      self.seq_num, self.ack_num, ACK, "")
                continue

            self.ack_num += 1
            _ = self.send_segment(self.con_ip, self.con_port,
                                  self.seq_num, self.ack_num, ACK, "")

            if segment.data == '':
                return ''.join(res)
            else:
                res.append(segment.data)



    def send_all(self, msg: str):
        ''' 
        El mensaje se separa en varios segmentos y se envían de manera segura utilizando
        stop-and-wait, al terminar envía una string vacía
        '''
        if self.con_ip == None:
            raise MySocketError(f"Can't call '{self.send_all.__name__}' with a disconnected socket")

        part_len = BUFF_SIZE - tcp.HEADER_SIZE_BITS
        parts: list[str] = [msg[i * part_len: (i+1) * part_len] for i in range((len(msg) // part_len) + 1)]
        parts.append('')
        resend_final = 0

        for part in parts:
            while True:
                _ = self.send_segment(self.con_ip, self.con_port, 
                                      self.seq_num, self.ack_num, ACK, part)

                try:
                    segment = self.recieve_segment()
                except TimeoutError:
                    if __debug__: print("Reenvio por timeout")
                    if part == '':
                        resend_final += 1
                        if resend_final > 100:
                            break
                    continue

                if segment.src_ip != self.con_ip \
                    or segment.src_port != self.con_port:
                    if __debug__:
                        print("Dirección incorrecta")
                        print(f"segment: {segment.src_ip}, self: {self.con_ip}")
                        print(f"segment: {segment.src_port}, self: {self.port}")
                    continue

                if segment.flags & FIN:
                    break

                if segment.ack_num == self.seq_num + 1:
                    self.seq_num += 1
                    break

    def end_connection(self) -> None:
        ''' 
        Se cierra la conección
        '''
        if self.con_ip == None:
            raise MySocketError(f"No se puede llamar a '{self.end_connection.__name__}' con un socket desconectado")

        while True:
            _ = self.send_segment(self.con_ip, self.con_port, 
                                0, 0, FIN, '')
            try:
                segment = self.recieve_segment()
            except TimeoutError:
                continue
            
            if segment.flags & FIN:
                break



