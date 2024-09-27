from common import *

soc = create_udp_socket(LOCALHOST, RESPONDER_PORT)

msg, addr = soc.recvfrom(BUFF_SIZE)
msg_ip, msg_port, msg_num, msg_body = decode_tcp_message(msg)

print(f"[Recieved message]\n\
Number: {msg_num} \n\
From adress: {addr[0]}:{addr[1]}\n\
With return address: {msg_ip}:{msg_port}\n\
Content:\n{msg_body}")

ret = encode_tcp_message(LOCALHOST, RESPONDER_PORT, msg_num + 1, 'ACK')
_ = soc.sendto(ret,(msg_ip, msg_port))


