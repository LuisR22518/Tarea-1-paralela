# Tarea 1 — Juego de la Vida de Conway

Implementacion en Python del Juego de la Vida de Conway para el curso de
Programacion Paralela y Distribuida (LEAD University).

## Requisitos

- Python 3.9 o superior
- Librerias listadas en `requirements.txt`

## Instalacion

```bash
python -m pip install -r requirements.txt
```

## Como ejecutar

### Demo animada de un patron clasico

```bash
python main.py demo --pattern *tipo de patron* --size *tamaño del encuadre* --steps *numero de pasos*
```

Patrones disponibles: `block`, `beehive`, `blinker`, `toad`, `beacon`,
`pulsar`, `glider`, `lwss`, `random`.

### Guardar la animacion como GIF

```bash
python main.py demo --pattern pulsar --size 32 --steps 60 --save salida.gif --no-show
```

### Benchmark de rendimiento

```bash
python main.py benchmark --sizes 32 64 128 256 512 1024 --reps 50
```

Comparar paralelo vs secuencial:

```bash
python main.py benchmark --sizes 64 128 256 512 1024 --reps 50 --compare
```

Los resultados (graficas) se guardan en la carpeta `resultados/`.
