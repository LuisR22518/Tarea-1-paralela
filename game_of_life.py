
from __future__ import annotations

from typing import Optional, Tuple

import numpy as np
from numba import njit, prange


@njit(cache=True, parallel=True, fastmath=True)
def _step_kernel_parallel(grid: np.ndarray, out: np.ndarray) -> None:
    rows, cols = grid.shape
    for i in prange(rows):
        up = (i - 1) % rows
        down = (i + 1) % rows
        for j in range(cols):
            left = (j - 1) % cols
            right = (j + 1) % cols
            neighbors = (
                grid[up, left] + grid[up, j] + grid[up, right]
                + grid[i, left] + grid[i, right]
                + grid[down, left] + grid[down, j] + grid[down, right]
            )
            alive = grid[i, j] == 1
            if alive and (neighbors == 2 or neighbors == 3):
                out[i, j] = 1
            elif (not alive) and neighbors == 3:
                out[i, j] = 1
            else:
                out[i, j] = 0


@njit(cache=True, fastmath=True)
def _step_kernel_sequential(grid: np.ndarray, out: np.ndarray) -> None:
    rows, cols = grid.shape
    for i in range(rows):
        up = (i - 1) % rows
        down = (i + 1) % rows
        for j in range(cols):
            left = (j - 1) % cols
            right = (j + 1) % cols
            neighbors = (
                grid[up, left] + grid[up, j] + grid[up, right]
                + grid[i, left] + grid[i, right]
                + grid[down, left] + grid[down, j] + grid[down, right]
            )
            alive = grid[i, j] == 1
            if alive and (neighbors == 2 or neighbors == 3):
                out[i, j] = 1
            elif (not alive) and neighbors == 3:
                out[i, j] = 1
            else:
                out[i, j] = 0


class GameOfLife:
    def __init__(
        self,
        rows: int,
        cols: int,
        initial_state: Optional[np.ndarray] = None,
        density: float = 0.25,
        seed: Optional[int] = None,
        parallel: bool = True,
    ) -> None:
        if rows <= 0 or cols <= 0:
            raise ValueError("Las dimensiones del tablero deben ser positivas.")

        self.rows = rows
        self.cols = cols
        self.generation = 0
        self._kernel = _step_kernel_parallel if parallel else _step_kernel_sequential

        if initial_state is None:
            rng = np.random.default_rng(seed)
            self._grid = (rng.random((rows, cols)) < density).astype(np.uint8)
        else:
            initial_state = np.asarray(initial_state, dtype=np.uint8)
            if initial_state.shape != (rows, cols):
                raise ValueError(
                    f"initial_state tiene forma {initial_state.shape}, "
                    f"se esperaba {(rows, cols)}."
                )
            self._grid = (initial_state != 0).astype(np.uint8)

        self._buffer = np.empty_like(self._grid)

    def step(self) -> None:
        self._kernel(self._grid, self._buffer)
        self._grid, self._buffer = self._buffer, self._grid
        self.generation += 1

    def run(self, steps: int) -> None:
        if steps < 0:
            raise ValueError("El numero de pasos no puede ser negativo.")
        for _ in range(steps):
            self.step()

    def get_state(self) -> np.ndarray:
        return self._grid.copy()

    @property
    def shape(self) -> Tuple[int, int]:
        return self._grid.shape

    @property
    def alive_count(self) -> int:
        return int(self._grid.sum())

    def clear(self) -> None:
        self._grid.fill(0)
        self.generation = 0

    def set_cells(self, pattern: np.ndarray, top: int = 0, left: int = 0) -> None:
        pattern = np.asarray(pattern, dtype=np.uint8)
        h, w = pattern.shape
        if top + h > self.rows or left + w > self.cols:
            raise ValueError("El patron no cabe en la posicion indicada.")
        self._grid[top:top + h, left:left + w] = (pattern != 0).astype(np.uint8)

    def __repr__(self) -> str:
        return (
            f"GameOfLife(rows={self.rows}, cols={self.cols}, "
            f"generation={self.generation}, alive={self.alive_count})"
        )
