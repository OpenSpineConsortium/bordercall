"""The annealing demo (autoanatomist/demo.py) on the sizes the model tests use: a crop of 16 by 20
by 12 voxels and two phantoms of three levels.

    python -m unittest tests.test_anneal_demo -v        # from the repository's root, in the venv

The demo's network is train.train's for its one measurement with the naming layer off, every
weight to the bit (the smoke run itself trains all seven measurements with the naming layer on).
Its snapshots fall before the first step, every few steps and after the last, each with the
schedule's w and lambda of the step just taken, the ladder's own input to the mask branch at that
lambda (the target vertebra's own mask before the first step) and the CT-only path's reading by the
network after that many steps, with each width the length between its points. demo.run reads the
held-out crops against the oracle and puts the display crop's CT under the mask input. Its figure,
frame by frame, draws the shown vertebra's own CT as the surface, the mask input at the opacity w
(whole at the start), the schedule's dots on its curves, the width line up to the slider's step
for the shown vertebra and the title's numbers for it, with one frame per snapshot and a slider
over them (where plotly is installed, as it is in Colab). The command says before it trains that
it needs plotly, and writes the page and, asked to, the run's record.

The notebook that runs it in Colab (notebooks/anneal_demo.ipynb) is kept with no outputs and asks
Colab for a T4. Its setup cell's functions, run against a stand-in for Colab's modules, read a
missing secret as none, sign in with GitHub's device flow (the code shown, the token returned and
never printed, a refusal or a decline falling back to the ZIP), hand git the token through a
credential helper and nowhere else, unpack a ZIP as GitHub makes one and install the four packages
bordercall pins; and prepare(), the one call the cell makes before it imports JAX, run on stand-ins
for Colab's GPU and CPU images, installs the GPU build of the pinned jaxlib for the CUDA version
whose build the image carries after taking the other versions' builds out, installs nothing when
the pins are there, stops with the words to restart Colab's session when pip replaced a package the
session had imported, asks for plotly before anything slow, and leaves JAX on the CPU, saying why,
when JAX does not start on the GPU in a child process.
"""
from __future__ import annotations

import argparse
import ast
import functools
import importlib.machinery
import io
import json
import os
import subprocess
import sys
import tempfile
import types
import unittest
import urllib.error
import urllib.parse
import zipfile
from contextlib import redirect_stdout
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

    def test_every_snapshot_holds_the_ladders_input_at_its_lambda(self):
        from autoanatomist import demo as D, ladder
        i, middle = D.display_crop(self.ex), self.cfg.shape[0] // 2
        self.assertGreater(len({snap.lam for snap in self.snapshots}), 2)
        for snap in self.snapshots:
            out = ladder.degrade(jnp.asarray(self.ex.masks[i:i + 1]), jnp.asarray(self.ex.hu[i:i + 1]),
                                 jnp.float32(snap.lam), spacing_mm=self.cfg.spacing)
            np.testing.assert_array_equal(snap.given, np.asarray(out[0, middle, :, :, 0]))
            self.assertEqual(snap.given.shape, self.cfg.shape[1:])

    def test_before_the_first_step_the_mask_branch_is_given_the_target_vertebras_own_mask(self):
        from autoanatomist import demo as D
        i, middle = D.display_crop(self.ex), self.cfg.shape[0] // 2
        first = self.snapshots[0]
        self.assertEqual(first.lam, 0.0)
        target, every = self.ex.masks[i, middle, :, :, 0], self.ex.masks[i, middle, :, :, 1]
        self.assertFalse(np.allclose(target, every))           # so the cut tells the two channels apart
        np.testing.assert_allclose(first.given, target, atol=1e-6)

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

    def test_the_display_crop_is_the_first_phantoms_middle_vertebra(self):
        from autoanatomist import demo as D
        first = self.ex.spines()[0]
        self.assertEqual(D.display_crop(self.ex), int(first[1]))


@unittest.skipUnless(HAVE_JAX and HAVE_PLOTLY, "jax, flax and plotly are not all installed")
class TheFigure(unittest.TestCase):
    """The figure of vertebra 1, so that a figure drawn from vertebra 0's numbers shows."""

    @classmethod
    def setUpClass(cls):
        from autoanatomist import demo as D
        cls.cfg, cls.ex, cls.held, cls.demo = tiny_demo()
        cls.fig = D.figure(cls.demo, vertebra=1)

    def test_the_run_reads_the_held_out_crops_against_the_oracle_and_keeps_the_display_crops_ct(self):
        from autoanatomist import demo as D, ladder
        i = D.display_crop(self.ex)
        np.testing.assert_array_equal(self.demo.given_ct, self.ex.hu[i, self.cfg.shape[0] // 2, :, :, 0])
        np.testing.assert_array_equal(self.demo.hu, self.held.hu[..., 0])
        np.testing.assert_array_equal(self.demo.reference_points, self.held.targets)
        np.testing.assert_array_equal(self.demo.reference_widths, self.held.values[:, 0])
        self.assertEqual(self.demo.levels, [r.level for r in self.held.readings])
        for mine, theirs in zip(self.demo.ticks, self.held.frames[0].axis_ticks()):
            np.testing.assert_array_equal(mine, theirs)
        schedule = ladder.Schedule(STEPS)
        np.testing.assert_array_equal(np.column_stack([self.demo.w, self.demo.lam]),
                                      [schedule.at(s) for s in range(STEPS)])
        self.assertEqual((self.demo.steps, [s.step for s in self.demo.snapshots]), (STEPS, [0, 3, 6, 7]))

    def test_each_snapshots_dots_lie_on_the_schedules_curves(self):
        lam_curve, w_curve = self.fig.data[5], self.fig.data[6]
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

    def test_the_frames_move_the_network_and_the_mask_branch_and_leave_the_ct_and_the_reference(self):
        moving = list(self.fig.frames[0].traces)
        self.assertEqual(moving, [2, 4, 7, 9])
        kinds = [self.fig.data[i].type for i in moving]
        self.assertEqual(kinds, ["scatter3d", "heatmap", "scatter", "scatter"])
        self.assertEqual(self.fig.data[0].type, "isosurface")
        self.assertEqual(self.fig.data[3].type, "heatmap")
        for frame, snap in zip(self.fig.frames, self.demo.snapshots):
            line = frame.data[0]
            np.testing.assert_allclose(np.column_stack([line.x, line.y, line.z]), snap.points[1])

    def test_the_surface_is_the_shown_vertebras_own_ct_at_the_bone_level(self):
        from scipy import ndimage
        from autoanatomist import gates
        iso = self.fig.data[0]
        self.assertFalse(np.allclose(self.demo.hu[0], self.demo.hu[1]))   # so another vertebra's CT would show
        smoothed = ndimage.gaussian_filter(np.asarray(self.demo.hu[1], np.float32), 1.0)
        np.testing.assert_array_equal(np.asarray(iso.value), smoothed.ravel())
        self.assertEqual((iso.isomin, iso.isomax), (gates.BONE_HU, gates.BONE_HU))
        for axis, ticks in zip((iso.x, iso.y, iso.z), np.meshgrid(*self.demo.ticks, indexing="ij")):
            np.testing.assert_array_equal(np.asarray(axis), ticks.ravel())

    def test_every_frame_draws_the_mask_input_at_its_weight_whole_at_the_start(self):
        weights = [snap.w for snap in self.demo.snapshots]
        self.assertEqual(weights[0], 1.0)
        self.assertTrue(any(0.0 < w < 1.0 for w in weights))   # so a weight between the ends is drawn as it is
        self.assertEqual(self.fig.data[4].opacity, 1.0)
        for frame, snap in zip(self.fig.frames, self.demo.snapshots):
            self.assertEqual(frame.data[1].opacity, max(snap.w, 0.0))
            np.testing.assert_array_equal(np.asarray(frame.data[1].z), snap.given.T)

    def test_every_frames_width_line_runs_to_its_step_for_the_shown_vertebra(self):
        snaps = self.demo.snapshots
        self.assertFalse(np.allclose([s.widths[0] for s in snaps], [s.widths[1] for s in snaps]))
        lines = [(0, self.fig.data[9])] + [(k, frame.data[3]) for k, frame in enumerate(self.fig.frames)]
        for k, line in lines:
            self.assertEqual(list(line.x), [s.step for s in snaps[:k + 1]])
            np.testing.assert_allclose(list(line.y), [s.widths[1] for s in snaps[:k + 1]])

    def test_every_frames_title_gives_the_shown_vertebras_numbers_at_its_step(self):
        levels, refs = self.demo.levels, self.demo.reference_widths
        self.assertNotEqual(levels[0], levels[1])
        for frame, snap in zip(self.fig.frames, self.demo.snapshots):
            text = frame.layout.title.text
            self.assertIn("After %d of %d steps: λ %.2f, w %.2f." % (snap.step, STEPS, snap.lam, snap.w), text)
            self.assertIn("%s's end-plate width %.1f mm from the CT alone" % (levels[1], snap.widths[1]), text)
            self.assertIn("the reference %.1f mm" % refs[1], text)
            self.assertTrue(text.endswith("held-out vertebrae %.1f mm" % np.mean(np.abs(snap.widths - refs))))
        self.assertEqual(self.fig.layout.title.text, self.fig.frames[0].layout.title.text)

    def test_the_oracles_line_is_drawn_where_the_oracle_put_it(self):
        ref = self.fig.data[1]
        np.testing.assert_allclose(np.column_stack([ref.x, ref.y, ref.z]), self.demo.reference_points[1])
        self.assertEqual(self.fig.data[8].y[0], float(self.demo.reference_widths[1]))

    def test_unless_named_the_vertebra_shown_is_the_one_with_the_median_error_at_the_end(self):
        from autoanatomist import demo as D
        errors = np.abs(self.demo.snapshots[-1].widths - self.demo.reference_widths)
        k = self.demo.typical()
        self.assertEqual(errors[k], sorted(errors)[(len(errors) - 1) // 2])
        fig = D.figure(self.demo)
        ref = fig.data[1]
        np.testing.assert_allclose(np.column_stack([ref.x, ref.y, ref.z]), self.demo.reference_points[k])

    def test_the_mask_input_lies_over_the_same_crops_ct_on_the_same_cut(self):
        under, over = self.fig.data[3], self.fig.data[4]
        np.testing.assert_array_equal(np.asarray(under.z), self.demo.given_ct.T)
        np.testing.assert_array_equal(np.asarray(over.z), self.demo.snapshots[0].given.T)
        self.assertEqual(self.demo.given_ct.shape, self.demo.snapshots[0].given.shape)


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

    @unittest.skipUnless(HAVE_PLOTLY, "plotly is not installed")
    def test_it_trains_as_told_and_writes_the_page_and_the_runs_record(self):
        from autoanatomist import demo as D
        _, _, _, demo = tiny_demo()
        with tempfile.TemporaryDirectory() as out, mock.patch.object(D, "run", return_value=demo) as run, \
                redirect_stdout(io.StringIO()):
            page, kept = os.path.join(out, "demo.html"), os.path.join(out, "demo.json")
            self.assertEqual(D.main(["demo", page, "--steps", "7", "--widths", "4,8,8", "--record", kept]), 0)
            self.assertGreater(os.path.getsize(page), 0)
            with open(kept) as f:
                record = json.load(f)
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

    def test_the_token_reaches_git_through_the_credential_helper_alone(self):
        seen = {}

        def run(argv, env=None, check=False, **kw):
            seen["argv"], seen["env"] = argv, env
        with mock.patch.object(self.ns["subprocess"], "run", run):
            self.ns["clone"]("not-a-token", "main")
        self.assertNotIn("not-a-token", " ".join(seen["argv"]))
        self.assertEqual(seen["env"]["GITHUB_TOKEN"], "not-a-token")
        helper = [a for a in seen["argv"] if a.startswith("credential.helper=")][0].split("=", 1)[1]
        env = dict(os.environ, GITHUB_TOKEN="not-a-token", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        out = subprocess.run(["git", "-c", "credential.helper=" + helper, "credential", "fill"], cwd=self.base,
                             input="protocol=https\nhost=github.com\n\n", capture_output=True, text=True,
                             env=env, check=True).stdout
        self.assertIn("username=x-access-token\n", out)
        self.assertIn("password=not-a-token\n", out)

    def fetch(self, github, secret=None):
        """fetch() with no clone yet, the secret in Colab's Secrets, the stand-in for GitHub's sign-in,
        a clone that only records what it was given and a ZIP that is never asked for in earnest:
        what fetch returned and printed, the clones and the waits between polls."""
        clones, waits, said = [], [], io.StringIO()

        def clone(secret, ref):
            clones.append((secret, ref))
            os.makedirs(os.path.join(self.ns["CLONE"], "autoanatomist"), exist_ok=True)
            open(os.path.join(self.ns["CLONE"], "autoanatomist", "demo.py"), "w").close()
        with mock.patch.dict(sys.modules, colab_stand_in(secret=secret)), \
                mock.patch.dict(self.ns, clone=clone, unpack_upload=lambda: "the ZIP"), \
                mock.patch.object(self.ns["urllib"].request, "urlopen", github.urlopen), \
                mock.patch.object(self.ns["time"], "sleep", waits.append), redirect_stdout(said):
            got = self.ns["fetch"]()
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
        with mock.patch.dict(self.ns, installed=carried.get), mock.patch.object(self.ns["subprocess"], "run", pip), \
                mock.patch.object(self.ns["importlib"].metadata, "packages_distributions", lambda: {}):
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

    def test_pip_replacing_an_imported_package_asks_for_a_restart(self):
        versions = {"jax": "0.1", "numpy": "1.0"}

        def pip(*a, **k):
            versions.update(jax="9.9", numpy="2.0")
        owners = {"numpy": ["numpy"], "jax": ["jax"]}
        with mock.patch.dict(self.ns, installed=versions.get), \
                mock.patch.object(self.ns["importlib"].metadata, "packages_distributions", lambda: owners), \
                mock.patch.dict(sys.modules, {"numpy": np}), mock.patch.object(self.ns["subprocess"], "run", pip):
            with self.assertRaises(SystemExit) as stop:
                self.ns["install"]({"jax": "9.9"})
        self.assertIn("numpy", str(stop.exception))
        self.assertIn("Restart session", str(stop.exception))

    def test_pip_replacing_nothing_imported_goes_on(self):
        versions = {"jax": "0.1"}

        def pip(*a, **k):
            versions.update(jax="9.9")
        with mock.patch.dict(self.ns, installed=versions.get), \
                mock.patch.object(self.ns["importlib"].metadata, "packages_distributions", lambda: {"numpy": ["numpy"]}), \
                mock.patch.object(self.ns["subprocess"], "run", pip):
            self.ns["install"]({"jax": "9.9"})
        self.assertEqual(versions["jax"], "9.9")

    def prepare(self, runtime, colab=True, plotly=True):
        """prepare() on a stand-in runtime, bordercall fetched already and plotly there or not: what it
        returned and JAX_PLATFORMS after it."""
        found = types.ModuleType("plotly")
        found.__spec__ = importlib.machinery.ModuleSpec("plotly", None)
        with mock.patch.dict(self.ns, in_colab=lambda: colab, fetch=lambda: ROOT, repository_root=lambda: ROOT,
                             installed=runtime.installed), \
                mock.patch.object(self.ns["subprocess"], "run", runtime.run), \
                mock.patch.object(self.ns["importlib"].metadata, "packages_distributions", lambda: {}), \
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

    def test_the_cell_settles_all_of_it_before_this_session_imports_jax(self):
        def imports(node):
            if isinstance(node, ast.Import):
                return {alias.name.split(".")[0] for alias in node.names}
            if isinstance(node, ast.ImportFrom):
                return {(node.module or "").split(".")[0]}
            return set()
        late = {"jax", "autoanatomist"}
        body = ast.parse(setup_source()).body
        acts = [i for i, node in enumerate(body) if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call)
                and getattr(node.value.func, "id", None) == "prepare"]
        jax_at = [i for i, node in enumerate(body) if imports(node) & late]
        self.assertEqual(len(acts), 1)
        self.assertTrue(jax_at)
        self.assertLess(acts[0], min(jax_at))
        inside = [node for f in body if isinstance(f, ast.FunctionDef) for node in ast.walk(f) if imports(node) & late]
        self.assertEqual(inside, [])


if __name__ == "__main__":
    unittest.main()
