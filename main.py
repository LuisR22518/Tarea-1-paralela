

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from game_of_life import GameOfLife
import patterns
from visualization import animate
from benchmark import (
    BenchmarkReport,
    PerformanceProfiler,
    plot_complexity,
    plot_speedup_comparison,
)


def _new_game_from_args(args) -> GameOfLife:
    """Instancia un GameOfLife segun el patron solicitado."""
    if args.pattern == "random":
        return GameOfLife(args.size, args.size,
                          density=args.density, seed=args.seed)

    sim = GameOfLife(args.size, args.size)
    sim.clear()
    pat = patterns.get(args.pattern)
    row = (args.size - pat.shape[0]) // 2
    col = (args.size - pat.shape[1]) // 2
    sim.set_cells(pat, top=row, left=col)
    return sim


def run_demo(args) -> None:
    sim = _new_game_from_args(args)
    print(f"[demo] {sim}")
    print(f"[demo] patron='{args.pattern}'  pasos={args.steps}")
    animate(
        sim,
        steps=args.steps,
        interval=args.interval,
        title=f"Juego de la Vida - {args.pattern} ({args.size}x{args.size})",
        save_path=args.save,
        show=not args.no_show,
    )


def run_benchmark(args) -> None:
    out_dir = Path(args.out)
    profiler = PerformanceProfiler(repetitions=args.reps,
                                   warmup=args.warmup,
                                   seed=args.seed)
    report = BenchmarkReport()

    for r in profiler.time_many(args.sizes, parallel=True, mode_label="paralelo"):
        report.add("paralelo", r)
    plot_complexity(report, out_dir, mode="paralelo")

    if args.compare:
        for r in profiler.time_many(args.sizes, parallel=False,
                                    mode_label="secuencial"):
            report.add("secuencial", r)
        plot_speedup_comparison(report, out_dir)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Juego de la Vida de Conway (Tarea 1)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # demo
    p_demo = sub.add_parser("demo", help="Demo animada del juego.")
    p_demo.add_argument("--pattern", default="glider",
                        choices=list(patterns.CATALOG) + ["random"])
    p_demo.add_argument("--size", type=int, default=64)
    p_demo.add_argument("--steps", type=int, default=200)
    p_demo.add_argument("--interval", type=int, default=80,
                        help="Ms entre frames.")
    p_demo.add_argument("--density", type=float, default=0.25,
                        help="Solo para --pattern random.")
    p_demo.add_argument("--seed", type=int, default=None)
    p_demo.add_argument("--save", type=str, default=None,
                        help="Ruta de salida (.gif o .mp4).")
    p_demo.add_argument("--no-show", action="store_true")
    p_demo.set_defaults(func=run_demo)

    # benchmark
    p_bench = sub.add_parser("benchmark", help="Mide rendimiento.")
    p_bench.add_argument("--sizes", type=int, nargs="+",
                         default=[32, 64, 128, 256, 512, 1024])
    p_bench.add_argument("--reps", type=int, default=50)
    p_bench.add_argument("--warmup", type=int, default=5)
    p_bench.add_argument("--out", type=str, default="resultados")
    p_bench.add_argument("--seed", type=int, default=0)
    p_bench.add_argument("--compare", action="store_true",
                         help="Compara paralelo vs secuencial.")
    p_bench.set_defaults(func=run_benchmark)

    return parser


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
