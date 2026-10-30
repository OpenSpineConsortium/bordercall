"""The annealing demo (autoanatomist/demo.py) on the sizes the model tests use: a crop of 16 by 20
by 12 voxels and two phantoms of three levels.

    python -m unittest tests.test_autoanatomist_demo -v        # from the repository's root, in the venv

The demo's network is train.train's for its one measurement with the naming layer off, every
weight to the bit (the smoke run itself trains all seven measurements with the naming layer on).
Its snapshots fall before the first step, every few steps and after the last, each with the
schedule's w and lambda of the step just taken, the ladder's own input to the mask branch at that
lambda (the target vertebra's own mask before the first step) and the CT-only path's reading by the
network after that many steps, with each width the length between its points. demo.run reads the
held-out crops against the oracle and puts the display crop's CT under the mask input, its figure
has one frame per snapshot, a slider over them, each snapshot's dots on the schedule's curves and
the oracle's line where the oracle put it (where plotly is installed, as it is in Colab), and its
command says before it trains that it needs plotly.

The notebook that runs it in Colab (notebooks/anneal_demo.ipynb) is kept with no outputs and asks
Colab for a T4, and its setup cell, run against a stand-in for Colab's modules, reads a missing
secret as none, hands git the token through a credential helper and nowhere else, unpacks a ZIP as
GitHub makes one, installs the four packages bordercall pins and, where nvidia-smi lists a GPU, the
GPU build of the same jaxlib for the CUDA version whose build the image carries, taking the other
versions' builds out first, installs nothing when they are there, stops with the words to restart
Colab's session when pip replaced a package the session had imported, trains on the CPU and says
why when JAX does not start on the GPU in a child process, and asks for plotly before training.
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
import types
import unittest
import zipfile
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
    @classmethod
    def setUpClass(cls):
        from autoanatomist import demo as D
        cls.cfg = tiny_config()
        cls.ex, cls.held = tiny_examples(cls.cfg)
        with mock.patch.object(D, "examples", lambda cfg: (cls.ex, cls.held)):
            cls.demo = D.run(STEPS, EVERY, cls.cfg, log_every=0)
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
        last = self.fig.frames[-1]
        np.testing.assert_allclose(np.column_stack([last.data[0].x, last.data[0].y, last.data[0].z]),
                                   self.demo.snapshots[-1].points[1])
        self.assertAlmostEqual(last.data[1].opacity, max(self.demo.snapshots[-1].w, 0.0))
        self.assertIn("After %d of %d steps" % (STEPS, STEPS), last.layout.title.text)

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


def notebook():
    with open(NOTEBOOK) as f:
        return json.load(f)


def notebook_cells():
    return notebook()["cells"]


def setup_definitions() -> str:
    """The notebook's setup cell up to the lines that act: its imports, constants and functions."""
    code = [c for c in notebook_cells() if c["cell_type"] == "code"]
    head, sep, _ = "".join(code[0]["source"]).partition("\nROOT = ")
    assert sep, "the setup cell no longer ends by setting ROOT"
    return head


def setup_namespace(base: str) -> dict:
    ns = {}
    with mock.patch.dict(os.environ):                 # the cell sets JAX_PLATFORMS for the session
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

    def test_with_no_secret_it_unpacks_a_zip_as_github_makes_one_and_keeps_it(self):
        top = "bordercall-claude-project-thread-5hj0q5"
        upload = os.path.join(self.base, top + ".zip")
        with zipfile.ZipFile(upload, "w") as z:
            for rel in ("autoanatomist/demo.py", "requirements-autoanatomist.txt"):
                z.write(os.path.join(ROOT, rel), top + "/" + rel)
        here = os.getcwd()
        os.chdir(self.base)
        try:
            with mock.patch.dict(sys.modules, colab_stand_in(upload=upload)):
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

    def test_it_asks_colab_for_a_t4(self):
        meta = notebook()["metadata"]
        self.assertEqual(meta["accelerator"], "GPU")
        self.assertEqual(meta["colab"]["gpuType"], "T4")

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
        new = "| NVIDIA-SMI 580.82.07    Driver Version: 580.82.07    CUDA Version: 13.0 |\n"
        old = new.replace("13.0", "12.4")
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
        failed = ("Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\n"
                  "RuntimeError: Unable to initialize backend 'cuda': CUDA_ERROR_SYSTEM_DRIVER_MISMATCH (you may "
                  "need to uninstall the failing plugin package, or set JAX_PLATFORMS=cpu to skip this backend.)\n")
        for answer, why in ((child(0, "gpu\n"), None), (child(0, "cpu\n"), "JAX chose its cpu backend"),
                            (child(1, err=failed), failed.splitlines()[-1])):
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
            backend = subprocess.run([sys.executable, "-c", "import jax; print(jax.default_backend())"],
                                     capture_output=True, text=True, check=True).stdout.split()[-1]
            why = self.ns["why_no_gpu"]()
        self.assertEqual(why is None, backend == "gpu")
        if why is not None:
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
        listing = "GPU 0: Tesla T4 (UUID: GPU-00000000-0000-0000-0000-000000000000)\n"
        for run, expected in ((lists(listing), True), (lists(""), False), (missing, False)):
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


if __name__ == "__main__":
    unittest.main()
