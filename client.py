import tarea

soc = tarea.conectar(tarea.LOCALHOST, tarea.DEFAULT_SERVER_PORT)

soc.socket.close()
