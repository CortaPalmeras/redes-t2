from common import *

soc = create_udp_socket(LOCALHOST, ASKER_PORT)

msg = encode_tcp_message(LOCALHOST, ASKER_PORT, 12345, "Hola, mundo!")
_ = soc.sendto(msg, (LOCALHOST, RESPONDER_PORT))

ret, addr = soc.recvfrom(BUFF_SIZE)
ret_ip, ret_port, ret_num, ret_body = unpack_tcp_message(ret)

print(f"[Recieved message]\n\
Number: {ret_num} \n\
From adress: {addr[0]}:{addr[1]}\n\
With return address: {ret_ip}:{ret_port}\n\
Content:\n{ret_body}")

soc.close()
