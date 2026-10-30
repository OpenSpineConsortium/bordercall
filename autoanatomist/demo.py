"""The annealing demo: a network of the smoke run's widths trained on one measurement, with a snapshot
every few steps of what its mask branch is given and of the width it measures on held-out CTs from
the CT alone, drawn as one figure with a slider over the steps (notebooks/anneal_demo.ipynb runs it
in Colab).

    python -m autoanatomist.demo demo.html --record demo.json    # from bordercall's root; needs plotly, which no requirements file pins

The run takes smoke.py's phantoms, seeds, learning rate, batches and schedule (lambda from 0 to 1
over steps 23 to 82 of 150, then w from 1 to 0 over steps 68 to 127), but trains one measurement,
the upper end-plate's width (Panjabi's EPWu), with the naming layer off, where smoke.py trains all
seven with it on; its network is train.train's to the bit for that measurement with the naming
layer off (tests/test_anneal_demo.py). Each snapshot holds the last step's lambda and w, what the
mask branch was given at that lambda (ladder.degrade on one training crop: the target vertebra's
mask fading into every vertebra's, blurring and giving way to a soft threshold of the CT), and the
network's two end-plate landmarks and its width on every held-out crop, read by model.ct_only, the
path a raw CT takes, with no mask anywhere. The reference is the oracle's width and its two points,
read off each held-out vertebra's mask.

A demonstration on phantoms, not a result: minutes of training on a CPU, nothing kept, no real CT.
The held-out crops are placed as the training crops are, from the oracle's frame turned and moved at
random; placing a crop from the CT alone (crops.from_found) is not measured yet.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import os
import platform
import sys
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple

import jax.numpy as jnp
import numpy as np
import optax
from flax import nnx
from scipy import ndimage

from . import gates, ladder, smoke, train
from .model import Config, Model

KEY = "endplate"                    # Panjabi's EPWu, the upper end-plate's width
EVERY = 5                           # steps between snapshots
# Okabe and Ito's colours, apart for colour-blind readers: the oracle's reference, the network's
# reading from the CT alone, and the mask branch with its weight w.
BLUE, ORANGE, GREEN = "#0072B2", "#D55E00", "#009E73"
BONE = "#D9CFB8"
CT_WINDOW_HU = (-300.0, 1300.0)     # the grey scale of the CT cut under the mask branch's input
LAM, W = "\u03bb", "w"                 # lambda, as the figure prints it


@dataclass
class Snapshot:
    """The network after `step` steps: the last step's w and lambda (the first step's before any),
    the mask branch's input then, the display crop's middle sagittal cut of the target channel
    (Y, Z), and from the CT alone the two end-plate landmarks on every held-out crop (H, 2, 3), in
    the crop's millimetres, and the width between them (H,)."""
    step: int
    w: float
    lam: float
    given: np.ndarray
    points: np.ndarray
    widths: np.ndarray


@dataclass
class Demo:
    """A run's snapshots and what they are read against: each held-out crop's CT in HU (H, X, Y, Z)
    and its level, the oracle's two points and width there, the crop's axis ticks in millimetres,
    w and lambda at every step, every step's loss and the seconds the run took; and the display
    crop's CT in HU on the cut the snapshots' mask input is taken on (Y, Z)."""
    snapshots: List[Snapshot]
    given_ct: np.ndarray
    hu: np.ndarray
    levels: List[str]
    reference_points: np.ndarray
    reference_widths: np.ndarray
    ticks: List[np.ndarray]
    w: np.ndarray
    lam: np.ndarray
    losses: List[float]
    seconds: float

    @property
    def steps(self) -> int:
        return len(self.losses)

    def error_mm(self, k: int) -> float:
        """The mean absolute error of snapshot k's widths against the oracle's, over the held-out crops."""
        return float(np.nanmean(np.abs(self.snapshots[k].widths - self.reference_widths)))

    def typical(self) -> int:
        """The held-out crop whose error after the last step is the median of all of them (the lower
        of the two middle ones for an even count): the figure's vertebra unless one is named, so
        that it shows neither the best reading nor the worst."""
        errors = np.abs(self.snapshots[-1].widths - self.reference_widths)
        return int(np.argsort(errors, kind="stable")[(len(errors) - 1) // 2])


def examples(cfg: Config) -> Tuple[train.Examples, train.Examples]:
    """The smoke run's phantoms for cfg: its training columns and its held-out ones."""
    ex = train.make_examples(cfg, smoke.TRAIN_SPINES, smoke.COUNT, seed=smoke.SEEDS["train_examples"],
                             starts=smoke.TRAIN_STARTS, **smoke.PHANTOM)
    held = train.make_examples(cfg, smoke.HELD_SPINES, smoke.COUNT, seed=smoke.SEEDS["held_examples"],
                               starts=smoke.HELD_STARTS, **smoke.PHANTOM)
    return ex, held


def given_cut(ex: train.Examples, i: int, lam: float, spacing: float) -> np.ndarray:
    """What the mask branch reads of crop i at lambda: the target channel after ladder.degrade, on
    the crop's middle sagittal cut, (Y, Z)."""
    out = ladder.degrade(jnp.asarray(ex.masks[i:i + 1]), jnp.asarray(ex.hu[i:i + 1]), jnp.float32(lam),
                         spacing_mm=spacing)
    return np.asarray(out[0, out.shape[1] // 2, :, :, 0])


def ct_cut(ex: train.Examples, i: int) -> np.ndarray:
    """Crop i's CT in HU on the cut given_cut takes, (Y, Z)."""
    return np.asarray(ex.hu[i, ex.hu.shape[1] // 2, :, :, 0])


def display_crop(ex: train.Examples) -> int:
    """The training crop whose mask channel the figure shows: the first phantom's middle vertebra."""
    first = ex.spines()[0]
    return int(first[len(first) // 2])


class Snapper:
    """Takes snapshots of one model: its CT-only reading of the held-out crops, jitted once, and the
    mask branch's input on the display crop."""

    def __init__(self, ex: train.Examples, held: train.Examples, spacing: float):
        self.ex, self.spacing = ex, spacing
        self.display = display_crop(ex)
        self.hu = jnp.asarray(held.hu)
        self.read = nnx.jit(lambda m, hu: m.ct_only(hu))

    def take(self, model: Model, step: int, w: float, lam: float) -> Snapshot:
        out = self.read(model, self.hu)
        return Snapshot(step=step, w=float(w), lam=float(lam),
                        given=given_cut(self.ex, self.display, lam, self.spacing),
                        points=np.asarray(out["points"]), widths=np.asarray(out["values"])[:, 0])


def anneal(ex: train.Examples, held: train.Examples, cfg: Config, steps: int, every: int = EVERY,
           log_every: int = 0) -> Tuple[Model, List[Snapshot], List[float]]:
    """train.train with the naming layer off, step for step (the same model, optimiser, batches and
    schedule at smoke.py's batch, rate and seed, so the network is train.train's to the bit), with
    a snapshot before the first step, after every `every` steps and after the last."""
    groups = ex.spines()
    model = Model(cfg, nnx.Rngs(smoke.SEEDS["run"]))
    opt = nnx.Optimizer(model, optax.adamw(smoke.LR), wrt=nnx.Param)
    schedule = ladder.Schedule(steps)
    step = train.make_step(None, 0)
    rng = np.random.default_rng(smoke.SEEDS["run"])
    snapper = Snapper(ex, held, cfg.spacing)
    snapshots, losses = [snapper.take(model, 0, *schedule.at(0))], []
    for s in range(steps):
        pick = rng.choice(len(groups), size=smoke.SPINES_PER_BATCH, replace=len(groups) < smoke.SPINES_PER_BATCH)
        batch = train.batch_of(ex, np.concatenate([groups[g] for g in pick]))
        w, lam = schedule.at(s)
        total, _ = step(model, opt, batch, jnp.float32(w), jnp.float32(lam))
        losses.append(float(total))
        if (s + 1) % every == 0 or s + 1 == steps:
            snapshots.append(snapper.take(model, s + 1, w, lam))
        if log_every and ((s + 1) % log_every == 0 or s + 1 == steps):
            print(progress(snapshots[-1], held, s + 1, steps), flush=True)
    return model, snapshots, losses


def progress(snap: Snapshot, held: train.Examples, step: int, steps: int) -> str:
    error = float(np.nanmean(np.abs(snap.widths - held.values[:, 0])))
    return "step %d of %d: w %.2f, lambda %.2f, the width's mean error on the held-out CTs %.1f mm" % (
        step, steps, snap.w, snap.lam, error)


def run(steps: int = smoke.STEPS, every: int = EVERY, cfg: Optional[Config] = None, log_every: int = 25) -> Demo:
    """The demo: the phantoms, the annealed training with its snapshots, and what they are read against."""
    cfg = cfg or Config(keys=(KEY,))
    t0 = time.time()
    ex, held = examples(cfg)
    _, snapshots, losses = anneal(ex, held, cfg, steps, every, log_every)
    schedule = ladder.Schedule(steps)
    w, lam = np.array([schedule.at(s) for s in range(steps)]).T
    return Demo(snapshots=snapshots, given_ct=ct_cut(ex, display_crop(ex)), hu=held.hu[..., 0],
                levels=[r.level for r in held.readings],
                reference_points=held.targets, reference_widths=held.values[:, 0],
                ticks=held.frames[0].axis_ticks(), w=w, lam=lam, losses=losses, seconds=time.time() - t0)


def surface(demo: Demo, vertebra: int):
    """The held-out crop's CT as plotly's isosurface at the ladder's bone level (gates.BONE_HU),
    lightly smoothed against the phantom's noise: a raw CT, no mask in it."""
    import plotly.graph_objects as go
    x, y, z = np.meshgrid(*demo.ticks, indexing="ij")
    hu = ndimage.gaussian_filter(np.asarray(demo.hu[vertebra], np.float32), 1.0)
    return go.Isosurface(x=x.ravel(), y=y.ravel(), z=z.ravel(), value=hu.ravel(), isomin=gates.BONE_HU,
                         isomax=gates.BONE_HU, surface_count=1, caps=dict(x_show=False, y_show=False, z_show=False),
                         colorscale=[[0.0, BONE], [1.0, BONE]], showscale=False, opacity=0.45,
                         lighting=dict(ambient=0.55, diffuse=0.7, specular=0.15), hoverinfo="skip",
                         name="the CT at %d HU, no mask" % gates.BONE_HU, showlegend=True)


def chord(points: np.ndarray, colour: str, name: str):
    import plotly.graph_objects as go
    return go.Scatter3d(x=points[:, 0], y=points[:, 1], z=points[:, 2], mode="lines+markers", name=name,
                        line=dict(color=colour, width=9), marker=dict(color=colour, size=5))


def ct_under(demo: Demo):
    """The display crop's CT on the mask input's cut, in grey: what the CT branch reads there all along."""
    import plotly.graph_objects as go
    return go.Heatmap(z=demo.given_ct.T, x=demo.ticks[1], y=demo.ticks[2], zmin=CT_WINDOW_HU[0],
                      zmax=CT_WINDOW_HU[1], colorscale="gray", showscale=False, hoverinfo="skip")


def given(snap: Snapshot, ticks: List[np.ndarray]):
    """The mask branch's input on the display crop's sagittal cut, in green over the CT, drawn at the
    weight w the network gives the branch, so it fades out as the network comes to read the CT alone."""
    import plotly.graph_objects as go
    clear, full = "rgba(0,158,115,0)", "rgba(0,158,115,0.85)"
    return go.Heatmap(z=snap.given.T, x=ticks[1], y=ticks[2], zmin=0.0, zmax=1.0, colorscale=[[0.0, clear], [1.0, full]],
                      showscale=False, opacity=max(snap.w, 0.0), hoverinfo="skip")


def schedule_marks(snap: Snapshot):
    import plotly.graph_objects as go
    return go.Scatter(x=[snap.step, snap.step], y=[snap.lam, snap.w], mode="markers", showlegend=False,
                      marker=dict(color=["#000000", GREEN], size=10), hoverinfo="skip")


def width_line(demo: Demo, k: int, vertebra: int):
    import plotly.graph_objects as go
    shown = demo.snapshots[:k + 1]
    return go.Scatter(x=[s.step for s in shown], y=[float(s.widths[vertebra]) for s in shown], mode="lines+markers",
                      line=dict(color=ORANGE, width=3), marker=dict(size=5), name="the network, from the CT alone",
                      showlegend=False)


def title(demo: Demo, k: int, vertebra: int) -> str:
    snap = demo.snapshots[k]
    return ("After %d of %d steps: %s %.2f, %s %.2f. %s's end-plate width %.1f mm from the CT alone, "
            "the reference %.1f mm; mean error over the %d held-out vertebrae %.1f mm" % (
                snap.step, demo.steps, LAM, snap.lam, W, snap.w, demo.levels[vertebra], snap.widths[vertebra],
                demo.reference_widths[vertebra], len(demo.reference_widths), demo.error_mm(k)))


def figure(demo: Demo, vertebra: Optional[int] = None):
    """The demo drawn with a slider over the snapshots. Left: one held-out vertebra's CT as a bone
    isosurface with no mask, the network's end-plate width from the CT alone (orange) beside the
    oracle's (blue). Right, from the top: what the mask branch is given at the snapshot's lambda,
    in green over a training crop's CT and drawn at its weight w; lambda and w over the run; the
    width over the run against the reference."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    vertebra = demo.typical() if vertebra is None else vertebra
    fig = make_subplots(rows=3, cols=2, column_widths=[0.56, 0.44], row_heights=[0.4, 0.22, 0.38],
                        specs=[[{"type": "scene", "rowspan": 3}, {"type": "xy"}], [None, {"type": "xy"}],
                               [None, {"type": "xy"}]],
                        horizontal_spacing=0.07, vertical_spacing=0.13,
                        subplot_titles=("", "A training vertebra: what the mask branch is given (green), at its weight %s" % W,
                                        "The schedule: %s (black) and %s (green)" % (LAM, W),
                                        "The end-plate width (mm) of the held-out vertebra on the left"))
    fig.add_trace(surface(demo, vertebra), row=1, col=1)
    fig.add_trace(chord(demo.reference_points[vertebra], BLUE, "the reference (the oracle, from the mask)"), row=1, col=1)
    fig.add_trace(chord(demo.snapshots[0].points[vertebra], ORANGE, "the network, from the CT alone"), row=1, col=1)
    fig.add_trace(ct_under(demo), row=1, col=2)
    fig.add_trace(given(demo.snapshots[0], demo.ticks), row=1, col=2)
    add_schedule(fig, demo)
    fig.add_trace(schedule_marks(demo.snapshots[0]), row=2, col=2)
    add_reference_width(fig, demo, vertebra)
    fig.add_trace(width_line(demo, 0, vertebra), row=3, col=2)
    moving = [2, 4, 7, 9]
    fig.frames = [go.Frame(name=str(k), traces=moving, layout=dict(title_text=title(demo, k, vertebra)),
                           data=[chord(s.points[vertebra], ORANGE, "the network, from the CT alone"),
                                 given(s, demo.ticks), schedule_marks(s), width_line(demo, k, vertebra)])
                  for k, s in enumerate(demo.snapshots)]
    lay_out(fig, demo, vertebra)
    fig.update_layout(title_text=title(demo, 0, vertebra), sliders=[slider(demo)], updatemenus=[buttons()])
    return fig


def add_schedule(fig, demo: Demo) -> None:
    """lambda and w over the run, counted as the slider counts: at step s the values the s-th update
    used, and at step 0 the first update's, so each snapshot's dots lie on the curves."""
    import plotly.graph_objects as go
    steps = np.arange(demo.steps + 1)
    for values, line in ((demo.lam, dict(color="#000000", width=2)), (demo.w, dict(color=GREEN, width=2, dash="dot"))):
        fig.add_trace(go.Scatter(x=steps, y=np.concatenate([values[:1], values]), mode="lines", line=line,
                                 showlegend=False, hoverinfo="skip"), row=2, col=2)


def add_reference_width(fig, demo: Demo, vertebra: int) -> None:
    import plotly.graph_objects as go
    ref = float(demo.reference_widths[vertebra])
    fig.add_trace(go.Scatter(x=[0, demo.steps], y=[ref, ref], mode="lines", showlegend=False,
                             line=dict(color=BLUE, width=2, dash="dash"), hoverinfo="skip"), row=3, col=2)


def width_range(demo: Demo, vertebra: int) -> List[float]:
    values = [float(s.widths[vertebra]) for s in demo.snapshots] + [float(demo.reference_widths[vertebra])]
    return [min(values) - 3.0, max(values) + 3.0]


def lay_out(fig, demo: Demo, vertebra: int) -> None:
    axis = dict(backgroundcolor="#FFFFFF", showbackground=True, gridcolor="#DDDDDD")
    fig.update_scenes(aspectmode="data", camera=dict(eye=dict(x=0.35, y=1.7, z=0.8)),
                      xaxis=dict(title="x, right (mm)", **axis), yaxis=dict(title="y, anterior (mm)", **axis),
                      zaxis=dict(title="z, up the column (mm)", **axis))
    fig.update_xaxes(title_text="posterior to anterior (mm)", constrain="domain", row=1, col=2)
    beside = fig.get_subplot(1, 2).xaxis.plotly_name.replace("axis", "")
    fig.update_yaxes(title_text="up the column (mm)", scaleanchor=beside, scaleratio=1.0, row=1, col=2)
    fig.update_xaxes(range=[0, demo.steps], row=2, col=2)
    fig.update_yaxes(range=[-0.05, 1.05], row=2, col=2)
    fig.update_xaxes(range=[0, demo.steps], title_text="step", row=3, col=2)
    fig.update_yaxes(range=width_range(demo, vertebra), title_text="mm", row=3, col=2)
    fig.update_layout(height=760, margin=dict(l=10, r=10, t=90, b=10), plot_bgcolor="#FFFFFF",
                      title=dict(font=dict(size=14), x=0.01),
                      legend=dict(x=0.01, y=0.02, bgcolor="rgba(255,255,255,0.8)"))


def slider(demo: Demo) -> dict:
    moves = [dict(method="animate", label=str(s.step),
                  args=[[str(k)], dict(mode="immediate", frame=dict(duration=0, redraw=True),
                                       transition=dict(duration=0))])
             for k, s in enumerate(demo.snapshots)]
    return dict(steps=moves, active=0, x=0.1, len=0.88, y=-0.02, currentvalue=dict(prefix="After step "),
                pad=dict(t=30))


def buttons() -> dict:
    play = dict(label="Play", method="animate",
                args=[None, dict(frame=dict(duration=250, redraw=True), transition=dict(duration=0), fromcurrent=True)])
    pause = dict(label="Pause", method="animate",
                 args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")])
    return dict(type="buttons", buttons=[play, pause], direction="left", x=0.0, y=-0.02, xanchor="left",
                yanchor="top", pad=dict(t=30, r=10), showactive=False)


def versions() -> dict:
    """What ran a demo: Python, the packages its numbers depend on, JAX's device and the CPUs it may use."""
    import jax
    found = {"python": platform.python_version(), "device": str(jax.devices()[0]),
             "cpus": len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count()}
    for name in ("jax", "jaxlib", "flax", "optax", "numpy", "scipy"):
        found[name] = importlib.metadata.version(name)
    return found


def record(demo: Demo, cfg: Config) -> dict:
    """A run's numbers for its record file: the settings, each snapshot's lambda, w and mean error over
    the held-out vertebrae, each held-out vertebra's reference and its reading after the last step,
    the vertebra the figure shows unless told otherwise, the seconds from making the phantoms to the
    last snapshot, and what ran it."""
    last = demo.snapshots[-1]
    return {"measurement": KEY, "steps": demo.steps, "widths": list(cfg.widths), "crop": list(cfg.shape),
            "spacing_mm": cfg.spacing, "learning_rate": smoke.LR, "seeds": dict(smoke.SEEDS),
            "snapshots": [{"step": s.step, "w": s.w, "lambda": s.lam, "mean_error_mm": demo.error_mm(k)}
                          for k, s in enumerate(demo.snapshots)],
            "held_out": [{"level": level, "reference_mm": float(ref), "read_mm": float(read),
                          "error_mm": float(abs(read - ref))}
                         for level, ref, read in zip(demo.levels, demo.reference_widths, last.widths)],
            "shown": demo.typical(), "seconds": demo.seconds, "ran_on": versions()}


def widths_of(text: str) -> Tuple[int, ...]:
    """--widths 8,16,32: the encoders' channels at each of the three scales."""
    widths = tuple(int(part) for part in text.split(","))
    if len(widths) != 3 or min(widths) < 1:
        raise argparse.ArgumentTypeError("three positive widths, as 8,16,32")
    return widths


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(prog="python -m autoanatomist.demo",
                                     description="Train the demo's network and draw its anneal as an HTML page.")
    parser.add_argument("page", help="the HTML page to write")
    parser.add_argument("--steps", type=int, default=smoke.STEPS, help="training steps (%(default)s, the smoke run's)")
    parser.add_argument("--widths", type=widths_of, default=Config(keys=(KEY,)).widths,
                        help="the encoders' widths (16,32,64, the smoke run's)")
    parser.add_argument("--record", help="also write the run's numbers here as JSON")
    args = parser.parse_args(argv[1:])
    if importlib.util.find_spec("plotly") is None:      # said before the minutes of training, not after
        print("the figure needs plotly, which no requirements file pins: pip install plotly", file=sys.stderr)
        return 2
    cfg = Config(keys=(KEY,), widths=args.widths)
    demo = run(args.steps, EVERY, cfg)
    figure(demo).write_html(args.page, include_plotlyjs=True, auto_play=False)
    if args.record:
        with open(args.record, "w") as f:
            json.dump(record(demo, cfg), f, indent=1)
            f.write("\n")
    print("%s: %d snapshots over %d steps in %.0f s" % (args.page, len(demo.snapshots), demo.steps, demo.seconds))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
