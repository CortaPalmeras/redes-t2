import socket
import typing
import random

from .tcp import TCPSegment, pack_tcp_segment, unpack_tcp_segment, flags_to_str
from .const import *

class MySocket:
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port

        self.socket: socket.SocketType = socket.socket(
            family = socket.AF_INET, type = socket.SOCK_DGRAM)
        self.socket.bind((ip, port))

        self.cwnd = BUFF_SIZE

    def recieve_segment(self) -> TCPSegment:
        while True:
            recieved = self.socket.recvfrom(self.cwnd)
            segment_raw = recieved[0]
            ip = typing.cast(str, recieved[1][0])

            segment = unpack_tcp_segment(ip, self.ip, segment_raw)

            if segment == None:
                if __debug__:
                    print("Paquete descartado")

            else:
                if __debug__:
                    print("Paquete recibido--- ")
                    print(f"  src_port: {segment.src_port}") 
                    print(f"  dst_port: {segment.dst_port}")
                    print(f"  seq_num: {segment.seq_num}")
                    print(f"  ack_num: {segment.ack_num}")
                    print(f"  flags: {flags_to_str(segment.flags)}") 
                    print(f"  cwnd: {segment.cwnd}")
                    print(f"  data: {segment.data}")
                    print("Fin de los datos")

                return segment

    def send_segment(self, ip: str, port:int, seq_num: int, 
                     ack_num: int, flags:int, data: str) -> int:
        segment = pack_tcp_segment(self.ip, ip,
                                   self.port, port,
                                   seq_num, ack_num,
                                   flags, self.cwnd, data)

        print(f"{flags_to_str(flags)} enviado")
        return self.socket.sendto(segment, (ip, port))

    def wait_connect(self) -> None:
        print("Esperando conección")

        segment = self.recieve_segment()
        if segment.flags != SYN:
            print("Flags invalidas")
            return

        seq_num = random.randrange(0, 1 << 32)
        _ = self.send_segment(segment.src_ip, segment.src_port, 
                              seq_num, segment.seq_num + 1, SYN | ACK, '')

        segment = self.recieve_segment()
        if segment.flags != ACK:
            print("Flags invalidas")
            return

        segment = self.recieve_segment()
        if segment.flags != ACK:
            print("Flags invalidas")
            return

        print(segment.data)


    def try_connect(self, ip: str, port: int) -> None:
        print("intentando conectar")

        seq_num = random.randrange(0, 1 << 32)
        segment = self.send_segment(ip, port, seq_num, 0, SYN, '')

        segment = self.recieve_segment()
        if segment.flags != (SYN | ACK) and segment.ack_num != seq_num + 1:
            print("Flags invalidas")
            return

        seq_num += 1
        _ = self.send_segment(ip, port, seq_num, segment.seq_num + 1, ACK, '')

        seq_num += 1
        _ = self.send_segment(ip, port, seq_num, segment.seq_num + 1, ACK, 'Conección establecida!')
        print("Conección establecida!")
