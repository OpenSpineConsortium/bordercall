"""The extractors on phantoms whose every measure is known (phantom.py): a straight lumbar column
at 0.8 by 0.8 by 1 mm tilted against the scanner, the same with its shape changed one part at a
time, a column whose joints turn and slip, a pelvis, thick slices, and two masks a segmenter gets
wrong. Linear measures must land within TOL_MM of the truth, angles within TOL_DEG and areas
within TOL_SHARE, on 1 mm slices; the thick-slice case states its own, looser bounds, and why."""
import math
import unittest

import numpy as np

from morphometry import anatomy as A, measure as M
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS

TOL_MM = 0.75
TOL_DEG = 1.5
TOL_SHARE = 0.04
LUMBAR = ["L2", "L3", "L4"]


def measured(placed, levels, spacing=(0.8, 0.8, 1.0), grid_turn=((0.0, 0.0, 1.0), 7.0), pelvis=None, hook=None,
             strict=True):
    """Rows of measure_volume over the drawn phantom, as {level: {key: value}}; hook, where
    given, changes the drawn (labels, affine) first."""
    lab, aff = P.draw(placed, spacing=spacing, grid_turn=grid_turn, pelvis=pelvis, strict=strict)
    if hook is not None:
        lab, aff = hook(lab, aff)
    grid = G.VoxelGrid(aff, lab.shape)
    names = {P.LEVEL_IDS[lv]: lv for lv in levels}
    if pelvis is not None:
        names.update({P.SACRUM: "sacrum", P.HIP_RIGHT: "hip_right", P.HIP_LEFT: "hip_left"})
    out = {}
    for r in M.measure_volume(lab, grid, names, "phantom", pelvis=pelvis is not None):
        out.setdefault(r["level"], {})[r["key"]] = r["value"] if not r["key"].startswith("flag") else r["note"]
    return out


class Straight(unittest.TestCase):
    """L2 to L4, identical, 10 mm discs, tilted 18 degrees, the grid turned 7."""

    @classmethod
    def setUpClass(cls):
        cls.v = P.Vert()
        cls.rows = measured(P.straight(LUMBAR, cls.v), LUMBAR)
        cls.truth = P.truth(cls.v)
        cls.truth.update(P.canal_profile(cls.v))

    def near(self, key, tol=TOL_MM, level="L3"):
        got, want = self.rows[level][key], self.truth[key]
        self.assertTrue(np.isfinite(got), "%s %s is not finite" % (level, key))
        self.assertLessEqual(abs(got - want), tol, "%s %s: %.2f against %.2f" % (level, key, got, want))

    def test_body(self):
        for k in ("endplate", "endplate_depth", "endplate_lower", "endplate_lower_depth", "h_ant", "h_mid",
                  "h_post_inset", "body_w_mid", "body_d_mid", "endplate_concavity", "endplate_lower_concavity"):
            self.near(k)

    def test_end_plate_angles_and_areas(self):
        for k in ("endplate_incl", "endplate_lower_incl", "wedge"):
            self.near(k, TOL_DEG)
        for k in ("endplate_area", "endplate_lower_area"):
            self.near(k, TOL_SHARE * self.truth[k])

    def test_canal(self):
        for k in ("canal_ap_min", "interpedicular", "interpedicular_max", "canal_ap_lateral", "canal_ap_lateral_film"):
            self.near(k)
        self.near("canal_area_min", TOL_SHARE * self.truth["canal_area_min"])

    def test_pedicles(self):
        for k in ("pedicle_w", "pedicle_h", "pedicle_chord"):
            self.near(k)
        for k in ("pedicle_angle_transverse", "pedicle_angle_sagittal"):
            self.near(k, TOL_DEG)
        self.near("pedicle_area", TOL_SHARE * self.truth["pedicle_area"])

    def test_posterior_elements(self):
        for k in ("transverse_width", "transverse_length", "transverse_h", "lamina_thickness", "interfacet_w_sup",
                  "interfacet_w_inf"):
            self.near(k)
        self.near("spinous_angle", 2 * TOL_DEG)
        for k in ("facet_angle_axial_sup", "facet_angle_axial_inf"):
            got = self.rows["L3"][k]
            self.assertLessEqual(abs(got - self.v.facet), 2 * TOL_DEG, "%s %.2f" % (k, got))

    def test_discs_and_segments(self):
        for pair in ("L2-L3", "L3-L4"):
            for k in ("disc_h_ant", "disc_h_mid", "disc_h_post"):
                self.assertLessEqual(abs(self.rows[pair][k] - 10.0), TOL_MM, "%s %s" % (pair, k))
            for k in ("segment_sagittal", "segment_coronal", "segment_axial"):
                self.assertLessEqual(abs(self.rows[pair][k]), TOL_DEG, "%s %s" % (pair, k))
            self.assertLessEqual(abs(self.rows[pair]["listhesis"]), TOL_MM)

    def test_axis_follows_the_end_plates(self):
        self.assertLessEqual(self.rows["L3"]["axis_offset"], TOL_DEG)


class Shapes(unittest.TestCase):
    """One part changed at a time: a wedge, concave end-plates, a waist, angled pedicles, a
    steeper facet and spinous process."""

    @classmethod
    def setUpClass(cls):
        cls.v = P.lumbar(Ha=30.0, concavity=2.0, waist=0.92, ped_t=12.0, ped_s=6.0, facet=55.0, sp_angle=32.0)
        cls.rows = measured(P.straight(LUMBAR, cls.v), LUMBAR)
        cls.truth = P.truth(cls.v)

    def near(self, key, tol):
        got, want = self.rows["L3"][key], self.truth[key]
        self.assertLessEqual(abs(got - want), tol, "%s: %.2f against %.2f" % (key, got, want))

    def test_wedge_and_heights(self):
        self.near("wedge", TOL_DEG)
        for k in ("h_ant", "h_mid", "h_post_inset"):
            self.near(k, TOL_MM)

    def test_concavity_and_waist(self):
        for k in ("endplate_concavity", "endplate_lower_concavity", "body_w_mid", "body_d_mid"):
            self.near(k, TOL_MM)

    def test_pedicle_angles(self):
        for k in ("pedicle_angle_transverse", "pedicle_angle_sagittal"):
            self.near(k, TOL_DEG)
        for k in ("pedicle_w", "pedicle_h"):
            self.near(k, TOL_MM)

    def test_processes(self):
        self.near("spinous_angle", 2 * TOL_DEG)
        got = self.rows["L3"]["facet_angle_axial_sup"]
        self.assertLessEqual(abs(got - self.v.facet), 2 * TOL_DEG, "facet %.2f" % got)


class LateralMass(unittest.TestCase):
    """Pedicles that swell away from their isthmus, each with a block 8 mm wide and 24 mm tall
    against its side, as the lateral mass stands against a cervical pedicle, pierced by a
    foramen 6.5 mm across whose wall beside the isthmus is the pedicle's own side, as the
    foramen transversarium lies beside the cervical pedicle, so that only the rows through the
    foramen show the pedicle free of the block: the pedicle's width and height are its own, not
    the block's, and the interpedicular distance is read at the isthmus, where the swelling is
    nil, not across the hole's middle behind it, where the swollen pedicles narrow the canal.
    The phantom is drawn unstrictly: the swollen posterior end of each pedicle, half again its
    isthmus's size at the pillar, runs into the neighbour above's inferior articular process by
    a few dozen voxels, a collision of the phantom's parts and not of any real vertebra's."""

    @classmethod
    def setUpClass(cls):
        cls.v = P.lumbar(ped_waist=0.02, mass_w=8.0, mass_h=24.0, foramen_d=6.5)
        cls.rows = measured(P.straight(LUMBAR, cls.v), LUMBAR, strict=False)
        cls.truth = P.truth(cls.v)

    def near(self, key, tol):
        got, want = self.rows["L3"][key], self.truth[key]
        self.assertTrue(np.isfinite(got), "%s is not finite" % key)
        self.assertLessEqual(abs(got - want), tol, "%s: %.2f against %.2f" % (key, got, want))

    def test_pedicle_without_the_mass(self):
        for k in ("pedicle_w", "pedicle_h"):
            self.near(k, TOL_MM)

    def test_interpedicular_at_the_isthmus(self):
        for k in ("interpedicular", "interpedicular_max"):
            self.near(k, TOL_MM)


class Joints(unittest.TestCase):
    """L2 to L4 with each joint opened 8 degrees in front, tilted 4 sideways, turned 5 and the
    upper vertebra slipped 4 mm forward. The turned facets of neighbours claim a few voxels
    twice (2,578 of about 150,000), the later drawn keeping them, which none of the measures
    tested here reads."""

    @classmethod
    def setUpClass(cls):
        v = P.Vert()
        joint = P.Joint(gap=10.0, sagittal=8.0, coronal=4.0, axial=5.0, slip=4.0)
        placed = P.chain(LUMBAR, {lv: v for lv in LUMBAR}, {lv: joint for lv in LUMBAR[1:]},
                         R0=P.rotation((1.0, 0.3, 0.0), 12.0))
        cls.rows = measured(placed, LUMBAR, strict=False)

    def test_segment_angles(self):
        row = self.rows["L2-L3"]
        self.assertLessEqual(abs(row["segment_sagittal"] - 8.0), TOL_DEG, row["segment_sagittal"])
        self.assertLessEqual(abs(row["segment_coronal"] - 4.0), TOL_DEG, row["segment_coronal"])
        self.assertLessEqual(abs(abs(row["segment_axial"]) - 5.0), TOL_DEG, row["segment_axial"])

    def test_slip(self):
        self.assertLessEqual(abs(self.rows["L2-L3"]["listhesis"] - 4.0), 2 * TOL_MM, self.rows["L2-L3"]["listhesis"])

    def test_disc_at_the_centre(self):
        self.assertLessEqual(abs(self.rows["L2-L3"]["disc_h_mid"] - 10.0), 2 * TOL_MM, self.rows["L2-L3"]["disc_h_mid"])


class Pelvis(unittest.TestCase):
    """L4 and L5 on a sacrum tilted 10 degrees, with two hip sockets of radius 24 mm."""

    @classmethod
    def setUpClass(cls):
        levels = ["L4", "L5"]
        placed = P.straight(levels)
        cls.p = P.Pelvis()
        cls.truth = P.pelvis_truth(placed[-1], cls.p)
        cls.rows = measured(placed, levels, spacing=(1.0, 1.0, 1.0), pelvis=cls.p)

    def test_incidence_and_its_parts(self):
        row = self.rows["pelvis"]
        self.assertLessEqual(abs(row["pelvic_incidence"] - self.truth["pelvic_incidence"]), 2 * TOL_DEG,
                             (row["pelvic_incidence"], self.truth["pelvic_incidence"]))
        self.assertLessEqual(abs(row["sacral_slope_supine"] + row["pelvic_tilt_supine"] - row["pelvic_incidence"]), 0.1)

    def test_sockets(self):
        row = self.rows["pelvis"]
        width = float(np.linalg.norm(self.truth["hip_right"] - self.truth["hip_left"]))
        self.assertLessEqual(abs(row["hip_axis_width"] - width), 2 * TOL_MM, (row["hip_axis_width"], width))
        for side in ("right", "left"):
            self.assertLessEqual(abs(row["acetabulum_radius_" + side] - self.p.socket), 2 * TOL_MM)


class ThickSlices(unittest.TestCase):
    """0.86 by 0.86 by 2.5 mm, the column tilted 20 degrees, as most of ENHANCE.PET's CTs are cut.

    The chords across the column and the canal keep the 1 mm bounds, since a pixel is 0.86 mm.
    A height or a disc is read across the layers, and its two surfaces each fall somewhere in a
    2.5 mm step: `python -m morphometry bench --slice 2.5` gives the errors over 22 tilts and
    turns of the straight phantom, whose largest errors were 2.27 mm on a height and 2.53 on a
    disc; THICK_MM is 2.6, so that this case fails only where the reading gets worse than the
    bench says."""

    @classmethod
    def setUpClass(cls):
        cls.v = P.Vert()
        cls.rows = measured(P.straight(LUMBAR, cls.v, tilt=((1.0, 0.0, 0.0), 20.0)), LUMBAR,
                            spacing=(0.86, 0.86, 2.5), grid_turn=((0.0, 0.0, 1.0), 0.0))
        cls.truth = P.truth(cls.v)
        cls.truth.update(P.canal_profile(cls.v))

    def test_chords_across(self):
        for k in ("endplate", "endplate_lower", "interpedicular", "transverse_width", "interfacet_w_sup"):
            got, want = self.rows["L3"][k], self.truth[k]
            self.assertLessEqual(abs(got - want), TOL_MM, "%s: %.2f against %.2f" % (k, got, want))

    def test_heights_and_discs(self):
        for k in ("h_ant", "h_mid", "h_post_inset"):
            self.assertLessEqual(abs(self.rows["L3"][k] - self.truth[k]), THICK_MM, k)
        for k in ("disc_h_ant", "disc_h_mid", "disc_h_post"):
            self.assertLessEqual(abs(self.rows["L2-L3"][k] - 10.0), THICK_MM, k)


THICK_MM = 2.6


class WrongMasks(unittest.TestCase):
    """What a segmenter or the scan's edge gets wrong is flagged, not measured."""

    def test_a_label_holding_half_a_neighbour(self):
        def swap_half(lab, aff):
            idx = np.argwhere(lab == P.LEVEL_IDS["L3"])
            right = idx[idx[:, 0] > np.median(idx[:, 0])]
            out = lab.copy()
            out[tuple(right.T)] = P.LEVEL_IDS["L2"]
            return out, aff
        rows = measured(P.straight(LUMBAR), LUMBAR, hook=swap_half)
        self.assertIn("flag:all", rows["L2"])
        self.assertIn("flag:all", rows["L3"])

    def test_a_vertebra_cut_by_the_volume(self):
        def crop(lab, aff):
            idx = np.argwhere(lab == P.LEVEL_IDS["L4"])
            k0 = int(np.percentile(idx[:, 2], 30))
            out = np.array(aff, float)
            out[:3, 3] += out[:3, 2] * k0
            return lab[:, :, k0:], out
        rows = measured(P.straight(LUMBAR), LUMBAR, hook=crop)
        self.assertNotIn("L3-L4", rows, "a disc against a body the volume cuts is not read")
        self.assertLessEqual(abs(rows["L3"]["pedicle_angle_transverse"]), TOL_DEG,
                             "the cut neighbour does not turn L3's line")


if __name__ == "__main__":
    unittest.main()
