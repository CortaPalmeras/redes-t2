
### Prueba de UDP con conección poco confiable

Para simular conección poco confiable utilizar el comando:

```bash
sudo tc qdisc add dev lo root netem loss random 30%
```

Para retornar la red a su estado original utilizar:

```bash
sudo tc qdisc delete dev lo root netem
```

