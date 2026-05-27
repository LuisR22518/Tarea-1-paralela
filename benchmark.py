from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Dict, List, Sequence

import matplotlib.pyplot as plt
import numpy as np

from game_of_life import GameOfLife


@dataclass
class TimingResult:
    size: int
    cells: int
    avg_seconds: float
    parallel: bool

    @property
    def avg_ms(self) -> float:
        return self.avg_seconds * 1000.0


@dataclass
class BenchmarkReport:
    results: Dict[str, List[TimingResult]] = field(default_factory=dict)

    def add(self, mode: str, result: TimingResult) -> None:
        self.results.setdefault(mode, []).append(result)

    def sizes(self, mode: str) -> np.ndarray:
        return np.array([r.size for r in self.results[mode]], dtype=np.int64)

    def cells(self, mode: str) -> np.ndarray:
        return np.array([r.cells for r in self.results[mode]], dtype=np.float64)

    def times_ms(self, mode: str) -> np.ndarray:
        return np.array([r.avg_ms for r in self.results[mode]], dtype=np.float64)


class PerformanceProfiler:

    def __init__(self, repetitions: int = 50, warmup: int = 5, seed: int = 0) -> None:
        self.repetitions = repetitions
        self.warmup = warmup
        self.seed = seed

    def time_single(self, size: int, parallel: bool = True) -> TimingResult:
        sim = GameOfLife(size, size, seed=self.seed, parallel=parallel)
        sim.run(self.warmup)
        t0 = perf_counter()
        sim.run(self.repetitions)
        dt = perf_counter() - t0
        return TimingResult(
            size=size,
            cells=size * size,
            avg_seconds=dt / self.repetitions,
            parallel=parallel,
        )

    def time_many(self, sizes: Sequence[int], parallel: bool = True,
                  mode_label: str = "") -> List[TimingResult]:
        tag = f"[{mode_label}]" if mode_label else ""
        print(f"\n--- Profilando {tag} ---")
        header = f"{'Grilla':>10} | {'Celdas':>10} | {'ms / iter':>12}"
        print(header)
        print("-" * len(header))
        out: List[TimingResult] = []
        for n in sizes:
            r = self.time_single(n, parallel=parallel)
            out.append(r)
            print(f"{n:>4}x{n:<4} | {r.cells:>10.0f} | {r.avg_ms:>12.4f}")
        return out


def _theoretical_curves(cells: np.ndarray, t_ms: np.ndarray) -> Dict[str, np.ndarray]:
    anchor_n, anchor_t = cells[0], t_ms[0]
    return {
        "O(n)":       anchor_t * (cells / anchor_n),
        "O(n log n)": anchor_t * (cells * np.log2(cells)) / (anchor_n * np.log2(anchor_n)),
        "O(n^2)":     anchor_t * (cells / anchor_n) ** 2,
    }


def plot_complexity(report: BenchmarkReport, out_dir: Path,
                    mode: str = "paralelo") -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    cells = report.cells(mode)
    t_ms = report.times_ms(mode)
    curves = _theoretical_curves(cells, t_ms)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(cells, t_ms, marker="o", linewidth=2, label="Empirico")
    for name, curve in curves.items():
        ax.plot(cells, curve, linestyle="--", alpha=0.7, label=name)
    ax.set(xlabel="Celdas (n = filas x columnas)",
           ylabel="Tiempo por iteracion (ms)",
           title="Rendimiento del Juego de la Vida (escala lineal)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "tiempo_lineal.png", dpi=120)
    plt.close(fig)

    # Figura 2: escala log-log
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.loglog(cells, t_ms, marker="o", linewidth=2, label="Empirico")
    for name, curve in curves.items():
        ax.loglog(cells, curve, linestyle="--", alpha=0.7, label=name)
    ax.set(xlabel="Celdas (n)  [log]",
           ylabel="Tiempo por iteracion (ms)  [log]",
           title="Rendimiento del Juego de la Vida (escala log-log)")
    ax.grid(which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "tiempo_loglog.png", dpi=120)
    plt.close(fig)

    slope = np.polyfit(np.log(cells), np.log(t_ms), 1)[0]
    print(f"\nPendiente log-log estimada: {slope:.3f} (≈ exponente de complejidad)")
    print(f"Figuras guardadas en: {out_dir.resolve()}")


def plot_speedup_comparison(report: BenchmarkReport, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    cells = report.cells("paralelo")
    t_par = report.times_ms("paralelo")
    t_seq = report.times_ms("secuencial")
    speedup = t_seq / t_par

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    axes[0].loglog(cells, t_seq, marker="o", linewidth=2, label="Secuencial")
    axes[0].loglog(cells, t_par, marker="s", linewidth=2, label="Paralelo")
    axes[0].set(xlabel="Celdas (n)  [log]",
                ylabel="Tiempo por iteracion (ms)  [log]",
                title="Tiempos: paralelo vs secuencial")
    axes[0].grid(which="both", alpha=0.3)
    axes[0].legend()

    axes[1].semilogx(cells, speedup, marker="o", color="darkgreen", linewidth=2)
    axes[1].axhline(1.0, color="gray", linestyle="--", alpha=0.6,
                    label="Sin aceleracion")
    axes[1].set(xlabel="Celdas (n)  [log]",
                ylabel="Speedup (t_seq / t_par)",
                title="Aceleracion del kernel paralelo")
    axes[1].grid(which="both", alpha=0.3)
    axes[1].legend()

    fig.tight_layout()
    fig.savefig(out_dir / "comparacion_paralelismo.png", dpi=120)
    plt.close(fig)

    print("\n--- Tabla comparativa ---")
    print(f"{'Grilla':>10} | {'Seq (ms)':>10} | {'Par (ms)':>10} | {'Speedup':>8}")
    print("-" * 48)
    for s, ms, mp, sp in zip(report.sizes("paralelo"), t_seq, t_par, speedup):
        print(f"{s:>4}x{s:<4} | {ms:>10.4f} | {mp:>10.4f} | {sp:>7.2f}x")


def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Profiler de rendimiento del Juego de la Vida."
    )
    p.add_argument("--sizes", type=int, nargs="+",
                   default=[32, 64, 128, 256, 512, 1024],
                   help="Lados N de las grillas NxN a evaluar.")
    p.add_argument("--reps", type=int, default=50,
                   help="Numero de iteraciones medidas por tamano.")
    p.add_argument("--warmup", type=int, default=5,
                   help="Iteraciones de warmup (no se cronometran).")
    p.add_argument("--out", type=str, default="resultados",
                   help="Directorio de salida para las graficas.")
    p.add_argument("--compare", action="store_true",
                   help="Tambien evalua el kernel secuencial y genera el speedup.")
    p.add_argument("--seed", type=int, default=0,
                   help="Semilla del generador para reproducibilidad.")
    return p


def main() -> None:
    args = _build_argparser().parse_args()
    out_dir = Path(args.out)
    profiler = PerformanceProfiler(repetitions=args.reps, warmup=args.warmup,
                                   seed=args.seed)
    report = BenchmarkReport()

    for r in profiler.time_many(args.sizes, parallel=True, mode_label="paralelo"):
        report.add("paralelo", r)
    plot_complexity(report, out_dir, mode="paralelo")

    if args.compare:
        for r in profiler.time_many(args.sizes, parallel=False, mode_label="secuencial"):
            report.add("secuencial", r)
        plot_speedup_comparison(report, out_dir)


if __name__ == "__main__":
    main()
