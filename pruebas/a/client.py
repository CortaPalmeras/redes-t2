import socket as skt

IP = "127.0.0.1"
PORT = 12321
BUFF_SIZE = 1080

soc = skt.socket(family = skt.AF_INET,
                 type = skt.SOCK_DGRAM)

for i in range(100):
    msg = str(i) + ('a' * 100)

    _ = soc.sendto(msg.encode(), (IP, PORT))

soc.close()
