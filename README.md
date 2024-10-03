
# Tarea 2 - Redes

Esta tarea fue hecha en python utilizando modulos de la librería estandar,
por lo que no es necesario instalar dependencias adicionales, recomiendo usar 
linux para ejecutarla ya que solo la he probado en Debian, la versión de 
python que utilicé para probar la tarea es la 3.11.2.


## Como ejecutar

Además de la librería, incluí algunos archivos ejecutables que sirven para probar
la tarea, para realizar el test del enunciado (enviar un archivo grande de
un lado a otro sin perdidas) se pueden utilizar los siguientes comandos:

Para simular conección poco confiable yo utilicé este comando:
```bash
sudo tc qdisc add dev lo root netem loss random 30%
```

Para crear un archivo grande con caracteres aleatorios se puede usar el 
siguiente comando, el primer argumento es el nombre del achivo y el segundo
es el tamaño deseado (en Kb):
```bash
python3 crear_archivo_grande.py in.txt 5000
```

Luego, los siguientes dos comandos se deben ejecutar en terminales separadas,
la flag `-OO` se puede quitar si se desea ver los logs completos, pero advierto
que es un monton de texto:
```bash
python3 -OO receptor.py out.txt
python3 -OO transmisor.py in.txt
```

Para comparar el archivo de entrada con el de salida se puede utilizar el
comando de unix `diff`, si este no arroja ningun output significa que los 
dos archivos son iguales:
```bash
diff in.txt out.txt
```


Finalmente, para retornar la red a su estado original se puede usar:
```bash
sudo tc qdisc delete dev lo root netem
```

## El codigo

La tarea tiene esta estructura:

```

```


