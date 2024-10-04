import tarea
import sys

if len(sys.argv) != 2:
    print(f"uso: {sys.argv[0]} <archivo salida>")
    exit(1)

soc = tarea.conectar()

with open(sys.argv[1], 'w') as file:
    print(f"{file.write(tarea.recibir(soc))} bytes escritos en el archivo {sys.argv[1]}")


tarea.cerrar(soc)
