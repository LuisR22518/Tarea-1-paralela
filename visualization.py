from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
from matplotlib import animation

from game_of_life import GameOfLife


def _make_figure(game: GameOfLife, title: str):
    aspect = game.cols / game.rows
    fig_h = 6
    fig_w = max(4, fig_h * aspect)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    img = ax.imshow(
        game.get_state(),
        cmap="binary",
        interpolation="nearest",
        vmin=0,
        vmax=1,
    )
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title)
    fig.tight_layout()
    return fig, ax, img


def animate(
    game: GameOfLife,
    steps: int = 200,
    interval: int = 80,
    title: str = "Juego de la Vida",
    save_path: Optional[str] = None,
    show: bool = True,
) -> animation.FuncAnimation:
    fig, ax, img = _make_figure(game, title)
    gen_text = ax.text(
        0.02, 0.97, "",
        transform=ax.transAxes,
        color="red",
        fontsize=10,
        verticalalignment="top",
    )

    def update(_frame):
        game.step()
        img.set_data(game.get_state())
        gen_text.set_text(f"Generación: {game.generation}  |  Vivas: {game.alive_count}")
        return img, gen_text

    anim = animation.FuncAnimation(
        fig,
        update,
        frames=steps,
        interval=interval,
        blit=False,
        repeat=False,
    )

    if save_path is not None:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix.lower() == ".gif":
            anim.save(path, writer="pillow", fps=max(1, 1000 // interval))
        else:
            anim.save(path, fps=max(1, 1000 // interval))
        print(f"[visualization] Animación guardada en {path}")

    if show:
        plt.show()
    else:
        plt.close(fig)

    return anim


def snapshot_sequence(
    game: GameOfLife,
    steps: int,
    output_dir: str,
    stride: int = 1,
    title: str = "Juego de la Vida",
) -> None:

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fig, ax, img = _make_figure(game, title)

    for i in range(steps + 1):
        if i % stride == 0:
            img.set_data(game.get_state())
            ax.set_title(f"{title} — generación {game.generation}")
            fig.canvas.draw()
            fig.savefig(out_dir / f"gen_{i:04d}.png", dpi=100)
        if i < steps:
            game.step()

    plt.close(fig)
    print(f"[visualization] {steps // stride + 1} imágenes guardadas en {out_dir}")
