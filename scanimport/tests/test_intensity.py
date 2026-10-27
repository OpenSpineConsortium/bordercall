"""The mask-free mode on synthetic CTs of known size: the blurred-step fit recovers a surface it
drew and is neither cancelled nor steered by one profile it cannot describe, the half-maximum
edge lies outward as the module's text says and the fit moves it back, the same volume gives the
same chords, a DICOM series gives what its NIfTI gives, a fatty body's marrow is not taken for the
canal, a contrast-filled vessel in every section hides no disc, a shallow dip far from any disc
(a sacral remnant, a ripple along a fused block) is no disc, metal leaves its vertebra
unmeasured, and what cannot be measured says so. Each phantom is three vertebrae, so one body
lies between two discs."""
import contextlib
import io
import json
import math
import os
import tempfile
import unittest

import numpy as np
from scipy.special import ndtr

from scanimport import edges as E
from scanimport import intensity as I
from scanimport.__main__ import main
from scanimport.readers import Volume
from scanimport.tests import dicom_files as DF
from scanimport.tests import phantom as P

SEVEN = ("endplate", "endplate_lower", "endplate_depth", "endplate_lower_depth", "h_post", "canal_w", "canal_ap")
S = P.Shape()
TRUTH = dict(zip(SEVEN, (S.W, S.W, S.D, S.D, S.H, S.CW, S.CD)))
# A clinical CT's vertebra: a thin dense cortex blurred by a point spread of 1 mm SD, with noise.
REALISTIC = dict(blur_mm=1.0, cortex=1500.0, cortex_mm=0.5, noise_hu=15.0)
# A sharper scan of a 1 mm cortex of 800 HU, less dense than edges.CORTICAL_HU.
SHARP = dict()
# Rendered one point per voxel, which is quicker, for the phantoms that test finding, not the
# chords' last tenth of a millimetre.
QUICK = dict(sub=1, blur_mm=1.0)
# hu_column's default lean of the column, to place things in a vertebra's own frame.
TILT = P.rotation((1.0, 0.3, 0.0), 18.0)


def model(x, a, t, sigma, y0=40.0, y1=E.CORTICAL_HU, y2=230.0):
    """Treece's blurred step (edges.py, THE MODEL), sampled at x."""
    return y0 + (y1 - y0) * ndtr((x - a) / sigma) + (y2 - y1) * ndtr((x - a - t) / sigma)


def errors(bodies):
    measured = [b for b in bodies if b.values]
    return {m: measured[0].values[m] - TRUTH[m] for m in SEVEN}, measured


def local_to_voxel(affine, vertebra, local):
    """The voxel of a point given in the frame of vertebra 0, 1 or 2 of hu_column's default
    column (local x to the right, y anterior, the posterior body wall at y = 0)."""
    ez = TILT @ np.array([0.0, 0.0, 1.0])
    world = TILT @ np.asarray(local, float) - 36.0 * vertebra * ez
    return np.linalg.solve(affine[:3, :3], world - affine[:3, 3])


def with_vessel(hu, affine, value=420.0, radius=12.5, at=(-14.0, 47.5)):
    """The volume with a contrast-filled vessel along the column in front of it, clear of the
    body: an aorta in the arterial phase, 25 mm across, at local (x, y) = at."""
    ez = TILT @ np.array([0.0, 0.0, 1.0])
    axis = TILT @ np.array([at[0], at[1], 0.0])
    out = hu.copy()
    ii, jj = np.meshgrid(np.arange(hu.shape[0]), np.arange(hu.shape[1]), indexing="ij")
    for k in range(hu.shape[2]):
        ijk = np.stack([ii.ravel(), jj.ravel(), np.full(ii.size, k)], axis=1)
        d = ijk @ affine[:3, :3].T + affine[:3, 3] - axis
        radial = np.linalg.norm(d - np.outer(d @ ez, ez), axis=1).reshape(ii.shape)
        out[:, :, k][radial <= radius] = value
    return out


class EdgeModel(unittest.TestCase):
    def test_profiles_drawn_by_the_model_give_back_their_surface_and_blur(self):
        x = E.positions()
        drawn = np.array([0.2, 0.35, 0.4, 0.5, 0.55, 0.7])
        got = E.fit(np.array([model(x, a, 0.6, 0.9) for a in drawn]), x)
        self.assertEqual(got.reason, "")
        self.assertAlmostEqual(got.sigma, 0.9, places=9)
        np.testing.assert_allclose(got.surfaces, drawn, atol=1e-9)
        self.assertAlmostEqual(got.shift, float(np.median(drawn)), places=9)

    def test_a_cortex_less_dense_than_assumed_puts_the_surface_inward_and_a_denser_one_outward(self):
        x = E.positions()
        drawn = np.full(6, 0.4)
        thin = E.fit(np.array([model(x, a, 0.6, 1.0, y1=800.0) for a in drawn]), x)
        dense = E.fit(np.array([model(x, a, 0.6, 1.0, y1=1800.0) for a in drawn]), x)
        self.assertGreater(thin.shift, 0.4)
        self.assertLess(dense.shift, 0.4)
        # within the cortex's thickness either way, as the docstring says
        self.assertLess(abs(thin.shift - 0.4), 0.6)
        self.assertLess(abs(dense.shift - 0.4), 0.6)

    def test_one_profile_into_dense_bone_neither_cancels_nor_steers_the_blur(self):
        # Nineteen wall profiles drawn by the model with noise, and one that runs into solid bone
        # denser than the cortex assumed, as a ray through a bone island or an ossified ligament
        # does. A plain sum over the profiles let it pull the blur to 0.7 mm at 1,500 HU and
        # cancel the fit at 1,800 HU.
        x = E.positions()
        rng = np.random.default_rng(3)
        good = [model(x, 0.4, 0.6, 1.0) + rng.normal(0.0, 10.0, len(x)) for _ in range(19)]
        alone = E.fit(np.array(good), x)
        self.assertEqual((alone.sigma, alone.shift), (1.0, 0.4))
        for dense in (1500.0, 1800.0):
            step = 15.0 + (dense - 15.0) * ndtr(x / 1.0)
            got = E.fit(np.array(good + [step]), x)
            self.assertEqual(got.reason, "", dense)
            self.assertEqual((got.sigma, got.shift), (alone.sigma, alone.shift), dense)

    def test_too_few_profiles_are_refused_with_the_reason(self):
        x = E.positions()
        got = E.fit(np.array([model(x, 0.4, 0.6, 0.9)] * 3), x)
        self.assertIn("fewer than", got.reason)
        self.assertEqual(got.shift, 0.0)

    def test_the_density_trial_runs_and_says_the_density_it_chose(self):
        x = E.positions()
        drawn = np.array([0.3, 0.35, 0.4, 0.45, 0.5, 0.4])
        got = E.fit_density(np.array([model(x, a, 0.6, 1.0) for a in drawn]), x)
        self.assertEqual(got.reason, "")
        self.assertEqual(got.cortical, E.CORTICAL_HU)
        self.assertAlmostEqual(got.shift, float(np.median(drawn)), places=9)

    def test_the_half_maximum_edge_lies_outward_by_what_the_module_says(self):
        # intensity.py, WHAT IT CANNOT DO: with the threshold half way from the soft tissue (40 HU)
        # to the blurred peak of a 1,200 HU cortex, the edge lies outward by up to about three
        # quarters of the blur's SD over trabecular bone of 230 HU and about nine tenths over an
        # osteoporotic core of 100 HU, by about a quarter of it over either at a cortex one full
        # width at half maximum thick, and outward of a thin isolated plate by half the width less
        # its thickness.
        sigma = 1.0
        fwhm = 2.0 * math.sqrt(2.0 * math.log(2.0)) * sigma
        x = np.arange(-8.0, 10.0, 0.001)

        def outward(t, inside):
            y = model(x, 0.0, t, sigma, y2=inside)
            half = 40.0 + 0.5 * (y.max() - 40.0)
            return -float(x[np.flatnonzero(y >= half)[0]])

        over_trabecular = [outward(t, 230.0) for t in np.arange(0.1, 3.0, 0.1)]
        self.assertGreater(max(over_trabecular), 0.7 * sigma)
        self.assertLess(max(over_trabecular), 0.8 * sigma)
        over_osteoporotic = [outward(t, 100.0) for t in np.arange(0.1, 3.0, 0.1)]
        self.assertGreater(max(over_osteoporotic), 0.85 * sigma)
        self.assertLess(max(over_osteoporotic), 1.0 * sigma)
        self.assertAlmostEqual(outward(fwhm, 230.0), 0.25 * sigma, delta=0.05 * sigma)
        self.assertAlmostEqual(outward(fwhm, 100.0), 0.25 * sigma, delta=0.05 * sigma)
        self.assertAlmostEqual(outward(0.1, 40.0), (fwhm - 0.1) / 2.0, delta=0.01)
        self.assertLess(outward(0.1, 40.0), 1.15 * sigma)

    def test_a_crossing_is_found_between_samples(self):
        s = np.arange(5.0)
        self.assertAlmostEqual(E.crossing(np.array([900, 700, 300, 100, 50.0]), s, 500.0, True), 1.5)
        self.assertAlmostEqual(E.crossing(np.array([0, 100, 300, 900, 900.0]), s, 600.0, False), 2.5)
        self.assertIsNone(E.crossing(np.zeros(5), s, 500.0, True))

    def test_each_chord_moves_with_its_two_surfaces(self):
        fits = {"walls": E.SurfaceFit(1.0, np.zeros(9), 0.3, 9), "plates": E.SurfaceFit(1.0, np.zeros(9), 0.5, 9),
                "canal": E.SurfaceFit(1.0, np.zeros(9), 0.2, 9)}
        got, notes = I.corrected({m: 10.0 for m in SEVEN}, fits)
        self.assertEqual(notes, {})
        self.assertAlmostEqual(got["endplate"], 9.4)
        self.assertAlmostEqual(got["endplate_depth"], 9.5)
        self.assertAlmostEqual(got["h_post"], 9.0)
        self.assertAlmostEqual(got["canal_w"], 10.4)
        fits["canal"] = E.SurfaceFit(math.nan, np.zeros(0), 0.0, 2, "2 profiles, fewer than 5")
        got, notes = I.corrected({m: 10.0 for m in SEVEN}, fits)
        self.assertEqual(got["canal_ap"], 10.0)
        self.assertIn("no blurred-step fit for the canal", notes["canal_ap"])
        self.assertEqual(got["endplate"], 9.4)


class Canal(unittest.TestCase):
    @staticmethod
    def slice_of(*rings):
        """One axial slice at 1 mm of soft tissue holding bony rings, each (centre i, centre j,
        outer half-axes, inner half-axes, contents HU); +j is anterior."""
        ii, jj = np.meshgrid(np.arange(120), np.arange(120), indexing="ij")
        sl = np.full(ii.shape, 40.0)
        for ci, cj, (a, b), (ai, bi), inside in rings:
            sl[((ii - ci) / a) ** 2 + ((jj - cj) / b) ** 2 <= 1.0] = 300.0
            sl[((ii - ci) / ai) ** 2 + ((jj - cj) / bi) ** 2 <= 1.0] = inside
        return sl[:, :, None]

    def candidates(self, hu):
        return I.canal_candidates(hu, np.eye(4), np.ones(hu.shape, bool))[0]

    def test_a_fatty_marrow_in_front_of_the_canal_is_not_the_canal(self):
        # a small body's marrow at 40 HU (pi x 13 x 10 = 408 mm2, under the canal-sized cap) in
        # front of a canal of CSF in its bony ring: both are bone-enclosed holes of canal density
        hu = self.slice_of((60, 70, (15, 12), (13, 10), 40.0), (60, 45, (11, 9), (9, 7), 15.0))
        got = self.candidates(hu)
        self.assertEqual(len(got), 1)
        self.assertAlmostEqual(float(got[0].centre[1]), 45.0, delta=0.5)

    def test_a_hole_larger_than_any_canal_is_not_a_candidate(self):
        # a lumbar body's fatty marrow, pi x 20 x 16 = 1,005 mm2, alone in the slice
        hu = self.slice_of((60, 60, (22, 18), (20, 16), 40.0))
        self.assertEqual(self.candidates(hu), [])

    def test_a_chain_of_holes_larger_than_any_canal_is_said(self):
        # a tube of 15 HU, about 500 mm2 across, above the largest canal of Panjabi's means and
        # under the candidates' cap, in a bony ring through 40 slices
        ii, jj = np.meshgrid(np.arange(90), np.arange(90), indexing="ij")
        r = np.hypot(ii - 45.0, jj - 45.0)
        sl = np.where(r <= 12.6, 15.0, np.where(r <= 16.0, 300.0, np.where(r <= 40.0, 40.0, -1000.0)))
        hu = np.repeat(sl[:, :, None], 40, axis=2).astype(np.float32)
        found = I.find(hu, np.eye(4), I.body_outline(hu))
        self.assertIsNotNone(found.centreline)
        self.assertTrue(any("median area" in q for q in found.problems), found.problems)

    def test_a_chain_shorter_than_a_millimetre_gives_no_centreline(self):
        chain = [I.Candidate(k, np.array([0.0, 0.0, 0.25 * k]), 100.0) for k in range(3)]
        self.assertIsNone(I.centreline_of(chain))


class Discs(unittest.TestCase):
    @staticmethod
    def column_weight():
        """A weight every millimetre: bodies of 1,000, discs of 100 nine samples wide, 36 mm apart."""
        w = np.full(230, 1000.0)
        for c in (4, 40, 76, 112, 148, 184, 220):
            w[c - 4:c + 5] = 100.0
        return w

    def test_a_dense_section_hides_only_the_disc_beside_it(self):
        w = self.column_weight()
        self.assertEqual(I.find_discs(w), [40, 76, 112, 148, 184, 220])
        # the spike reference spans Radnostics' 40 mm window, so the discs 24 and 38 mm from a
        # dense section are kept; the one beside it fails the spike test
        w[150:160] = 3500.0
        self.assertEqual(I.find_discs(w), [40, 76, 112, 184, 220])

    def test_a_weight_every_section_shares_moves_no_disc(self):
        w = self.column_weight()
        w[150:160] = 3500.0
        want = I.find_discs(w)
        for shared in (500.0, 900.0, 1500.0):
            self.assertEqual(I.find_discs(w + shared), want, shared)

    def test_a_shallow_dip_with_no_deeper_one_near_is_no_disc(self):
        # The discs at 112 and 148 fused into one block 100 mm long, with a ripple of 5 per cent in
        # its middle, more than 20 mm from any disc; and, below the last disc, a sacrum whose
        # rudimentary discs dip to 90 per cent of its bodies every 30 mm. Each lone dip is its own
        # moving minimum; measured from it alone, the ripple and the remnants were taken for discs.
        fused = self.column_weight()
        fused[108:153] = 1000.0
        fused[128:131] = 950.0
        sacrum = np.r_[self.column_weight()[:189], np.tile(np.r_[np.full(26, 1000.0), np.full(4, 900.0)], 3)]
        for w, want in ((fused, [40, 76, 184, 220]), (sacrum, [40, 76, 112, 148, 184])):
            for shared in (0.0, 900.0):
                self.assertEqual(I.find_discs(w + shared), want, shared)


class Phantoms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vols = {name: P.hu_column(n=3, **kw) for name, kw in (("realistic", REALISTIC), ("sharp", SHARP))}
        cls.got = {}
        for name, (hu, aff) in cls.vols.items():
            for fit in (False, True):
                cls.got[name, fit] = I.measure(Volume(hu=hu, affine=aff, source="phantom"), fit_edges=fit)

    def test_one_body_between_two_discs_a_vertebra_apart(self):
        bodies, found = self.got["sharp", True]
        self.assertEqual(found.problems, [])
        self.assertEqual(len(found.discs), 2)
        self.assertLess(abs(found.discs[1] - found.discs[0] - 36.0), 1.5)
        self.assertEqual([b.level for b in bodies], ["?", "?", "?"])
        self.assertEqual(sum(1 for b in bodies if b.values), 1)
        self.assertTrue(all("bounded by one disc" in b.flags["all"] for b in bodies if not b.values))

    def test_the_half_maximum_edge_lies_outward_of_a_thin_cortex_under_blur(self):
        err, _ = errors(self.got["realistic", False][0])
        for m in ("endplate", "endplate_lower", "endplate_depth", "endplate_lower_depth", "h_post"):
            self.assertGreater(err[m], 1.0, m)
        for m in ("canal_w", "canal_ap"):
            self.assertLess(err[m], -1.0, m)

    def test_the_fit_brings_every_chord_of_a_clinical_vertebra_within_half_a_millimetre(self):
        fit, measured = errors(self.got["realistic", True][0])
        half, _ = errors(self.got["realistic", False][0])
        for m in SEVEN:
            self.assertLessEqual(abs(fit[m]), 0.5, m)
            self.assertLess(abs(fit[m]), abs(half[m]), m)
        self.assertIn("blurred-step surface", measured[0].methods["endplate"])

    def test_on_a_sharp_scan_both_hold_within_the_documented_bounds(self):
        half, _ = errors(self.got["sharp", False][0])
        fit, _ = errors(self.got["sharp", True][0])
        for m in SEVEN:
            self.assertLessEqual(abs(half[m]), 0.4, m)
            # a cortex of 800 HU taken as 1,200 HU reads thinner, so the fit moves the ends inward too far
            self.assertLessEqual(abs(fit[m]), 0.75, m)

    def test_the_same_volume_gives_the_same_chords(self):
        hu, aff = self.vols["realistic"]
        again, _ = I.measure(Volume(hu=hu.copy(), affine=aff.copy(), source="phantom"), fit_edges=True)
        first, _ = self.got["realistic", True]
        for a, b in zip(first, again):
            self.assertEqual(a.values, b.values)
            self.assertEqual(a.methods, b.methods)

    def test_metal_in_a_vertebra_leaves_it_unmeasured_and_is_said(self):
        # a screw's tip of 27 voxels at 3,000 HU in the middle of the measured body
        hu, aff = self.vols["sharp"]
        hu = hu.copy()
        at = np.round(local_to_voxel(aff, 1, (0.0, S.D / 2.0, 0.0))).astype(int)
        hu[tuple(slice(i - 1, i + 2) for i in at)] = 3000.0
        bodies, found = I.measure(Volume(hu=hu, affine=aff, source="phantom"), fit_edges=False)
        self.assertEqual(len(found.discs), 2)
        self.assertEqual([b for b in bodies if b.values], [])
        self.assertEqual(sum(1 for b in bodies if b.flags.get("all", "").startswith("metal")), 1)
        self.assertTrue(any("metal" in q and "within 60 mm" in q for q in found.problems), found.problems)

    def test_a_dicom_series_through_the_command_line_gives_what_the_volume_gives(self):
        hu, aff = self.vols["sharp"]
        with tempfile.TemporaryDirectory() as d:
            DF.write_ct_series(os.path.join(d, "ct"), hu, aff, covariates={"PatientSex": "M", "PatientAge": "061Y"})
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                main(["ingest-raw-ct", "--volume", os.path.join(d, "ct"), "--study", "p1", "--source", "phantom",
                      "--out", os.path.join(d, "out")])
            with open(os.path.join(d, "out", "columns", "p1.json")) as fh:
                col = json.load(fh)
            self.assertTrue(os.path.exists(os.path.join(d, "out", "fields", "p1.csv")))
        study = col["study"]
        self.assertEqual(study["annotation"], "none")
        self.assertEqual(study["mask_free"]["edges"], "blurred-step fit (edges.py)")
        self.assertEqual(study["covariates"]["sex"]["value"], "M")
        self.assertFalse(study["countable"])
        measured = [b for b in col["bodies"] if any(v is not None for v in b["values"].values())]
        want, _ = errors(self.got["sharp", True][0])
        for m in SEVEN:
            # the series stores whole HU, so its edges may move by a few hundredths of a millimetre
            self.assertLess(abs(measured[0]["values"][m] - TRUTH[m] - want[m]), 0.05, m)


class HardSpines(unittest.TestCase):
    """Phantoms that broke the finding of the canal or the discs before: a body whose marrow is as
    dark as the canal, and an osteoporotic column beside a contrast-filled aorta."""

    @classmethod
    def setUpClass(cls):
        fatty = P.hu_column(n=3, trabecular=40.0, noise_hu=15.0, **QUICK)
        hu, aff = P.hu_column(n=3, trabecular=120.0, **QUICK)
        vessel = (with_vessel(hu, aff), aff)
        cls.got = {name: I.measure(Volume(hu=h, affine=a, source="phantom"), fit_edges=False)
                   for name, (h, a) in (("fatty", fatty), ("vessel", vessel))}

    def test_a_fatty_body_is_measured_round_the_canal_not_through_its_marrow(self):
        # with marrow at 40 HU the inside of each body is a bone-enclosed hole of canal density;
        # taken for the canal, it gave chords 5 to 35 mm wrong with no problem said
        bodies, found = self.got["fatty"]
        self.assertEqual(found.problems, [])
        self.assertEqual(len(found.discs), 2)
        self.assertLess(abs(found.discs[1] - found.discs[0] - 36.0), 1.5)
        err, _ = errors(bodies)
        for m in SEVEN:
            self.assertLess(abs(err[m]), 1.5, m)

    def test_a_contrast_filled_aorta_in_every_section_hides_no_disc(self):
        # the vessel adds the same dense weight to every cross-section; measured from zero, the
        # dips stood above half the spikes and no disc was found
        bodies, found = self.got["vessel"]
        self.assertEqual(found.problems, [])
        self.assertEqual(len(found.discs), 2)
        self.assertLess(abs(found.discs[1] - found.discs[0] - 36.0), 2.0)
        self.assertEqual(sum(1 for b in bodies if b.values), 1)


class Refusals(unittest.TestCase):
    def test_no_canal_and_metal_are_said_and_nothing_is_measured(self):
        hu = np.full((40, 40, 12), 40.0, np.float32)
        hu[:3] = -1000.0
        hu[20, 20, 6] = 3000.0
        bodies, found = I.measure(Volume(hu=hu, affine=np.eye(4), source="phantom"))
        self.assertEqual(bodies, [])
        self.assertTrue(any(q.startswith("no canal") for q in found.problems))
        self.assertTrue(any("metal" in q for q in found.problems))

    def test_metal_far_from_the_canal_is_not_a_problem_of_the_study(self):
        hu = np.zeros((10, 10, 200), np.float32)
        line = I.Centreline(points=np.array([[5.0, 5.0, z] for z in range(100)]),
                            tangents=np.tile([0.0, 0.0, 1.0], (100, 1)), found_slices=100, skipped_slices=0)
        hu[5, 5, 190] = 3000.0                      # 91 mm past the canal's end, as teeth above a neck's bodies
        self.assertIsNone(I.metal_problem(hu, np.eye(4), line))
        hu[5, 5, 120] = 3000.0                      # 21 mm past it
        self.assertIn("(metal) within 60 mm", I.metal_problem(hu, np.eye(4), line))

    def test_one_slice_is_not_a_volume(self):
        import nibabel as nib
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "slice.nii.gz")
            hu = np.full((30, 30, 1), 40.0, np.float32)
            hu[:2] = -1000.0
            nib.save(nib.Nifti1Image(hu, np.eye(4)), p)
            with self.assertRaises(SystemExit) as e:
                I.ingest(p, "s1", "test")
        self.assertIn("not one slice", str(e.exception))


if __name__ == "__main__":
    unittest.main()
