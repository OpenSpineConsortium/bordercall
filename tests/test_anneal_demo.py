"""The annealing demo (autoanatomist/demo.py) on the sizes the model tests use: a crop of 16 by 20
by 12 voxels and two phantoms of three levels.

    python -m unittest tests.test_anneal_demo -v        # from the repository's root, in the venv

The demo's network is train.train's for its one measurement with the naming layer off, every
weight to the bit (the smoke run itself trains all seven measurements with the naming layer on).
Its snapshots fall before the first step, every few steps and after the last, each with the
schedule's w and lambda of the step just taken and the CT-only path's reading by the network after
that many steps, with each width the length between its points. demo.run reads the held-out crops
against the oracle and keeps their masks for the figure alone. Its figure, frame by frame, draws
the shown vertebra's own CT as the surface and on it that vertebra's own mask taken down the ladder
to the snapshot's lambda (ladder.degrade, pooled two voxels a side) at the opacity of w, the
network's width with its length in the legend, the schedule's dots on its curves, the width line
up to the slider's step and the title's numbers, at a fixed size, the vertebra on the left and two
panels of one height stacked beside it, one frame per snapshot and a slider over them (where
plotly is installed, as it is in Colab). The command says before it trains that it needs plotly,
writes the page in a box of fixed width set in from the edges and, asked to, the run's record and
the run itself with its network's weights, which --load draws again for any held-out vertebra
without training, run as python -m autoanatomist.demo as the notebook runs it. With --test the kept
network, restored to the reading of its last snapshot, reads test sets drawn after training (new
draws, each differing from the training phantoms as it says) from the CT alone, and the page sets
each vertebra against its reference and each set's mean error, with an interval that resamples
whole columns, against always guessing the training phantoms' mean width.

The notebook that runs it in Colab (notebooks/anneal_demo.ipynb) is kept with no outputs and asks
Colab for a T4. Its setup cell's functions, run against a stand-in for Colab's modules, read a
missing secret as none, sign in with GitHub's device flow (the code shown large beside a button
that copies it and opens GitHub's page, the token returned and never printed, a refusal or a
decline falling back to the ZIP), clone shallow and sparse with the token handed to git through a
credential helper and nowhere else, the three folders it checks out being all the demo imports,
fall back to the ZIP with git's words when no clone holds the demo, unpack a ZIP as GitHub makes
one and install the four packages bordercall pins with no restart; and prepare(), run on stand-ins
for Colab's GPU and CPU images, installs the GPU build of the pinned jaxlib for the CUDA version
whose build the image carries after taking the other versions' builds out, installs nothing when
the pins are there, asks for plotly before anything slow, and leaves JAX on the CPU, saying why,
when JAX does not start on the GPU in a child process. No cell imports JAX or bordercall: the run
and show cells train and draw in a child, python -m autoanatomist.demo, which inherits the
session's JAX_PLATFORMS, and the test cell tests the run the run cell kept.
"""
from __future__ import annotations

import argparse
import ast
import functools
import importlib.machinery
import io
import json
import os
import pickle
import runpy
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
import urllib.error
import urllib.parse
import warnings
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

try:
    import jax
    import jax.numpy as jnp
    from flax import nnx
    HAVE_JAX = True
except ImportError:                                               # pragma: no cover
    HAVE_JAX = False

try:
    import plotly  # noqa: F401
    HAVE_PLOTLY = True
except ImportError:                                               # pragma: no cover
    HAVE_PLOTLY = False

STEPS, EVERY = 7, 3
# The figure's traces, in the order demo.figure adds them.
CT, MASK, REFERENCE, NETWORK, LAMBDA, WEIGHT, DOTS, REFERENCE_WIDTH, WIDTH = range(9)
NOTEBOOK = os.path.join(ROOT, "notebooks", "anneal_demo.ipynb")


def tiny_config():
    from autoanatomist.model import Config
    return Config(keys=("endplate",), widths=(4, 8, 8), shape=(16, 20, 12), spacing=6.0)


def tiny_examples(cfg):
    from autoanatomist import train as T
    ex = T.make_examples(cfg, n_spines=2, count=3, seed=1, spacing_mm=2.0)
    held = T.make_examples(cfg, n_spines=1, count=3, seed=2, spacing_mm=2.0)
    return ex, held


@functools.lru_cache(maxsize=None)
def tiny_demo():
    """One run of demo.run on the tiny sizes, which the figure's tests and the command's share."""
    from autoanatomist import demo as D
    cfg = tiny_config()
    ex, held = tiny_examples(cfg)
    with mock.patch.object(D, "examples", lambda c: (ex, held)):
        return cfg, ex, held, D.run(STEPS, EVERY, cfg, log_every=0)


@unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
class TheAnnealedRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from autoanatomist import demo as D
        cls.cfg = tiny_config()
        cls.ex, cls.held = tiny_examples(cls.cfg)
        cls.model, cls.snapshots, cls.losses = D.anneal(cls.ex, cls.held, cls.cfg, STEPS, EVERY)

    def test_the_network_is_train_trains_with_the_naming_layer_off_to_the_bit(self):
        from autoanatomist import smoke, train as T
        run = T.train(self.ex, self.cfg, STEPS, spines_per_batch=smoke.SPINES_PER_BATCH, lr=smoke.LR,
                      seed=smoke.SEEDS["run"], use_naming=False)
        mine = jax.tree.leaves(nnx.state(self.model, nnx.Param))
        theirs = jax.tree.leaves(nnx.state(run.model, nnx.Param))
        self.assertEqual(len(mine), len(theirs))
        for a, b in zip(mine, theirs):
            np.testing.assert_array_equal(np.asarray(a), np.asarray(b))
        np.testing.assert_array_equal(self.losses, [row["total"] for row in run.record])

    def test_the_snapshots_fall_before_the_first_step_every_few_steps_and_after_the_last(self):
        from autoanatomist import ladder
        self.assertEqual([s.step for s in self.snapshots], [0, 3, 6, 7])
        schedule = ladder.Schedule(STEPS)
        for snap in self.snapshots:
            self.assertEqual((snap.w, snap.lam), schedule.at(max(snap.step - 1, 0)))

    def test_every_snapshots_reading_is_the_ct_only_path_of_the_network_after_its_steps(self):
        from autoanatomist import ladder, smoke, train as T
        from autoanatomist.model import Model
        read = nnx.jit(lambda m, hu: m.ct_only(hu))
        for snap in self.snapshots:
            if snap.step == 0:
                model = Model(self.cfg, nnx.Rngs(smoke.SEEDS["run"]))
            elif snap.step == STEPS:
                model = self.model
            else:                                               # the first steps of the same run
                model = T.train(self.ex, self.cfg, snap.step, spines_per_batch=smoke.SPINES_PER_BATCH, lr=smoke.LR,
                                seed=smoke.SEEDS["run"], use_naming=False, schedule=ladder.Schedule(STEPS)).model
            np.testing.assert_array_equal(snap.points, np.asarray(read(model, jnp.asarray(self.held.hu))["points"]))
            lengths = np.linalg.norm(snap.points[:, 1] - snap.points[:, 0], axis=-1)
            np.testing.assert_allclose(snap.widths, lengths, rtol=1e-5)
            self.assertEqual(snap.points.shape, (len(self.held), 2, 3))

    def test_pooling_takes_means_over_blocks_of_two_voxels_a_side_and_leaves_an_odd_last_one_out(self):
        from autoanatomist import demo as D
        volume = np.arange(5 * 4 * 3, dtype=np.float64).reshape(5, 4, 3)
        pooled = D.pooled(volume)
        self.assertEqual(pooled.shape, (2, 2, 1))
        self.assertEqual(pooled[1, 0, 0], volume[2:4, 0:2, 0:2].mean())
        ticks = [np.arange(5.0), np.arange(4.0) * 2.0, np.arange(3.0)]
        self.assertEqual([list(t) for t in D.pooled_ticks(ticks)], [[0.5, 2.5], [1.0, 5.0], [0.5]])


@unittest.skipUnless(HAVE_JAX and HAVE_PLOTLY, "jax, flax and plotly are not all installed")
class TheFigure(unittest.TestCase):
    """The figure of vertebra 1, so that a figure drawn from vertebra 0's numbers shows."""

    @classmethod
    def setUpClass(cls):
        from autoanatomist import demo as D
        cls.cfg, cls.ex, cls.held, cls.demo = tiny_demo()
        cls.fig = D.figure(cls.demo, vertebra=1)

    def test_the_run_reads_the_held_out_crops_against_the_oracle_and_keeps_their_masks_for_the_figure(self):
        from autoanatomist import ladder
        np.testing.assert_array_equal(self.demo.hu, self.held.hu[..., 0])
        np.testing.assert_array_equal(self.demo.masks, self.held.masks)
        self.assertEqual(self.demo.spacing, self.cfg.spacing)
        np.testing.assert_array_equal(self.demo.reference_points, self.held.targets)
        np.testing.assert_array_equal(self.demo.reference_widths, self.held.values[:, 0])
        self.assertEqual(self.demo.levels, [r.level for r in self.held.readings])
        for mine, theirs in zip(self.demo.ticks, self.held.frames[0].axis_ticks()):
            np.testing.assert_array_equal(mine, theirs)
        schedule = ladder.Schedule(STEPS)
        np.testing.assert_array_equal(np.column_stack([self.demo.w, self.demo.lam]),
                                      [schedule.at(s) for s in range(STEPS)])
        self.assertEqual((self.demo.steps, [s.step for s in self.demo.snapshots]), (STEPS, [0, 3, 6, 7]))

    def test_the_mask_input_is_the_shown_vertebras_own_mask_down_the_ladder_at_lambda_pooled(self):
        from autoanatomist import demo as D, ladder
        self.assertGreater(len({snap.lam for snap in self.demo.snapshots}), 2)
        for snap in self.demo.snapshots:
            out = ladder.degrade(jnp.asarray(self.held.masks[1:2]), jnp.asarray(self.held.hu[1:2]),
                                 jnp.float32(snap.lam), spacing_mm=self.cfg.spacing)
            np.testing.assert_allclose(D.mask_values(self.demo, 1, snap.lam),
                                       D.pooled(np.asarray(out[0, ..., 0], np.float64)), rtol=1e-6)

    def test_before_the_ladder_the_mask_input_is_the_vertebras_own_mask_and_not_every_vertebras(self):
        from autoanatomist import demo as D
        target, every = self.held.masks[1, ..., 0], self.held.masks[1, ..., 1]
        self.assertFalse(np.allclose(D.pooled(target), D.pooled(every)))   # so the pooling tells the two apart
        self.assertEqual(self.demo.snapshots[0].lam, 0.0)
        np.testing.assert_allclose(D.mask_values(self.demo, 1, 0.0), D.pooled(np.asarray(target, np.float64)),
                                   atol=1e-6)

    def test_each_snapshots_dots_lie_on_the_schedules_curves(self):
        lam_curve, w_curve = self.fig.data[LAMBDA], self.fig.data[WEIGHT]
        for k, snap in enumerate(self.demo.snapshots):
            dots = self.fig.frames[k].data[2]
            self.assertEqual(list(dots.x), [snap.step, snap.step])
            self.assertAlmostEqual(lam_curve.y[list(lam_curve.x).index(snap.step)], dots.y[0])
            self.assertAlmostEqual(w_curve.y[list(w_curve.x).index(snap.step)], dots.y[1])

    def test_one_frame_and_one_slider_step_per_snapshot(self):
        self.assertEqual(len(self.fig.frames), len(self.demo.snapshots))
        steps = self.fig.layout.sliders[0].steps
        self.assertEqual([s.label for s in steps], [str(s.step) for s in self.demo.snapshots])
        self.assertEqual([s.args[0][0] for s in steps], [f.name for f in self.fig.frames])

    def test_the_frames_move_the_mask_input_and_the_networks_width_and_leave_the_ct_and_the_reference(self):
        self.assertEqual(list(self.fig.frames[0].traces), [MASK, NETWORK, DOTS, WIDTH])
        self.assertEqual([trace.type for trace in self.fig.data],
                         ["isosurface", "isosurface", "scatter3d", "scatter3d"] + ["scatter"] * 5)
        for frame, snap in zip(self.fig.frames, self.demo.snapshots):
            line = frame.data[1]
            np.testing.assert_allclose(np.column_stack([line.x, line.y, line.z]), snap.points[1])
            self.assertEqual(line.name, "the network, from the CT alone: %.1f mm" % snap.widths[1])

    def test_the_surface_is_the_shown_vertebras_own_ct_at_the_bone_level(self):
        from scipy import ndimage
        from autoanatomist import gates
        iso = self.fig.data[CT]
        self.assertFalse(np.allclose(self.demo.hu[0], self.demo.hu[1]))   # so another vertebra's CT would show
        smoothed = ndimage.gaussian_filter(np.asarray(self.demo.hu[1], np.float32), 1.0)
        np.testing.assert_array_equal(np.asarray(iso.value), smoothed.ravel())
        self.assertEqual((iso.isomin, iso.isomax), (gates.BONE_HU, gates.BONE_HU))
        for axis, ticks in zip((iso.x, iso.y, iso.z), np.meshgrid(*self.demo.ticks, indexing="ij")):
            np.testing.assert_array_equal(np.asarray(axis), ticks.ravel())

    def test_every_frame_draws_the_mask_input_on_the_vertebra_at_its_weight_whole_at_the_start(self):
        from autoanatomist import demo as D
        weights = [snap.w for snap in self.demo.snapshots]
        self.assertEqual(weights[0], 1.0)
        self.assertTrue(any(0.0 < w < 1.0 for w in weights))   # so a weight between the ends is drawn as it is
        mask = self.fig.data[MASK]
        self.assertEqual((mask.opacity, mask.isomin, mask.isomax), (D.MASK_OPACITY, 0.5, 0.5))
        for axis, ticks in zip((mask.x, mask.y, mask.z), np.meshgrid(*D.pooled_ticks(self.demo.ticks), indexing="ij")):
            np.testing.assert_array_equal(np.asarray(axis), ticks.ravel())
        self.assertEqual(tuple(mask.value), tuple(self.fig.frames[0].data[0].value))
        for frame, snap in zip(self.fig.frames, self.demo.snapshots):
            given = frame.data[0]
            self.assertAlmostEqual(given.opacity, D.MASK_OPACITY * max(snap.w, 0.0))
            np.testing.assert_allclose(np.asarray(given.value), D.mask_values(self.demo, 1, snap.lam).ravel(),
                                       atol=0.005 + 1e-9)

    def test_every_frames_width_line_runs_to_its_step_for_the_shown_vertebra(self):
        snaps = self.demo.snapshots
        self.assertFalse(np.allclose([s.widths[0] for s in snaps], [s.widths[1] for s in snaps]))
        lines = [(0, self.fig.data[WIDTH])] + [(k, frame.data[3]) for k, frame in enumerate(self.fig.frames)]
        for k, line in lines:
            self.assertEqual(list(line.x), [s.step for s in snaps[:k + 1]])
            np.testing.assert_allclose(list(line.y), [s.widths[1] for s in snaps[:k + 1]])

    def test_every_frames_title_gives_the_shown_vertebras_numbers_at_its_step(self):
        levels, refs = self.demo.levels, self.demo.reference_widths
        self.assertNotEqual(levels[0], levels[1])
        for frame, snap in zip(self.fig.frames, self.demo.snapshots):
            text = frame.layout.title.text
            self.assertIn("<b>After %d of %d steps: λ %.2f, w %.2f</b>" % (snap.step, STEPS, snap.lam, snap.w), text)
            self.assertIn("%s's end-plate width %.1f mm from the CT alone, the reference %.1f mm"
                          % (levels[1], snap.widths[1], refs[1]), text)
            self.assertTrue(text.endswith("mean error over the %d held-out vertebrae %.1f mm"
                                          % (len(refs), np.mean(np.abs(snap.widths - refs)))))
        self.assertEqual(self.fig.layout.title.text, self.fig.frames[0].layout.title.text)

    def test_the_oracles_line_is_drawn_where_the_oracle_put_it_its_length_in_the_legend(self):
        ref = self.fig.data[REFERENCE]
        np.testing.assert_allclose(np.column_stack([ref.x, ref.y, ref.z]), self.demo.reference_points[1])
        self.assertEqual(ref.name, "the reference, from the mask: %.1f mm" % self.demo.reference_widths[1])
        self.assertEqual(self.fig.data[REFERENCE_WIDTH].y[0], float(self.demo.reference_widths[1]))

    def test_unless_named_the_vertebra_shown_is_the_one_with_the_median_error_at_the_end(self):
        from autoanatomist import demo as D
        errors = np.abs(self.demo.snapshots[-1].widths - self.demo.reference_widths)
        k = self.demo.typical()
        self.assertEqual(errors[k], sorted(errors)[(len(errors) - 1) // 2])
        fig = D.figure(self.demo)
        ref = fig.data[REFERENCE]
        np.testing.assert_allclose(np.column_stack([ref.x, ref.y, ref.z]), self.demo.reference_points[k])

    def test_the_vertebra_is_on_the_left_and_the_two_panels_beside_it_are_stacked_of_one_height(self):
        from autoanatomist import demo as D
        lay = self.fig.layout
        self.assertEqual((lay.width, lay.height, lay.autosize), (D.WIDTH_PX, D.HEIGHT_PX, False))
        scene, top, bottom = lay.scene.domain, lay.yaxis.domain, lay.yaxis2.domain
        self.assertEqual(tuple(scene.y), (0.0, 1.0))
        self.assertLess(scene.x[1], lay.xaxis.domain[0])
        self.assertEqual(tuple(lay.xaxis.domain), tuple(lay.xaxis2.domain))
        self.assertAlmostEqual(top[1] - top[0], bottom[1] - bottom[0])
        self.assertEqual((top[1], bottom[0]), (scene.y[1], scene.y[0]))   # level with the vertebra's panel
        self.assertEqual({self.fig.data[i].yaxis for i in (LAMBDA, WEIGHT, DOTS)}, {"y"})
        self.assertEqual({self.fig.data[i].yaxis for i in (REFERENCE_WIDTH, WIDTH)}, {"y2"})


@unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
class TheCommand(unittest.TestCase):
    def test_without_plotly_it_says_so_before_it_trains(self):
        from autoanatomist import demo as D
        with mock.patch.dict(sys.modules, {"plotly": None}), mock.patch.object(D, "run") as run, \
                mock.patch("sys.stderr", new_callable=io.StringIO) as said:
            self.assertEqual(D.main(["demo", "out.html"]), 2)
        run.assert_not_called()
        self.assertIn("pip install plotly", said.getvalue())

    def test_the_widths_are_three_positive_numbers(self):
        from autoanatomist import demo as D
        self.assertEqual(D.widths_of("8,16,32"), (8, 16, 32))
        for wrong in ("8,16", "8,16,32,64", "0,16,32", "8,x,32"):
            with self.assertRaises((argparse.ArgumentTypeError, ValueError)):
                D.widths_of(wrong)

    def test_blocks_reach_the_run_checked_first_and_never_go_with_a_kept_run(self):
        from autoanatomist import demo as D
        with mock.patch.object(D, "run") as run, redirect_stderr(io.StringIO()) as said, \
                self.assertRaises(SystemExit) as stop:
            D.main(["demo", "out.html", "--blocks", "schedule=nonsense"])
        self.assertEqual(stop.exception.code, 2)
        self.assertIn("--blocks: schedule takes", said.getvalue())
        with mock.patch.object(D, "run") as run, redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            D.main(["demo", "out.html", "--load", "kept.pkl", "--blocks", "schedule=adaptive"])
        run.assert_not_called()

    def test_a_run_with_blocks_trains_as_a_session_and_says_so_in_its_record(self):
        from autoanatomist import demo as D
        cfg = tiny_config()
        ex, held = tiny_examples(cfg)
        with mock.patch.object(D, "examples", lambda c: (ex, held)):
            demo = D.run(STEPS, EVERY, cfg, log_every=0, blocks=" schedule=adaptive  restraint=abf ")
        self.assertEqual(demo.blocks, "schedule=adaptive restraint=abf")
        self.assertEqual([s.step for s in demo.snapshots], [s.step for s in tiny_demo()[3].snapshots])
        self.assertEqual((len(demo.w), len(demo.lam), len(demo.losses)), (STEPS, STEPS, STEPS))
        self.assertTrue(np.all(np.isfinite(demo.losses)))
        self.assertEqual(D.record(demo, cfg)["blocks"], "schedule=adaptive restraint=abf")
        self.assertEqual(D.record(tiny_demo()[3], cfg)["blocks"], "")

    @unittest.skipUnless(HAVE_PLOTLY, "plotly is not installed")
    def test_it_trains_as_told_and_writes_the_page_the_runs_record_and_the_run_itself(self):
        from autoanatomist import demo as D
        _, _, _, demo = tiny_demo()
        with tempfile.TemporaryDirectory() as out, mock.patch.object(D, "run", return_value=demo) as run, \
                redirect_stdout(io.StringIO()):
            page, numbers, kept = (os.path.join(out, name) for name in ("demo.html", "demo.json", "demo.pkl"))
            self.assertEqual(D.main(["demo", page, "--steps", "7", "--widths", "4,8,8", "--record", numbers,
                                     "--save", kept]), 0)
            self.assertGreater(os.path.getsize(page), 0)
            with open(numbers) as f:
                record = json.load(f)
            with open(kept, "rb") as f:
                again = pickle.load(f)
        (steps, every, cfg), _ = run.call_args
        self.assertEqual((steps, every, cfg.widths, cfg.keys), (7, D.EVERY, (4, 8, 8), (D.KEY,)))
        self.assertEqual((record["measurement"], record["steps"], record["widths"]), (D.KEY, STEPS, [4, 8, 8]))
        self.assertEqual([(s["step"], s["w"], s["lambda"]) for s in record["snapshots"]],
                         [(s.step, s.w, s.lam) for s in demo.snapshots])
        np.testing.assert_allclose([s["mean_error_mm"] for s in record["snapshots"]],
                                   [np.mean(np.abs(s.widths - demo.reference_widths)) for s in demo.snapshots],
                                   rtol=1e-6)
        last, held = demo.snapshots[-1], record["held_out"]
        self.assertEqual([h["level"] for h in held], demo.levels)
        np.testing.assert_allclose([h["reference_mm"] for h in held], demo.reference_widths)
        np.testing.assert_allclose([h["read_mm"] for h in held], last.widths)
        np.testing.assert_allclose([h["error_mm"] for h in held], np.abs(last.widths - demo.reference_widths),
                                   rtol=1e-6)
        self.assertEqual((record["shown"], record["seconds"]), (demo.typical(), demo.seconds))
        self.assertEqual(record["ran_on"]["jax"], jax.__version__)
        self.assertEqual(type(again).__module__, "autoanatomist.demo")
        np.testing.assert_array_equal(again.masks, demo.masks)
        for mine, theirs in zip(again.snapshots, demo.snapshots):
            self.assertEqual((mine.step, mine.w, mine.lam), (theirs.step, theirs.w, theirs.lam))
            np.testing.assert_array_equal(mine.points, theirs.points)

    @unittest.skipUnless(HAVE_PLOTLY, "plotly is not installed")
    def test_load_draws_a_kept_run_for_any_held_out_vertebra_without_training(self):
        from autoanatomist import demo as D
        _, _, _, demo = tiny_demo()
        self.assertEqual(len({"%.1f" % width for width in demo.reference_widths}), len(demo.levels))
        with tempfile.TemporaryDirectory() as out:
            kept, page = os.path.join(out, "run.pkl"), os.path.join(out, "page.html")
            with open(kept, "wb") as f:
                pickle.dump(demo, f, protocol=pickle.HIGHEST_PROTOCOL)
            with mock.patch.object(D, "run") as run, redirect_stdout(io.StringIO()) as said:
                self.assertEqual(D.main(["demo", page, "--load", kept, "--vertebra", "2", "--plotlyjs", "cdn"]), 0)
            run.assert_not_called()
            self.assertIn("it shows held-out vertebra 2, %s" % demo.levels[2], said.getvalue())
            with open(page) as f:
                text = f.read()
            self.assertIn("the reference, from the mask: %.1f mm" % demo.reference_widths[2], text)
            self.assertNotIn("the reference, from the mask: %.1f mm" % demo.reference_widths[1], text)
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as stop:
                D.main(["demo", page, "--load", kept, "--vertebra", str(len(demo.levels))])
            self.assertEqual(stop.exception.code, 2)

    def test_load_goes_with_neither_record_nor_save_and_the_vertebra_is_one_of_the_held_out(self):
        from autoanatomist import demo as D, smoke
        held = smoke.HELD_SPINES * smoke.COUNT
        for words in (["--load", "k.pkl", "--record", "r.json"], ["--load", "k.pkl", "--save", "s.pkl"],
                      ["--vertebra", str(held)], ["--vertebra", "-1"]):
            with mock.patch.object(D, "run") as run, redirect_stderr(io.StringIO()), \
                    self.assertRaises(SystemExit) as stop:
                D.main(["demo", "out.html", *words])
            self.assertEqual(stop.exception.code, 2, words)
            run.assert_not_called()

    @unittest.skipUnless(HAVE_PLOTLY, "plotly is not installed")
    def test_the_page_holds_the_figure_at_its_fixed_size_in_a_box_set_in_from_the_edges(self):
        from autoanatomist import demo as D
        _, _, _, demo = tiny_demo()
        fig = D.figure(demo, 1)
        cdn, inline = D.page(fig, "cdn"), D.page(fig, "inline")
        for text in (cdn, inline):
            self.assertTrue(text.startswith("<!DOCTYPE html>"))
            self.assertIn('<div style="width:%dpx;margin:16px auto;padding:12px;' % D.WIDTH_PX, text)
            self.assertIn("height:%dpx; width:%dpx;" % (D.HEIGHT_PX, D.WIDTH_PX), text)
        self.assertIn('src="https://cdn.plot.ly/', cdn)
        self.assertNotIn('src="https://cdn.plot.ly/', inline)
        self.assertGreater(len(inline), len(cdn) + 1_000_000)          # plotly.js itself, in the page

    def test_run_as_python_minus_m_it_runs_the_modules_own_main(self):
        """python -m runs the file as __main__, whose classes a pickle would name __main__'s: the
        command runs main from the module autoanatomist.demo, so a kept run names that module's."""
        from autoanatomist import demo as D
        with mock.patch.object(D, "main", return_value=0) as main, mock.patch.object(sys, "argv", ["demo", "x.html"]), \
                warnings.catch_warnings(), self.assertRaises(SystemExit) as stop:
            warnings.simplefilter("ignore", RuntimeWarning)       # runpy's, on a module imported already
            runpy.run_module("autoanatomist.demo", run_name="__main__")
        self.assertEqual(stop.exception.code, 0)
        main.assert_called_once_with(["demo", "x.html"])

    @unittest.skipUnless(HAVE_PLOTLY, "plotly is not installed")
    def test_as_the_notebook_runs_it_a_child_draws_a_kept_run_in_a_page(self):
        _, _, _, demo = tiny_demo()
        with tempfile.TemporaryDirectory() as out:
            kept, page = os.path.join(out, "run.pkl"), os.path.join(out, "page.html")
            with open(kept, "wb") as f:
                pickle.dump(demo, f, protocol=pickle.HIGHEST_PROTOCOL)
            child = subprocess.run([sys.executable, "-u", "-m", "autoanatomist.demo", page, "--load", kept,
                                    "--vertebra", "1", "--plotlyjs", "cdn"], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(child.returncode, 0, child.stderr)
            self.assertIn("it shows held-out vertebra 1, %s" % demo.levels[1], child.stdout)
            self.assertGreater(os.path.getsize(page), 0)


# Two small test sets on the tiny sizes, at the tiny phantoms' 2 mm.
TINY_TESTS = (("plain", {"spacing_mm": 2.0}), ("noisy", {"spacing_mm": 2.0, "noise_hu": 60.0}))
ORDER = ["T%d" % k for k in range(1, 13)] + ["L%d" % k for k in range(1, 6)]


def tiny_tests():
    from autoanatomist import demo as D
    return tuple(D.TestSet(name, "the tiny " + name, settings) for name, settings in TINY_TESTS)


@unittest.skipUnless(HAVE_JAX, "jax and flax are not installed")
class TheTestOnNewPhantoms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from autoanatomist import demo as D
        cls.cfg, cls.ex, cls.held, cls.demo = tiny_demo()
        cls.results = list(D.tested(cls.demo, tiny_tests(), columns=2))

    def test_the_run_keeps_its_network_whose_reading_is_the_last_snapshots(self):
        from autoanatomist import demo as D
        self.assertEqual(self.demo.cfg, self.cfg)
        for leaf in jax.tree.leaves(self.demo.params):
            self.assertIsInstance(leaf, np.ndarray)
        read = nnx.jit(lambda m, hu: m.ct_only(hu))
        out = read(D.restored(self.demo), jnp.asarray(self.held.hu))
        np.testing.assert_allclose(np.asarray(out["points"]), self.demo.snapshots[-1].points, rtol=1e-5, atol=1e-5)
        self.assertEqual(self.demo.train_mean, float(np.mean(self.ex.values[:, 0])))

    def test_each_set_is_drawn_after_training_and_read_from_the_ct_alone_by_the_run_network(self):
        from autoanatomist import demo as D, smoke, train as T
        model = D.restored(self.demo)
        read = nnx.jit(lambda m, hu: m.ct_only(hu)["values"][:, 0])
        for r, test in zip(self.results, tiny_tests()):
            ex = T.make_examples(self.cfg, 2, smoke.COUNT, seed=D.TEST_SEED, **D.phantom_settings(test))
            np.testing.assert_array_equal(r.reference, ex.values[:, 0])
            np.testing.assert_allclose(r.read, np.asarray(read(model, jnp.asarray(ex.hu))), rtol=1e-6)
            self.assertEqual((r.levels, list(r.columns)), ([x.level for x in ex.readings], list(ex.spine)))
        self.assertFalse(np.allclose(self.results[0].read, self.results[1].read))   # the noise reaches the reading

    def test_a_set_takes_the_held_out_phantoms_settings_but_those_it_names(self):
        from autoanatomist import demo as D, smoke
        held = dict(phenotypes=("typical",), starts=smoke.HELD_STARTS, **smoke.PHANTOM)
        self.assertEqual(D.phantom_settings(D.TestSet("same", "", {})), held)
        self.assertEqual(D.phantom_settings(D.TestSet("noisy", "", {"noise_hu": 60.0})), dict(held, noise_hu=60.0))

    def test_the_test_sets_are_new_draws_and_each_differs_from_training_as_it_says(self):
        from autoanatomist import demo as D, smoke
        self.assertNotIn(D.TEST_SEED, smoke.SEEDS.values())
        trained = {ORDER[ORDER.index(start) + k] for start in smoke.TRAIN_STARTS for k in range(smoke.COUNT)}
        by_name = {t.name: t for t in D.TESTS}
        unseen = {ORDER[ORDER.index(start) + k] for start in by_name["unseen levels"].settings["starts"]
                  for k in range(smoke.COUNT)}
        self.assertEqual(trained & unseen, set())
        self.assertEqual(by_name["new patients"].settings, {})
        self.assertGreater(by_name["noisier scanner"].settings["noise_hu"], smoke.PHANTOM["noise_hu"])
        self.assertGreater(by_name["coarser scan"].settings["spacing_mm"], smoke.PHANTOM["spacing_mm"])
        self.assertNotIn("typical", by_name["transitional spines"].settings["phenotypes"])
        self.assertEqual(len(D.TEST_COLOURS), len(D.TESTS))

    def test_the_error_is_the_mean_absolute_one_and_its_interval_resamples_whole_columns(self):
        from autoanatomist import demo as D
        r = D.Tested(test=tiny_tests()[0], levels=["L1"] * 4, columns=np.array([0, 0, 1, 1]),
                     reference=np.array([40.0, 40.0, 40.0, 40.0]), read=np.array([41.0, 43.0, 40.0, 38.0]))
        self.assertEqual(r.error(), 1.5)
        self.assertEqual(r.error(np.full(4, 42.0)), 2.0)
        low, high = r.interval()
        self.assertEqual((low, high), r.interval())                      # the same draws every time
        self.assertEqual((low, high), (1.0, 2.0))                       # the two columns' own means are the ends
        one = D.Tested(test=r.test, levels=["L1"] * 2, columns=np.array([0, 0]), reference=np.array([40.0, 40.0]),
                       read=np.array([41.0, 43.0]))
        self.assertEqual(one.interval(), (2.0, 2.0))

    @unittest.skipUnless(HAVE_PLOTLY, "plotly is not installed")
    def test_the_figure_sets_each_vertebra_against_its_reference_and_each_sets_error_against_the_guess(self):
        from autoanatomist import demo as D
        fig = D.test_figure(self.results, self.demo)
        self.assertEqual((fig.layout.width, fig.layout.height, fig.layout.autosize), (D.WIDTH_PX, D.TEST_HEIGHT_PX, False))
        n = len(self.results)
        diagonal, points, means, guess = fig.data[0], fig.data[1:1 + n], fig.data[1 + n:1 + 2 * n], fig.data[-1]
        self.assertEqual(list(diagonal.x), list(diagonal.y))
        for r, dots, mean in zip(self.results, points, means):
            np.testing.assert_array_equal(dots.x, r.reference)
            np.testing.assert_array_equal(dots.y, r.read)
            self.assertEqual((dots.name, list(dots.text)), (r.test.name, r.levels))
            low, high = r.interval()
            self.assertEqual((list(mean.x), list(mean.y)), ([r.test.name], [r.error()]))
            self.assertAlmostEqual(mean.error_y.array[0], high - r.error())
            self.assertAlmostEqual(mean.error_y.arrayminus[0], r.error() - low)
        self.assertEqual(list(guess.x), [r.test.name for r in self.results])
        np.testing.assert_allclose(guess.y, [np.mean(np.abs(self.demo.train_mean - r.reference)) for r in self.results])
        table = D.test_table(self.results, self.demo)
        self.assertEqual(table.count("<tr>"), n)
        for r in self.results:
            self.assertIn("<td>%.1f mm [%.1f, %.1f]</td>" % ((r.error(),) + r.interval()), table)

    @unittest.skipUnless(HAVE_PLOTLY, "plotly is not installed")
    def test_the_command_tests_a_kept_run_and_says_how_it_did_on_each_set(self):
        from autoanatomist import demo as D
        with tempfile.TemporaryDirectory() as out:
            kept, page = os.path.join(out, "run.pkl"), os.path.join(out, "test.html")
            with open(kept, "wb") as f:
                pickle.dump(self.demo, f, protocol=pickle.HIGHEST_PROTOCOL)
            with mock.patch.object(D, "TESTS", tiny_tests()), mock.patch.object(D, "TEST_COLUMNS", 2), \
                    mock.patch.object(D, "run") as run, redirect_stdout(io.StringIO()) as said:
                self.assertEqual(D.main(["demo", page, "--load", kept, "--test", "--plotlyjs", "cdn"]), 0)
            run.assert_not_called()
            with open(page) as f:
                text = f.read()
        lines = said.getvalue().splitlines()
        for r, line in zip(self.results, lines):
            self.assertTrue(line.startswith("%s: %d vertebrae, the network's mean error %.1f mm"
                                            % (r.test.name, len(r.reference), r.error())), line)
        self.assertIn("phantoms it never saw", text)
        self.assertIn("guessing the mean", text)

    def test_each_set_keeps_its_cts_and_both_pairs_of_points_and_its_median_vertebra(self):
        from autoanatomist import demo as D
        for r in self.results:
            n = len(r.reference)
            self.assertEqual((r.hu.shape[0], r.reference_points.shape, r.read_points.shape), (n, (n, 2, 3), (n, 2, 3)))
            self.assertEqual([len(t) for t in r.ticks], list(r.hu.shape[1:]))
        r = D.Tested(test=tiny_tests()[0], levels=["L1"] * 4, columns=np.array([0, 0, 1, 1]),
                     reference=np.full(4, 40.0), read=np.array([40.5, 43.0, 38.0, 41.0]))
        self.assertEqual(r.typical(), 3)            # errors 0.5, 3, 2, 1: the lower middle one is 1 mm

    @unittest.skipUnless(HAVE_PLOTLY, "plotly is not installed")
    def test_the_fits_draw_each_sets_median_vertebra_with_the_reference_and_the_networks_points(self):
        from autoanatomist import demo as D
        fig = D.fits_figure(self.results)
        self.assertEqual((fig.layout.width, fig.layout.height), (D.WIDTH_PX, D.FITS_HEIGHT_PX))
        self.assertEqual(len(fig.data), 3 * len(self.results))
        for i, r in enumerate(self.results):
            k = r.typical()
            surface, reference, network = fig.data[3 * i:3 * i + 3]
            self.assertEqual(surface.type, "isosurface")
            np.testing.assert_allclose(np.c_[reference.x, reference.y, reference.z], r.reference_points[k], rtol=1e-6)
            np.testing.assert_allclose(np.c_[network.x, network.y, network.z], r.read_points[k], rtol=1e-6)
            self.assertEqual((reference.line.color, network.line.color), (D.BLUE, D.ORANGE))
            self.assertIn("%s: %.1f mm" % (r.levels[k], r.read[k]), fig.layout.annotations[i].text)

    def test_test_reads_a_kept_run_alone(self):
        from autoanatomist import demo as D
        with mock.patch.object(D, "run") as run, redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as stop:
            D.main(["demo", "out.html", "--test"])
        self.assertEqual(stop.exception.code, 2)
        run.assert_not_called()


def loaded_imports(tree) -> set:
    """The top-level names a module imports as it loads: its imports outside any function's body,
    an import relative to its own package left out."""
    found, todo = set(), list(tree.body)
    while todo:
        node = todo.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            continue
        if isinstance(node, ast.Import):
            found |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            found.add((node.module or "").split(".")[0])
        todo.extend(ast.iter_child_nodes(node))
    return found


def notebook():
    with open(NOTEBOOK) as f:
        return json.load(f)


def notebook_cells():
    return notebook()["cells"]


ACTS = "\nROOT, CUDA, WHY_CPU = prepare()"


def setup_source() -> str:
    code = [c for c in notebook_cells() if c["cell_type"] == "code"]
    return "".join(code[0]["source"])


def setup_definitions() -> str:
    """The notebook's setup cell up to the line that acts: its imports, constants and functions."""
    head, sep, _ = setup_source().partition(ACTS)
    assert sep, "the setup cell no longer acts by calling prepare()"
    return head


def setup_namespace(base: str) -> dict:
    ns = {}
    exec(setup_definitions(), ns)
    ns["BASE"], ns["CLONE"] = base, os.path.join(base, "bordercall")
    return ns


class SecretNotFoundError(Exception):
    pass


def colab_stand_in(secret=None, upload=None) -> dict:
    """google.colab's userdata and files, as far as the setup cell uses them."""
    userdata, files = types.ModuleType("google.colab.userdata"), types.ModuleType("google.colab.files")

    def get(name):
        if secret is None:
            raise SecretNotFoundError(name)
        return secret

    def upload_one():
        name = os.path.basename(upload)
        with open(upload, "rb") as f:
            data = f.read()
        with open(name, "wb") as f:
            f.write(data)
        return {name: data}
    userdata.get, files.upload = get, upload_one
    colab = types.ModuleType("google.colab")
    colab.userdata, colab.files = userdata, files
    google = types.ModuleType("google")
    google.colab = colab
    return {"google": google, "google.colab": colab, "google.colab.userdata": userdata, "google.colab.files": files}


LISTING = "GPU 0: Tesla T4 (UUID: GPU-00000000-0000-0000-0000-000000000000)\n"
HEADER = "| NVIDIA-SMI 580.82.07    Driver Version: 580.82.07    CUDA Version: 13.0 |\n"
FAILED = ("Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\n"
          "RuntimeError: Unable to initialize backend 'cuda': CUDA_ERROR_SYSTEM_DRIVER_MISMATCH (you may "
          "need to uninstall the failing plugin package, or set JAX_PLATFORMS=cpu to skip this backend.)\n")
# Colab's images of October 2026 (googlecolab/backend-info), as far as the setup cell reads them.
COLAB_CPU = {"jax": "0.11.1", "jaxlib": "0.11.1", "flax": "0.11.2", "optax": "0.2.8"}
COLAB_GPU = dict(COLAB_CPU, **{"jax-cuda13-plugin": "0.11.1", "jax-cuda13-pjrt": "0.11.1"})


class Runtime:
    """A stand-in for a Colab runtime as the setup cell's commands meet it: nvidia-smi, pip, which
    changes what is installed, and the child that starts JAX, every command kept in the order run."""

    def __init__(self, image, gpu=True, child=(0, "gpu\n", "")):
        self.packages, self.gpu, self.child, self.commands = dict(image), gpu, child, []

    def installed(self, name):
        return self.packages.get(name)

    def run(self, argv, **kw):
        self.commands.append(list(argv))
        if argv[0] == "nvidia-smi":
            if not self.gpu:
                raise FileNotFoundError("nvidia-smi")
            return subprocess.CompletedProcess(argv, 0, stdout=LISTING if "-L" in argv else HEADER, stderr="")
        if argv[1:3] == ["-m", "pip"]:
            for name in self.named(argv):
                package, _, version = name.partition("==")
                if argv[3] == "uninstall":
                    self.packages.pop(package, None)
                else:
                    self.packages[package.split("[")[0]] = version or "the newest"
            return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")
        if argv[1] == "-c":
            code, out, err = self.child
            return subprocess.CompletedProcess(argv, code, stdout=out, stderr=err)
        raise AssertionError("the cell ran %r" % (argv,))

    @staticmethod
    def named(argv):
        return [word for word in argv[4:] if not word.startswith("-")]

    def steps(self):
        """What ran beside nvidia-smi, in order: pip's uninstall and install, and the child."""
        return [argv[3] if argv[1:3] == ["-m", "pip"] else "child" for argv in self.commands if argv[0] != "nvidia-smi"]

    def asked(self, verb):
        """The packages each pip command of one verb named."""
        return [self.named(argv) for argv in self.commands if argv[1:4] == ["-m", "pip", verb]]


STARTED = {"device_code": "the-device-code", "user_code": "WDJB-MJHT",
           "verification_uri": "https://github.com/login/device", "expires_in": 900, "interval": 5}


class GitHubStandIn:
    """GitHub's sign-in service as urllib's urlopen meets it: each post answered in turn, with a
    status and a body (JSON unless given as bytes) or by raising, every request kept."""

    def __init__(self, *answers):
        self.answers, self.requests = list(answers), []

    def urlopen(self, request, timeout=None):
        self.requests.append(request)
        answer = self.answers.pop(0)
        if isinstance(answer, BaseException):
            raise answer
        status, body = answer
        data = io.BytesIO(body if isinstance(body, bytes) else json.dumps(body).encode())
        if status != 200:
            raise urllib.error.HTTPError(request.full_url, status, "refused", {}, data)
        return data

    def fields(self, k):
        return dict(urllib.parse.parse_qsl(self.requests[k].data.decode()))


class TheNotebook(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.base = self.scratch.name
        self.ns = setup_namespace(self.base)

    def tearDown(self):
        self.scratch.cleanup()

    def test_it_is_kept_with_no_outputs_and_its_code_compiles(self):
        for cell in notebook_cells():
            if cell["cell_type"] == "code":
                self.assertEqual(cell["outputs"], [])
                self.assertIsNone(cell["execution_count"])
                compile("".join(cell["source"]), NOTEBOOK, "exec")

    def test_it_asks_colab_for_a_t4(self):
        meta = notebook()["metadata"]
        self.assertEqual(meta["accelerator"], "GPU")
        self.assertEqual(meta["colab"]["gpuType"], "T4")

    def test_a_missing_secret_reads_as_none_and_a_secret_as_itself(self):
        with mock.patch.dict(sys.modules, colab_stand_in()):
            self.assertIsNone(self.ns["token"]())
        with mock.patch.dict(sys.modules, colab_stand_in(secret="not-a-token")):
            self.assertEqual(self.ns["token"](), "not-a-token")

    def test_the_clone_is_shallow_and_sparse_and_the_token_reaches_git_through_the_credential_helper_alone(self):
        calls = []

        def run(argv, env=None, **kw):
            calls.append((argv, env))
            return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")
        with mock.patch.object(self.ns["subprocess"], "run", run):
            self.assertIsNone(self.ns["clone"]("not-a-token", "main"))
        (clone, env), (sparse, _) = calls
        for argv, _ in calls:
            self.assertNotIn("not-a-token", " ".join(argv))
        self.assertEqual((env["GITHUB_TOKEN"], env["GIT_TERMINAL_PROMPT"]), ("not-a-token", "0"))
        self.assertEqual(clone[clone.index("clone"):], ["clone", "--quiet", "--depth", "1", "--filter=blob:none", "--sparse",
                                                        "--branch", "main",
                                                        "https://github.com/OpenSpineConsortium/bordercall.git",
                                                        self.ns["CLONE"]])
        self.assertEqual(sparse[sparse.index("-C"):], ["-C", self.ns["CLONE"], "sparse-checkout", "set",
                                                       "autoanatomist", "scanimport", "schwingcheck"])
        helper = [a for a in clone if a.startswith("credential.helper=")][0].split("=", 1)[1]
        env = dict(os.environ, GITHUB_TOKEN="not-a-token", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        out = subprocess.run(["git", "-c", "credential.helper=" + helper, "credential", "fill"], cwd=self.base,
                             input="protocol=https\nhost=github.com\n\n", capture_output=True, text=True,
                             env=env, check=True).stdout
        self.assertIn("username=x-access-token\n", out)
        self.assertIn("password=not-a-token\n", out)

    def test_a_clone_git_refuses_says_gits_last_words_and_goes_no_further(self):
        calls = []

        def run(argv, **kw):
            calls.append(argv)
            return subprocess.CompletedProcess(argv, 128, stdout="",
                                               stderr="Cloning into 'bordercall'...\nremote: Repository not found.\n")
        with mock.patch.object(self.ns["subprocess"], "run", run):
            self.assertEqual(self.ns["clone"]("not-a-token", "main"), "remote: Repository not found.")
        self.assertEqual(len(calls), 1)

    def test_the_folders_the_clone_checks_out_hold_every_folder_of_bordercalls_the_demo_loads(self):
        """The imports a module runs as it loads, not those inside a function, which run when it is
        called: schwingcheck's one_body imports coarse in one, a path the demo never takes."""
        local = {name for name in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, name))}
        reached, todo = set(), ["autoanatomist"]
        while todo:
            folder = todo.pop()
            if folder in reached:
                continue
            reached.add(folder)
            for here, _, names in os.walk(os.path.join(ROOT, folder)):
                for name in (n for n in names if n.endswith(".py")):
                    with open(os.path.join(here, name)) as f:
                        todo.extend(loaded_imports(ast.parse(f.read())) & local)
        self.assertLessEqual(reached, set(self.ns["NEEDED"]))
        self.assertIn("scanimport", reached)

    @unittest.skipUnless(HAVE_JAX, "jax is not installed")
    def test_the_demo_loads_from_those_folders_alone(self):
        with tempfile.TemporaryDirectory() as sparse:
            for folder in self.ns["NEEDED"]:
                shutil.copytree(os.path.join(ROOT, folder), os.path.join(sparse, folder),
                                ignore=shutil.ignore_patterns("__pycache__"))
            child = subprocess.run([sys.executable, "-I", "-c", "import sys; sys.path.insert(0, %r); "
                                    "import autoanatomist.demo" % sparse], capture_output=True, text=True)
        self.assertEqual(child.returncode, 0, child.stderr)

    def fetch(self, github, secret=None, refused=None):
        """fetch() with no clone yet, the secret in Colab's Secrets, the stand-in for GitHub's sign-in,
        a clone that only records what it was given, or that git refuses with these words, and a ZIP
        that is never asked for in earnest: what fetch returned and printed, the clones, the waits
        between polls and why the ZIP was asked for."""
        clones, waits, said, zips = [], [], io.StringIO(), []

        def clone(secret, ref):
            clones.append((secret, ref))
            if refused:
                return refused
            os.makedirs(os.path.join(self.ns["CLONE"], "autoanatomist"), exist_ok=True)
            open(os.path.join(self.ns["CLONE"], "autoanatomist", "demo.py"), "w").close()
            return None

        def unpack_upload(why):
            zips.append(why)
            return "the ZIP"
        with mock.patch.dict(sys.modules, colab_stand_in(secret=secret)), \
                mock.patch.dict(self.ns, clone=clone, unpack_upload=unpack_upload), \
                mock.patch.object(self.ns["urllib"].request, "urlopen", github.urlopen), \
                mock.patch.object(self.ns["time"], "sleep", waits.append), redirect_stdout(said):
            got = self.ns["fetch"]()
        self.zips = zips
        return got, said.getvalue(), clones, waits

    def test_with_no_secret_it_signs_in_with_github_and_clones_with_what_github_grants(self):
        github = GitHubStandIn((200, STARTED), (200, {"error": "authorization_pending"}),
                               (200, {"error": "slow_down", "interval": 10}),
                               (200, {"access_token": "not-a-token", "token_type": "bearer"}))
        got, said, clones, waits = self.fetch(github)
        self.assertEqual((got, clones), (self.ns["CLONE"], [("not-a-token", self.ns["REFS"][0])]))
        self.assertIn("open https://github.com/login/device and enter the code WDJB-MJHT", said)
        self.assertNotIn("not-a-token", said)
        self.assertNotIn("the-device-code", said)
        self.assertEqual(waits, [5, 5, 10])
        app = "Iv23liTkIRov2FYN83wD"                                  # SymphonyBoard's client ID
        self.assertEqual([r.full_url for r in github.requests],
                         ["https://github.com/login/device/code"] + ["https://github.com/login/oauth/access_token"] * 3)
        self.assertEqual(github.fields(0), {"client_id": app})
        for k in (1, 2, 3):
            self.assertEqual(github.fields(k), {"client_id": app, "device_code": "the-device-code",
                                                "grant_type": "urn:ietf:params:oauth:grant-type:device_code"})
        for request in github.requests:
            self.assertEqual((request.get_method(), request.get_header("Accept")), ("POST", "application/json"))

    def test_a_sign_in_refused_declined_or_let_expire_falls_back_to_the_zip_saying_why(self):
        disabled = (400, {"error": "device_flow_disabled",
                          "error_description": "Device Flow must be explicitly enabled for this App"})
        denied = (200, {"error": "access_denied", "error_description": "The authorization request was denied."})
        for answers, why in (((disabled,), "Device Flow must be explicitly enabled for this App"),
                             (((200, STARTED), denied), "The authorization request was denied."),
                             (((200, dict(STARTED, expires_in=0)),), "The sign-in code expired."),
                             ((urllib.error.URLError("no route to host"),), "no route to host"),
                             (((502, b"<html>Bad gateway</html>"),), "GitHub answered 502"),
                             (((200, b"[]"),), "GitHub answered 200")):
            github = GitHubStandIn(*answers)
            got, said, clones, _ = self.fetch(github)
            self.assertEqual((got, clones, github.answers), ("the ZIP", [], []))
            self.assertIn(why, said)
            self.assertEqual(self.zips, ["No GITHUB_TOKEN in Colab's Secrets and no sign-in"])

    def test_where_git_gets_the_demo_at_no_ref_it_says_why_at_each_and_asks_for_the_zip(self):
        got, said, clones, _ = self.fetch(GitHubStandIn(), secret="from-secrets", refused="remote: Repository not found.")
        self.assertEqual(got, "the ZIP")
        self.assertEqual(clones, [("from-secrets", ref) for ref in self.ns["REFS"]])
        for ref in self.ns["REFS"]:
            self.assertIn("bordercall's %s: remote: Repository not found." % ref, said)
        self.assertEqual(self.zips, ["Git could not get the demo with that token"])

    def test_a_token_in_colabs_secrets_comes_before_signing_in(self):
        github = GitHubStandIn()                     # a post to GitHub's sign-in would find no answer
        got, _, clones, _ = self.fetch(github, secret="from-secrets")
        self.assertEqual((got, clones, github.requests), (self.ns["CLONE"], [("from-secrets", "main")], []))

    def test_with_no_secret_and_no_sign_in_it_unpacks_a_zip_as_github_makes_one_and_keeps_it(self):
        top = "bordercall-claude-project-thread-5hj0q5"
        upload = os.path.join(self.base, top + ".zip")
        with zipfile.ZipFile(upload, "w") as z:
            for rel in ("autoanatomist/demo.py", "requirements-autoanatomist.txt"):
                z.write(os.path.join(ROOT, rel), top + "/" + rel)
        here = os.getcwd()
        os.chdir(self.base)
        try:
            with mock.patch.dict(sys.modules, colab_stand_in(upload=upload)), \
                    mock.patch.dict(self.ns, sign_in=lambda: None), redirect_stdout(io.StringIO()):
                root = self.ns["fetch"]()
                self.assertEqual(self.ns["fetch"](), root)
        finally:
            os.chdir(here)
        self.assertEqual(root, self.ns["CLONE"])
        self.assertTrue(os.path.exists(os.path.join(root, "autoanatomist", "demo.py")))

    def test_it_installs_the_four_packages_bordercall_pins(self):
        wanted = {}
        with open(os.path.join(ROOT, "requirements-autoanatomist.txt")) as f:
            for line in f:
                name, _, version = line.split(";")[0].strip().partition("==")
                if name in ("jax", "jaxlib", "flax", "optax"):
                    wanted[name] = version
        self.assertEqual(self.ns["pins"](ROOT), wanted)
        self.assertEqual(len(wanted), 4)

    def test_on_a_gpu_it_adds_the_gpu_build_of_the_same_jaxlib_with_nvidias_libraries(self):
        cpu, spec = self.ns["pins"](ROOT), self.ns["spec"]
        for major in ("12", "13"):
            gpu = self.ns["pins"](ROOT, major)
            self.assertEqual({k: v for k, v in gpu.items() if k in cpu}, cpu)
            self.assertEqual(gpu["jax-cuda%s-plugin" % major], cpu["jaxlib"])  # JAX releases it under jaxlib's version
            self.assertEqual(gpu["jax-cuda%s-pjrt" % major], cpu["jaxlib"])
            self.assertEqual(len(gpu), 6)
            self.assertEqual(spec("jax-cuda%s-plugin" % major, "1.2"), "jax-cuda%s-plugin[with-cuda]==1.2" % major)
            self.assertEqual(spec("jax-cuda%s-pjrt" % major, "1.2"), "jax-cuda%s-pjrt==1.2" % major)
        self.assertEqual(spec("jax", "1.2"), "jax==1.2")
        with tempfile.TemporaryDirectory() as root:   # a jax released over an older jaxlib, as jax 0.5.2 was over 0.5.1
            with open(os.path.join(root, "requirements-autoanatomist.txt"), "w") as f:
                f.write("jax==0.5.2\njaxlib==0.5.1\nflax==0.10.4\noptax==0.2.4\n")
            gpu = self.ns["pins"](root, "12")
            self.assertEqual((gpu["jax"], gpu["jax-cuda12-plugin"], gpu["jax-cuda12-pjrt"]), ("0.5.2", "0.5.1", "0.5.1"))

    def test_the_gpu_build_is_for_the_cuda_version_whose_build_the_image_carries(self):
        def nvidia_smi(text):
            return lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout=text, stderr="")
        new, old = HEADER, HEADER.replace("13.0", "12.4")
        colab = {"jax-cuda13-plugin": "0.11.1", "jax-cuda13-pjrt": "0.11.1"}     # Colab's GPU image of October 2026
        for carried, header, major in ((colab, old, "13"), ({"jax-cuda12-plugin": "0.5.1"}, new, "12"),
                                       ({}, new, "13"), ({}, old, "12"), ({}, "", "12")):
            with mock.patch.dict(self.ns, installed=carried.get), \
                    mock.patch.object(self.ns["subprocess"], "run", nvidia_smi(header)):
                self.assertEqual(self.ns["cuda_major"](), major)

    def test_it_takes_the_other_cuda_versions_build_out_before_it_installs(self):
        carried = {"jax": "0.1", "jax-cuda12-plugin": "0.5.1", "jax-cuda12-pjrt": "0.5.1"}
        with mock.patch.dict(self.ns, installed=carried.get):
            stale = self.ns["stale_plugins"]("13")
            self.assertEqual(stale, ["jax-cuda12-plugin", "jax-cuda12-pjrt"])
            self.assertEqual(self.ns["stale_plugins"]("12"), [])
        verbs = []

        def pip(argv, **kw):
            verbs.append(argv[3])
            if argv[3] == "uninstall":
                for name in argv[-2:]:
                    carried.pop(name)
            else:
                carried["jax"] = "9.9"
        with mock.patch.dict(self.ns, installed=carried.get), mock.patch.object(self.ns["subprocess"], "run", pip):
            self.ns["install"]({"jax": "9.9"}, stale)
        self.assertEqual(verbs, ["uninstall", "install"])
        self.assertEqual(carried, {"jax": "9.9"})

    def test_a_gpu_jax_does_not_start_on_leaves_the_session_on_the_cpu_saying_why(self):
        def child(code, out="", err=""):
            return lambda *a, **k: subprocess.CompletedProcess(a, code, stdout=out, stderr=err)
        for answer, why in ((child(0, "gpu\n"), None), (child(0, "cpu\n"), "JAX chose its cpu backend"),
                            (child(1, err=FAILED), FAILED.splitlines()[-1])):
            with mock.patch.object(self.ns["subprocess"], "run", answer):
                self.assertEqual(self.ns["why_no_gpu"](), why)
        for why, platform in ((None, None), ("JAX chose its cpu backend", "cpu")):
            with mock.patch.dict(os.environ), mock.patch.dict(self.ns, why_no_gpu=lambda why=why: why):
                os.environ.pop("JAX_PLATFORMS", None)
                self.assertEqual(self.ns["settle_platform"]("13"), why)
                self.assertEqual(os.environ.get("JAX_PLATFORMS"), platform)
        with mock.patch.dict(os.environ):
            self.assertEqual(self.ns["settle_platform"](None), "this session has no GPU")
            self.assertEqual(os.environ["JAX_PLATFORMS"], "cpu")

    def test_the_gpu_is_tried_in_a_child_free_of_this_sessions_jax_platforms(self):
        seen = {}

        def run(argv, env=None, **kw):
            seen.update(argv=argv, env=env)
            return subprocess.CompletedProcess(argv, 0, stdout="gpu\n", stderr="")
        with mock.patch.dict(os.environ, JAX_PLATFORMS="cpu"), mock.patch.object(self.ns["subprocess"], "run", run):
            self.assertIsNone(self.ns["why_no_gpu"]())
        self.assertEqual(seen["argv"][0], sys.executable)
        self.assertNotIn("JAX_PLATFORMS", seen["env"])
        self.assertEqual(seen["env"]["XLA_PYTHON_CLIENT_PREALLOCATE"], "false")

    @unittest.skipUnless(HAVE_JAX, "jax is not installed")
    def test_the_child_starts_jax_on_the_backend_this_session_has(self):
        with mock.patch.dict(os.environ):
            os.environ.pop("JAX_PLATFORMS", None)
            child = subprocess.run([sys.executable, "-c", "import jax; print(jax.default_backend())"],
                                   capture_output=True, text=True, check=True)
            why = self.ns["why_no_gpu"]()
        backend = child.stdout.split()[-1]
        self.assertEqual(why is None, backend == "gpu")
        said = [line.strip() for line in child.stderr.splitlines() if line.strip()]
        if why is not None and said:                   # JAX's own words, a warning about the GPU most often
            self.assertIn(why, said)
        elif why is not None:
            self.assertEqual(why, "JAX chose its %s backend" % backend)

    def test_without_plotly_it_stops_before_training_or_installs_it_in_colab(self):
        with mock.patch.dict(sys.modules, {"plotly": None}):
            with mock.patch.dict(self.ns, in_colab=lambda: False), self.assertRaises(SystemExit) as stop:
                self.ns["ensure_plotly"]()
            self.assertIn("pip install plotly", str(stop.exception))
            calls = []
            with mock.patch.dict(self.ns, in_colab=lambda: True), \
                    mock.patch.object(self.ns["subprocess"], "run", lambda argv, **k: calls.append(argv)):
                self.ns["ensure_plotly"]()
            self.assertEqual(calls[0][-1], "plotly")
        if HAVE_PLOTLY:
            calls = []
            with mock.patch.object(self.ns["subprocess"], "run", lambda argv, **k: calls.append(argv)):
                self.ns["ensure_plotly"]()
            self.assertEqual(calls, [])

    def test_a_gpu_is_what_nvidia_smi_lists(self):
        def lists(text):
            return lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout=text, stderr="")

        def missing(*a, **k):
            raise FileNotFoundError("nvidia-smi")
        for run, expected in ((lists(LISTING), True), (lists(""), False), (missing, False)):
            with mock.patch.object(self.ns["subprocess"], "run", run):
                self.assertIs(self.ns["has_gpu"](), expected)

    def test_pins_already_installed_run_no_pip(self):
        calls = []
        with mock.patch.dict(self.ns, installed=lambda name: "1.0"), \
                mock.patch.object(self.ns["subprocess"], "run", lambda *a, **k: calls.append(a)):
            self.ns["install"]({"jax": "1.0", "optax": "1.0"})
        self.assertEqual(calls, [])

    def test_pip_replacing_a_package_this_session_imported_goes_on_with_no_restart(self):
        versions = {"jax": "0.1", "numpy": "1.0"}

        def pip(*a, **k):
            versions.update(jax="9.9", numpy="2.0")
        with mock.patch.dict(self.ns, installed=versions.get), mock.patch.dict(sys.modules, {"numpy": np}), \
                mock.patch.object(self.ns["subprocess"], "run", pip):
            self.ns["install"]({"jax": "9.9"})
        self.assertEqual(versions, {"jax": "9.9", "numpy": "2.0"})

    def prepare(self, runtime, colab=True, plotly=True):
        """prepare() on a stand-in runtime, bordercall fetched already and plotly there or not: what it
        returned and JAX_PLATFORMS after it."""
        found = types.ModuleType("plotly")
        found.__spec__ = importlib.machinery.ModuleSpec("plotly", None)
        with mock.patch.dict(self.ns, in_colab=lambda: colab, fetch=lambda: ROOT, repository_root=lambda: ROOT,
                             installed=runtime.installed), \
                mock.patch.object(self.ns["subprocess"], "run", runtime.run), \
                mock.patch.dict(sys.modules, {"plotly": found if plotly else None}), mock.patch.dict(os.environ):
            os.environ.pop("JAX_PLATFORMS", None)
            return self.ns["prepare"](), os.environ.get("JAX_PLATFORMS")

    def test_on_colabs_gpu_image_it_installs_the_pins_with_the_build_the_image_carries_and_uses_the_gpu(self):
        runtime = Runtime(COLAB_GPU)
        got, platform = self.prepare(runtime)
        self.assertEqual((got, platform), ((ROOT, "13", None), None))
        self.assertEqual(runtime.steps(), ["install", "child"])
        pinned = self.ns["pins"](ROOT)
        lacking = {"%s==%s" % (name, version) for name, version in pinned.items() if COLAB_GPU[name] != version}
        cuda13 = {"jax-cuda13-plugin[with-cuda]==" + pinned["jaxlib"], "jax-cuda13-pjrt==" + pinned["jaxlib"]}
        self.assertEqual(set(runtime.asked("install")[0]), lacking | cuda13)
        for name in ("jaxlib", "jax-cuda13-plugin", "jax-cuda13-pjrt"):
            self.assertEqual(runtime.packages[name], pinned["jaxlib"])

    def test_on_a_gpu_image_with_a_second_cuda_build_it_takes_that_one_out_first(self):
        runtime = Runtime(dict(COLAB_GPU, **{"jax-cuda12-plugin": "0.5.1", "jax-cuda12-pjrt": "0.5.1"}))
        (_, cuda, why), _ = self.prepare(runtime)
        self.assertEqual((cuda, why), ("13", None))
        self.assertEqual(runtime.steps(), ["uninstall", "install", "child"])
        self.assertEqual(runtime.asked("uninstall"), [["jax-cuda12-plugin", "jax-cuda12-pjrt"]])
        self.assertEqual([name for name in runtime.packages if "cuda12" in name], [])

    def test_where_jax_does_not_start_on_the_gpu_it_trains_on_the_cpu_and_says_why(self):
        runtime = Runtime(COLAB_GPU, child=(1, "", FAILED))
        (_, cuda, why), platform = self.prepare(runtime)
        self.assertEqual((cuda, why, platform), ("13", FAILED.splitlines()[-1], "cpu"))
        self.assertEqual(runtime.steps(), ["install", "child"])

    def test_on_colabs_cpu_image_it_installs_no_gpu_build_and_tries_no_gpu(self):
        runtime = Runtime(COLAB_CPU, gpu=False)
        (_, cuda, why), platform = self.prepare(runtime)
        self.assertEqual((cuda, why, platform), (None, "this session has no GPU", "cpu"))
        self.assertEqual(runtime.steps(), ["install"])
        self.assertEqual([name for name in runtime.packages if name.startswith("jax-cuda")], [])

    def test_with_the_pins_in_place_it_runs_no_pip(self):
        runtime = Runtime(dict(COLAB_GPU, **self.ns["pins"](ROOT, "13")))
        (_, cuda, why), _ = self.prepare(runtime)
        self.assertEqual((cuda, why, runtime.steps()), ("13", None, ["child"]))

    def test_without_plotly_it_stops_outside_colab_before_anything_slow_and_installs_it_in_colab(self):
        runtime = Runtime(COLAB_GPU)
        with self.assertRaises(SystemExit) as stop:
            self.prepare(runtime, colab=False, plotly=False)
        self.assertIn("pip install plotly", str(stop.exception))
        self.assertEqual(runtime.steps(), [])
        runtime = Runtime(COLAB_GPU)
        self.prepare(runtime, plotly=False)
        self.assertEqual(runtime.steps(), ["install", "install", "child"])
        self.assertEqual(runtime.asked("install")[1], ["plotly"])

    def test_no_cell_imports_jax_or_bordercall_so_pip_never_asks_for_a_restart(self):
        def imports(node):
            if isinstance(node, ast.Import):
                return {alias.name.split(".")[0] for alias in node.names}
            if isinstance(node, ast.ImportFrom):
                return {(node.module or "").split(".")[0]}
            return set()
        late = {"jax", "jaxlib", "flax", "optax", "autoanatomist", "scanimport", "schwingcheck"}
        code = [c for c in notebook_cells() if c["cell_type"] == "code"]
        self.assertEqual(len(code), 4)
        for cell in code:
            self.assertEqual([node for node in ast.walk(ast.parse("".join(cell["source"]))) if imports(node) & late], [])

    def run_demo(self, code, said):
        """run_demo's words to a stand-in child that prints these lines and exits with this code:
        what the child was started with and what the cell printed."""
        seen = {}

        class Child:
            def __init__(self, argv, **kw):
                seen.update(argv=argv, **kw)
                self.stdout, self.returncode = io.StringIO("".join(line + "\n" for line in said)), None

            def __enter__(self):
                return self

            def __exit__(self, *raised):
                self.returncode = code
        self.ns["ROOT"] = self.base
        with mock.patch.object(self.ns["subprocess"], "Popen", Child), redirect_stdout(io.StringIO()) as printed:
            self.ns["run_demo"]("page.html", "--load", "kept.pkl")
        return seen, printed.getvalue()

    def test_the_demo_trains_and_draws_in_a_child_of_this_python_its_words_shown_as_they_come(self):
        seen, printed = self.run_demo(0, ["step 25 of 150: w 1.00", "page.html: 31 snapshots"])
        self.assertEqual(seen["argv"], [sys.executable, "-u", "-m", "autoanatomist.demo", "page.html", "--load",
                                        "kept.pkl"])
        self.assertEqual(seen["cwd"], self.base)
        self.assertNotIn("env", seen)                # this session's environment, JAX_PLATFORMS with it
        self.assertEqual((seen["stdout"], seen["stderr"]), (subprocess.PIPE, subprocess.STDOUT))
        self.assertEqual(printed, "step 25 of 150: w 1.00\npage.html: 31 snapshots\n")
        with self.assertRaises(SystemExit) as stop:
            self.run_demo(1, ["Traceback (most recent call last):", "ValueError: no such run"])
        self.assertEqual(str(stop.exception), "the demo stopped with exit 1: ValueError: no such run")

    GPU_ERROR = "jax.errors.JaxRuntimeError: INTERNAL: Failed to get configs for: 46 out of 218 instructions"
    # As JAX ends its report: the error, then its note on the frames it took out.
    GPU_STOP = ["step 0 of 150", "Traceback (most recent call last):", '  File "train.py", line 1, in <module>',
                GPU_ERROR, "--------------------",
                "For simplicity, JAX has removed its internal frames from the traceback of the following exception. "
                "Set JAX_TRACEBACK_FILTERING=off to include these."]

    def run_children(self, children, platforms=None):
        """run_demo's run-cell words to stand-in children, started one after another, each with its
        exit code and lines: each child's words and JAX_PLATFORMS as it started, what the cell
        printed, why it stopped (None where it did not) and JAX_PLATFORMS after it."""
        waiting, started = list(children), []

        class Child:
            def __init__(self, argv, **kw):
                self.code, said = waiting.pop(0)
                started.append((argv[4:], os.environ.get("JAX_PLATFORMS")))
                self.stdout, self.returncode = io.StringIO("".join(line + "\n" for line in said)), None

            def __enter__(self):
                return self

            def __exit__(self, *raised):
                self.returncode = self.code
        self.ns["ROOT"], stopped = self.base, None
        with mock.patch.dict(os.environ), mock.patch.object(self.ns["subprocess"], "Popen", Child), \
                redirect_stdout(io.StringIO()) as printed:
            os.environ.pop("JAX_PLATFORMS", None)
            if platforms:
                os.environ["JAX_PLATFORMS"] = platforms
            try:
                self.ns["run_demo"]("page.html", "--widths", "16,32,64", "--save", "kept.pkl")
            except SystemExit as stop:
                stopped = str(stop)
            after = os.environ.get("JAX_PLATFORMS")
        self.assertEqual(waiting, [], "every child the test gave was started")
        return started, printed.getvalue(), stopped, after

    def test_a_child_the_gpu_cannot_run_starts_again_on_the_cpu_at_the_cpus_widths(self):
        started, printed, stopped, after = self.run_children([(1, self.GPU_STOP), (0, ["page.html: 31 snapshots"])])
        self.assertIsNone(stopped)
        self.assertEqual(started, [(["page.html", "--widths", "16,32,64", "--save", "kept.pkl"], None),
                                   (["page.html", "--widths", "8,16,32", "--save", "kept.pkl"], "cpu")])
        self.assertEqual(after, "cpu")                 # so every child after it runs on the CPU too
        self.assertIn("The GPU could not run the network (%s), so the demo starts again on the CPU." % self.GPU_ERROR,
                      printed)
        self.assertTrue(printed.endswith("page.html: 31 snapshots\n"))
        self.assertEqual(self.ns["WHY_CPU"], "the GPU could not run the network (%s)" % self.GPU_ERROR)

    def test_after_a_fallback_setup_run_again_stays_on_the_cpu_and_the_run_cell_takes_its_widths(self):
        self.ns["WHY_CPU"] = None
        self.run_children([(1, self.GPU_STOP), (0, ["page.html: 31 snapshots"])])
        with mock.patch.dict(os.environ, JAX_PLATFORMS="cpu"), \
                mock.patch.dict(self.ns, why_no_gpu=lambda: self.fail("the GPU is not asked again")):
            self.assertIn("set to the CPU already", self.ns["settle_platform"]("13"))
            self.assertEqual(os.environ["JAX_PLATFORMS"], "cpu")
        calls = []
        exec(self.cell("run"), dict(os=os, OUT=self.base, CUDA="13", WHY_CPU=self.ns["WHY_CPU"],
                                    run_demo=lambda *words: calls.append(words)))
        self.assertEqual(calls[0][1:3], ("--widths", "8,16,32"))

    def test_only_the_last_traceback_of_a_child_that_exited_says_the_gpu_failed(self):
        failure = self.ns["gpu_failure"]
        warned = ["W external/xla/xla/service/gpu/autotuner.cc: CUDA warning, falling back"]
        self.assertEqual(failure(1, self.GPU_STOP), self.GPU_ERROR)
        self.assertIsNone(failure(-9, self.GPU_STOP))                       # killed by a signal
        self.assertIsNone(failure(1, warned + ["Killed"]))                  # a warning, then no traceback
        self.assertIsNone(failure(1, warned + ["Traceback (most recent call last):", "ValueError: no such run"]))
        self.assertIsNone(failure(1, self.GPU_STOP + ["Traceback (most recent call last):", "MemoryError"]))
        self.assertIsNone(failure(0, self.GPU_STOP))
        started, _, stopped, _ = self.run_children([(-9, warned + self.GPU_STOP[:1])])
        self.assertEqual((len(started), stopped), (1, "the demo stopped with exit -9: " + self.GPU_STOP[0]))

    def test_a_child_that_stops_for_another_reason_or_on_the_cpu_is_not_started_again(self):
        started, _, stopped, after = self.run_children([(1, ["Traceback (most recent call last):", "ValueError: no such run"])])
        self.assertEqual((len(started), stopped, after), (1, "the demo stopped with exit 1: ValueError: no such run", None))
        started, _, stopped, after = self.run_children([(1, self.GPU_STOP)], platforms="cpu")
        self.assertEqual((len(started), after), (1, "cpu"))
        self.assertEqual(stopped, "the demo stopped with exit 1: " + self.GPU_STOP[-1])
        started, _, stopped, _ = self.run_children([(1, self.GPU_STOP), (1, ["MemoryError"])])
        self.assertEqual((len(started), stopped), (2, "the demo stopped with exit 1: MemoryError"))

    @unittest.skipUnless(HAVE_JAX, "jax is not installed")
    def test_the_child_finds_the_demo_from_bordercalls_root(self):
        self.ns["ROOT"] = ROOT
        with redirect_stdout(io.StringIO()) as printed:
            self.ns["run_demo"]("--help")
        self.assertIn("usage: python -m autoanatomist.demo", printed.getvalue())

    def cell(self, name):
        return "".join(next(c for c in notebook_cells() if c.get("id") == name)["source"])

    def test_the_run_cell_trains_and_keeps_the_run_and_the_show_cell_draws_it_or_another_vertebra(self):
        page, kept = os.path.join(self.base, "anneal_demo.html"), os.path.join(self.base, "anneal_demo.pkl")
        calls = []
        ns = dict(os=os, OUT=self.base, run_demo=lambda *words: calls.append(("run",) + words),
                  show=lambda page: calls.append(("show", page)))
        for cuda, why, widths in (("13", None, "16,32,64"), ("13", "no driver", "8,16,32"),
                                  (None, "this session has no GPU", "8,16,32")):
            calls.clear()
            exec(self.cell("run"), dict(ns, CUDA=cuda, WHY_CPU=why))
            self.assertEqual(calls, [("run", page, "--widths", widths, "--steps", "450", "--blocks",
                                      "schedule=adaptive restraint=abf w_landmark=4", "--plotlyjs", "cdn", "--save", kept)])
        ns.update(CUDA=None, WHY_CPU="this session has no GPU")
        exec(self.cell("run"), ns)                   # the show cell reads the run cell's PAGE and KEPT
        calls.clear()
        exec(self.cell("show"), ns)
        self.assertEqual(calls, [("show", page)])
        calls.clear()
        named = self.cell("show").replace("VERTEBRA = None", "VERTEBRA = 3", 1)
        self.assertNotEqual(named, self.cell("show"))
        exec(named, ns)
        other = os.path.join(self.base, "anneal_demo_3.html")
        self.assertEqual(calls, [("run", other, "--load", kept, "--vertebra", "3", "--plotlyjs", "cdn"), ("show", other)])

    def test_the_settings_line_from_the_pipeline_page_sets_the_widths_the_steps_and_the_blocks(self):
        calls = []
        ns = dict(os=os, OUT=self.base, CUDA=None, WHY_CPU="no GPU", run_demo=lambda *words: calls.append(words))
        for line, widths, steps, blocks in (
                ("normalise=clip widths=16:32:64 schedule=cyclic steps=100 seed=2", "16,32,64", "100",
                 ["--blocks", "normalise=clip schedule=cyclic seed=2"]),
                ("widths=auto steps=50", "8,16,32", "50", [])):
            calls.clear()
            exec(self.cell("run").replace('SETTINGS = ""', "SETTINGS = %r" % line, 1), dict(ns))
            self.assertEqual(calls[0][1:5], ("--widths", widths, "--steps", steps))
            self.assertEqual(list(calls[0][5:-4]), blocks)

    def test_the_test_cell_tests_the_kept_run_and_shows_its_page(self):
        calls = []
        kept = os.path.join(self.base, "anneal_demo.pkl")
        exec(self.cell("test"), dict(os=os, OUT=self.base, KEPT=kept, run_demo=lambda *words: calls.append(("run",) + words),
                                     show=lambda page: calls.append(("show", page))))
        page = os.path.join(self.base, "anneal_test.html")
        self.assertEqual(calls, [("run", page, "--load", kept, "--test", "--plotlyjs", "cdn"), ("show", page)])

    def test_the_sign_in_shows_the_code_large_with_a_button_that_copies_it_and_opens_github(self):
        shown = []
        display = types.ModuleType("IPython.display")
        display.HTML, display.display = (lambda text: text), shown.append
        ipython = types.ModuleType("IPython")
        ipython.display = display
        code, link = "WDJB-</script><b>", "https://github.com/login/device"
        with mock.patch.dict(sys.modules, {"IPython": ipython, "IPython.display": display}), \
                redirect_stdout(io.StringIO()) as said:
            self.ns["show_code"](link, code)
        self.assertIn("open %s and enter the code %s" % (link, code), said.getvalue())
        (box,) = shown
        self.assertIn(">WDJB-&lt;/script&gt;&lt;b&gt;</div>", box)          # the code as text, not as markup
        self.assertEqual(box.count("</script>"), 1)                          # the box's own, at its end
        self.assertIn('var code = "WDJB-\\u003c/script>\\u003cb>", link = "%s";' % link, box)
        self.assertIn('window.open(link, "github-sign-in", "popup,width=520,height=720")', box)
        self.assertIn("navigator.clipboard.writeText(code)", box)
        self.assertIn('<a href="%s" target="_blank">' % link, box)
        button = box.split('<button id="', 1)[1].split('"', 1)[0]
        self.assertIn('document.getElementById("%s")' % button, box)


if __name__ == "__main__":
    unittest.main()
