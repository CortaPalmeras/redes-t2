import sys
import tarea

if len(sys.argv) != 2:
    print(f'uso: {sys.argv[0]} <archivo>')
    exit(1)

with open(sys.argv[1], 'rb') as file:
    msg = file.read().decode()

soc = tarea.conectar(tarea.LOCALHOST, tarea.DEFAULT_SERVER_PORT)

tarea.enviar(soc, msg)

soc.socket.close()
