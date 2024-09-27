import socket as skt

IP = "127.0.0.1"
PORT = 12321
BUFF_SIZE = 1080

soc = skt.socket(family = skt.AF_INET,
                 type = skt.SOCK_DGRAM)

soc.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
soc.bind((IP, PORT))

recieved_nums = [False for _ in range(100)]
recieved_count = 0
repeated_count = 0
invalid_count = 0

aaa = ('a' * 100)

try:
    while True:
        msg, _ = soc.recvfrom(BUFF_SIZE)

        txt = msg.decode()
        if len(txt) <= 100:
            invalid_count += 1
            continue

        aas = txt[-100:]
        if (aas != aaa):
            invalid_count += 1
            continue

        try:
            num = int(txt[:-100])

        except ValueError:
            invalid_count += 1
            continue

        if (0 <= num and num < 100):
            if (recieved_nums[num]):
                repeated_count += 1

            recieved_nums[num] = True
            recieved_count += 1

            
        else:
            invalid_count += 1
            continue

except KeyboardInterrupt:
    print("\r", end="")

    print(f"recieved:\n\
    {recieved_count} total packages\n\
    {repeated_count} repeated packages\n\
    {invalid_count} invalid packages")
   
    soc.close()
