from __future__ import annotations

import numpy as np


BLOCK = np.array(
    [[1, 1],
     [1, 1]],
    dtype=np.uint8,
)

BEEHIVE = np.array(
    [[0, 1, 1, 0],
     [1, 0, 0, 1],
     [0, 1, 1, 0]],
    dtype=np.uint8,
)


BLINKER = np.array(
    [[1, 1, 1]],
    dtype=np.uint8,
)

TOAD = np.array(
    [[0, 1, 1, 1],
     [1, 1, 1, 0]],
    dtype=np.uint8,
)

BEACON = np.array(
    [[1, 1, 0, 0],
     [1, 1, 0, 0],
     [0, 0, 1, 1],
     [0, 0, 1, 1]],
    dtype=np.uint8,
)

PULSAR = np.array(
    [[0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
     [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
     [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
     [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
     [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
     [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
     [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0]],
    dtype=np.uint8,
)

GLIDER = np.array(
    [[0, 1, 0],
     [0, 0, 1],
     [1, 1, 1]],
    dtype=np.uint8,
)

LWSS = np.array(
    [[0, 1, 0, 0, 1],
     [1, 0, 0, 0, 0],
     [1, 0, 0, 0, 1],
     [1, 1, 1, 1, 0]],
    dtype=np.uint8,
)


CATALOG = {
    "block": BLOCK,
    "beehive": BEEHIVE,
    "blinker": BLINKER,
    "toad": TOAD,
    "beacon": BEACON,
    "pulsar": PULSAR,
    "glider": GLIDER,
    "lwss": LWSS,
}


def get(name: str) -> np.ndarray:
    key = name.strip().lower()
    if key not in CATALOG:
        disponibles = ", ".join(sorted(CATALOG))
        raise KeyError(f"Patrón desconocido '{name}'. Disponibles: {disponibles}")
    return CATALOG[key]
