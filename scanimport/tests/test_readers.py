"""Raw images read back as written: a CT series, an Enhanced CT Image, a NIfTI with its sidecar,
one DICOM radiograph's scale and covariates, and a picture file's orientation; and what is
refused or left out because the header says the values are not what the reader needs."""
import json
import os
import tempfile
import unittest
import warnings

import numpy as np

from scanimport import readers as R
from scanimport.tests import dicom_files as DF
from scanimport.tests import phantom as PH


def small_volume():
    """A 12 x 10 x 6 volume of HU values, air on one side, on a grid turned 9 degrees about the scanner's
    axis, 0.8 by 0.8 by 2.5 mm, in RAS."""
    hu = (np.arange(12 * 10 * 6).reshape(12, 10, 6) % 700 - 300).astype(np.float32)
    hu[:2] = -1000.0                                     # air beside the patient, as in any CT
    aff = np.eye(4)
    aff[:3, :3] = PH.rotation((0, 0, 1), 9.0) @ np.diag([0.8, 0.8, 2.5])
    aff[:3, 3] = [-40.0, 25.0, -110.0]
    return hu, aff


class Series(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.hu, cls.aff = small_volume()
        d = cls.tmp.name
        DF.write_ct_series(os.path.join(d, "one"), cls.hu, cls.aff, order=[3, 0, 5, 1, 4, 2],
                           covariates={"PatientSex": "F", "PatientAge": "054Y", "PatientSize": 1.62,
                                       "PatientWeight": 58.0, "KVP": 120, "ConvolutionKernel": "B30f"})
        DF.write_localizer(os.path.join(d, "one", "scout.dcm"), "1.2.826.0.1.3680043.10.1")
        with open(os.path.join(d, "one", "notes.txt"), "w") as fh:
            fh.write("not a DICOM file")
        DF.write_ct_series(os.path.join(d, "two"), cls.hu, cls.aff)
        DF.write_ct_series(os.path.join(d, "two", "b"), cls.hu, cls.aff, series_uid="1.2.826.0.1.3680043.10.9")
        DF.write_ct_series(os.path.join(d, "gap"), cls.hu, cls.aff, drop=[2])
        DF.write_enhanced_ct(os.path.join(d, "enhanced.dcm"), cls.hu, cls.aff)
        DF.write_ct_series(os.path.join(d, "mgml"), cls.hu, cls.aff, covariates={"RescaleType": "MGML"})
        DF.write_ct_series(os.path.join(d, "dual"), cls.hu, cls.aff, covariates={"MultienergyCTAcquisition": "YES"})
        DF.write_ct_series(os.path.join(d, "dual_hu"), cls.hu, cls.aff,
                           covariates={"MultienergyCTAcquisition": "YES", "RescaleType": "HU"})
        DF.write_ct_series(os.path.join(d, "reformat"), cls.hu, cls.aff,
                           covariates={"ImageType": ["DERIVED", "SECONDARY", "REFORMATTED"]})
        DF.write_enhanced_ct(os.path.join(d, "enhanced_zeff.dcm"), cls.hu, cls.aff, rescale_type="Z_EFF")
        DF.write_enhanced_ct(os.path.join(d, "enhanced_macros.dcm"), cls.hu, cls.aff,
                             macros={"CTXRayDetailsSequence": {"KVP": 120},
                                     "CTReconstructionSequence": {"ConvolutionKernel": "B30f"}})

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_a_rescale_type_other_than_hu_is_refused(self):
        for name in ("mgml", "enhanced_zeff.dcm"):
            with self.assertRaises(SystemExit) as e:
                R.read_volume(os.path.join(self.tmp.name, name))
            self.assertIn("not HU", str(e.exception), msg=name)

    def test_a_multi_energy_slice_is_hu_only_where_it_says_so(self):
        with self.assertRaises(SystemExit) as e:
            R.read_volume(os.path.join(self.tmp.name, "dual"))
        self.assertIn("multi-energy", str(e.exception))
        np.testing.assert_array_equal(R.read_volume(os.path.join(self.tmp.name, "dual_hu")).hu, self.hu)

    def test_a_derived_slice_with_no_rescale_type_is_hu(self):
        vol = R.read_volume(os.path.join(self.tmp.name, "reformat"))
        np.testing.assert_array_equal(vol.hu, self.hu)
        self.assertEqual(vol.problems, [])

    def test_enhanced_ct_covariates_come_from_their_macros(self):
        h = R.read_volume(os.path.join(self.tmp.name, "enhanced_macros.dcm")).header
        self.assertEqual(h["kvp"]["value"], 120)
        self.assertIn("CT X-Ray Details (0018,9325)", h["kvp"]["from"])
        self.assertEqual(h["kernel"]["value"], "B30f")
        self.assertIn("CT Reconstruction (0018,9314)", h["kernel"]["from"])
        self.assertAlmostEqual(h["slice_thickness_mm"]["value"], 2.5)
        self.assertIn("Pixel Measures (0028,9110)", h["slice_thickness_mm"]["from"])

    def test_series_comes_back_in_hu_on_its_grid(self):
        vol = R.read_volume(os.path.join(self.tmp.name, "one"))
        np.testing.assert_array_equal(vol.hu, self.hu)
        np.testing.assert_allclose(vol.affine, self.aff, atol=1e-6)
        self.assertEqual(vol.header["slices"]["value"], 6)
        self.assertEqual(vol.problems, [])

    def test_covariates_are_read_with_their_tags(self):
        h = R.read_volume(os.path.join(self.tmp.name, "one")).header
        self.assertEqual(h["sex"], {"value": "F", "from": "PatientSex (0010,0040)"})
        self.assertEqual(h["age_years"]["value"], 54.0)
        self.assertAlmostEqual(h["height_cm"]["value"], 162.0)
        self.assertEqual(h["weight_kg"]["value"], 58.0)
        self.assertEqual(h["kernel"]["value"], "B30f")

    def test_enhanced_ct_gives_the_same_volume(self):
        vol = R.read_volume(os.path.join(self.tmp.name, "enhanced.dcm"))
        np.testing.assert_array_equal(vol.hu, self.hu)
        np.testing.assert_allclose(vol.affine, self.aff, atol=1e-6)
        self.assertEqual(vol.source, "dicom-enhanced-ct")

    def test_two_series_are_refused_unless_one_is_named(self):
        folder = os.path.join(self.tmp.name, "two")
        with self.assertRaises(SystemExit) as e:
            R.read_volume(folder)
        self.assertIn("2 CT series", str(e.exception))
        vol = R.read_dicom_series(folder, "1.2.826.0.1.3680043.10.9")
        np.testing.assert_array_equal(vol.hu, self.hu)
        with self.assertRaises(SystemExit) as e:
            R.read_dicom_series(folder, "1.2.3")
        self.assertIn("no CT series 1.2.3", str(e.exception))

    def test_a_missing_slice_is_refused(self):
        with self.assertRaises(SystemExit) as e:
            R.read_volume(os.path.join(self.tmp.name, "gap"))
        self.assertIn("one step", str(e.exception))

    def test_one_slice_is_read_and_says_so(self):
        one = sorted(os.listdir(os.path.join(self.tmp.name, "gap")))[0]
        vol = R.read_volume(os.path.join(self.tmp.name, "gap", one))
        self.assertEqual(vol.hu.shape[2], 1)
        self.assertTrue(any("one slice" in p for p in vol.problems))


class Nifti(unittest.TestCase):
    def test_sidecar_covariates_and_uncalibrated_intensities(self):
        hu, aff = small_volume()
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "ct.nii.gz")
            PH.save(path, hu, aff)
            with open(os.path.join(d, "ct.json"), "w") as fh:
                json.dump({"PatientSex": "M", "PatientAge": "061Y", "PatientWeight": 81, "Manufacturer": "SIEMENS"}, fh)
            vol = R.read_volume(path)
            np.testing.assert_allclose(vol.affine, aff, atol=1e-6)
            self.assertEqual(vol.header["sex"]["value"], "M")
            self.assertEqual(vol.header["age_years"]["value"], 61.0)
            self.assertEqual(vol.header["weight_kg"]["from"], "dcm2niix sidecar PatientWeight")
            PH.save(path, hu + 1324.0, aff)             # stored values with no intercept: air near +300
            self.assertTrue(any("may not be in HU" in p for p in R.read_volume(path).problems))

    def test_no_orientation_is_refused(self):
        import nibabel as nib
        hu, aff = small_volume()
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "bare.nii.gz")
            img = nib.Nifti1Image(hu, aff)
            img.set_sform(None, code=0)
            img.set_qform(None, code=0)
            nib.save(img, path)
            with self.assertRaises(SystemExit) as e:
                R.read_volume(path)
            self.assertIn("orientation is unknown", str(e.exception))

    def test_a_fourth_dimension_of_one_is_one_volume(self):
        hu, aff = small_volume()
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "ct4.nii.gz")
            PH.save(path, hu[..., None], aff)
            vol = R.read_volume(path)
            np.testing.assert_array_equal(vol.hu, hu)
            PH.save(path, np.stack([hu, hu], axis=3), aff)
            with self.assertRaises(SystemExit):
                R.read_volume(path)


class Covariates(unittest.TestCase):
    def test_a_size_above_three_metres_is_left_out_with_why(self):
        for size in (162, "162"):
            h = R.dicom_covariates(ds_with(PatientSize=size, PatientWeight=58.0))
            self.assertIsNone(h["height_cm"]["value"])
            self.assertIn("probably centimetres", h["height_cm"]["from"])
            self.assertEqual(h["weight_kg"]["value"], 58.0)
        self.assertAlmostEqual(R.dicom_covariates(ds_with(PatientSize=1.62))["height_cm"]["value"], 162.0)

    def test_an_age_of_zero_years_is_missing_but_zero_months_is_an_age(self):
        self.assertIsNone(R.age_in_years("000Y"))
        self.assertEqual(R.age_in_years("000M"), 0.0)
        self.assertAlmostEqual(R.age_in_years("018M"), 1.5)
        h = R.dicom_covariates(ds_with(PatientAge="000Y"))
        self.assertIsNone(h["age_years"]["value"])
        self.assertIn("000Y", h["age_years"]["from"])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")              # pydicom warns that "54" is no Age String, as it should
            self.assertNotIn("age_years", R.dicom_covariates(ds_with(PatientAge="54")))

    def test_the_sidecar_is_held_to_the_same_rules(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "ct.json"), "w") as fh:
                json.dump({"PatientSize": 175, "PatientAge": "000Y", "PatientWeight": 70}, fh)
            h = R.sidecar_covariates(os.path.join(d, "ct.nii.gz"))
            self.assertIsNone(h["height_cm"]["value"])
            self.assertIsNone(h["age_years"]["value"])
            self.assertEqual(h["weight_kg"]["value"], 70)

    def test_the_sidecar_is_the_niftis_name_with_json(self):
        for name, side in (("ct.nii.gz", "ct.json"), ("ct.nii", "ct.json"), ("CT.NII.GZ", "CT.json"),
                           ("Ct.Nii", "Ct.json"), ("a.b.nii.gz", "a.b.json")):
            self.assertEqual(R.sidecar_path(os.path.join("d", name)), os.path.join("d", side), name)
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "CT.json"), "w") as fh:
                json.dump({"PatientWeight": 70}, fh)
            self.assertEqual(R.sidecar_covariates(os.path.join(d, "CT.NII.GZ"))["weight_kg"]["value"], 70)


def ds_with(**attrs):
    from pydicom.dataset import Dataset
    ds = Dataset()
    for k, v in attrs.items():
        setattr(ds, k, v)
    return ds


M, M_SD = R.DEFAULT_MAGNIFICATION, R.DEFAULT_MAGNIFICATION_LOG_SD


class ProjectionScale(unittest.TestCase):
    def test_the_order_of_the_dicom_note(self):
        cases = [
            (dict(PixelSpacing=[0.2, 0.2], ImagerPixelSpacing=[0.15, 0.15], PixelSpacingCalibrationType="FIDUCIAL"),
             0.2, 0.03),
            (dict(PixelSpacing=[0.13, 0.13], ImagerPixelSpacing=[0.15, 0.15], PixelSpacingCalibrationType="GEOMETRY"),
             0.13, 0.05),
            (dict(PixelSpacing=[0.12, 0.12], ImagerPixelSpacing=[0.15, 0.15]), 0.12, 0.05),
            (dict(PixelSpacing=[0.12, 0.12], ImagerPixelSpacing=[0.15, 0.15], EstimatedRadiographicMagnificationFactor=1.4),
             0.12, 0.05),
            (dict(ImagerPixelSpacing=[0.15, 0.15], EstimatedRadiographicMagnificationFactor=1.25), 0.12, 0.05),
            (dict(ImagerPixelSpacing=[0.15, 0.15], DistanceSourceToDetector=1200, DistanceSourceToPatient=1000),
             0.125, 0.05),
            (dict(ImagerPixelSpacing=[0.15, 0.15], PixelSpacing=[0.1501, 0.1501]), 0.15 / M, M_SD),
            (dict(ImagerPixelSpacing=[0.15, 0.15]), 0.15 / M, M_SD),
            (dict(PixelSpacing=[0.15, 0.15]), 0.15 / M, 0.12),
        ]
        for attrs, mm, sd in cases:
            s = R.projection_scale(ds_with(**attrs))
            self.assertAlmostEqual(s["pixel_mm"], mm, places=9, msg=str(attrs))
            self.assertAlmostEqual(s["log_sd"], sd, msg=str(attrs))
        self.assertIsNone(R.projection_scale(ds_with())["pixel_mm"])
        self.assertAlmostEqual(R.projection_scale(ds_with(), override_mm=0.2)["pixel_mm"], 0.2 / M)

    def test_a_pixel_spacing_corrected_at_the_modality_says_so(self):
        s = R.projection_scale(ds_with(PixelSpacing=[0.11, 0.11], ImagerPixelSpacing=[0.14, 0.14]))
        self.assertAlmostEqual(s["pixel_mm"], 0.11)
        self.assertAlmostEqual(s["pixel_mm_at_detector"], 0.14)
        self.assertIn("method not stated", s["basis"])

    def test_a_pixel_spacing_larger_than_the_detectors_is_a_problem(self):
        problems = []
        s = R.projection_scale(ds_with(PixelSpacing=[0.2, 0.2], ImagerPixelSpacing=[0.15, 0.15]), problems=problems)
        self.assertAlmostEqual(s["pixel_mm"], 0.15 / M)
        self.assertEqual(len(problems), 1)
        self.assertIn("contradicts itself", problems[0])

    def test_a_magnification_factor_of_one_is_no_statement(self):
        s = R.projection_scale(ds_with(ImagerPixelSpacing=[0.15, 0.15], EstimatedRadiographicMagnificationFactor=1.0))
        self.assertAlmostEqual(s["pixel_mm"], 0.15 / M)
        self.assertAlmostEqual(s["log_sd"], M_SD)
        s = R.projection_scale(ds_with(ImagerPixelSpacing=[0.15, 0.15], EstimatedRadiographicMagnificationFactor=1.0,
                                       DistanceSourceToDetector=1200, DistanceSourceToPatient=1000))
        self.assertAlmostEqual(s["pixel_mm"], 0.125)

    def test_a_magnification_passed_over_is_said(self):
        for attrs, said in ((dict(EstimatedRadiographicMagnificationFactor=1.0), "not above 1"),
                            (dict(EstimatedRadiographicMagnificationFactor=0.8), "not above 1"),
                            (dict(DistanceSourceToDetector=1000, DistanceSourceToPatient=1200), "passed over"),
                            (dict(DistanceSourceToDetector=1000, DistanceSourceToPatient=1000), "passed over")):
            problems = []
            s = R.projection_scale(ds_with(ImagerPixelSpacing=[0.15, 0.15], **attrs), problems=problems)
            self.assertAlmostEqual(s["pixel_mm"], 0.15 / M, msg=str(attrs))
            self.assertEqual(len(problems), 1, msg=str(attrs))
            self.assertIn(said, problems[0], msg=str(attrs))
        problems = []
        R.projection_scale(ds_with(ImagerPixelSpacing=[0.15, 0.15], EstimatedRadiographicMagnificationFactor=1.25,
                                   DistanceSourceToDetector=1000, DistanceSourceToPatient=1200), problems=problems)
        self.assertEqual(problems, [])                   # a usable factor is read first, and the distances not at all

    def test_a_calibration_that_shrinks_the_patient_is_a_problem(self):
        for kind in ("FIDUCIAL", "GEOMETRY"):
            problems = []
            s = R.projection_scale(ds_with(PixelSpacing=[0.2, 0.2], ImagerPixelSpacing=[0.15, 0.15],
                                           PixelSpacingCalibrationType=kind), problems=problems)
            self.assertAlmostEqual(s["pixel_mm"], 0.2, msg=kind)
            self.assertEqual(len(problems), 1, msg=kind)
            self.assertIn("magnification below 1", problems[0])
            problems = []
            R.projection_scale(ds_with(PixelSpacing=[0.12, 0.12], ImagerPixelSpacing=[0.15, 0.15],
                                       PixelSpacingCalibrationType=kind), problems=problems)
            self.assertEqual(problems, [], msg=kind)

    def test_scanned_film_holds_pixel_spacing_against_its_nominal_spacing(self):
        s = R.projection_scale(ds_with(PixelSpacing=[0.15, 0.15], NominalScannedPixelSpacing=[0.15, 0.15]))
        self.assertAlmostEqual(s["pixel_mm"], 0.15 / M)
        self.assertAlmostEqual(s["log_sd"], M_SD)
        self.assertIn("Nominal Scanned Pixel Spacing (0018,2010), on the scanned film", s["basis"])
        s = R.projection_scale(ds_with(PixelSpacing=[0.12, 0.12], NominalScannedPixelSpacing=[0.15, 0.15]))
        self.assertAlmostEqual(s["pixel_mm"], 0.12)
        self.assertAlmostEqual(s["pixel_mm_at_detector"], 0.15)
        self.assertIn("smaller than Nominal Scanned Pixel Spacing", s["basis"])
        s = R.projection_scale(ds_with(NominalScannedPixelSpacing=[0.15, 0.15], ImagerPixelSpacing=[0.2, 0.2]))
        self.assertAlmostEqual(s["pixel_mm_at_detector"], 0.2)    # Imager Pixel Spacing first, where both are given
        s = R.projection_scale(ds_with(PixelSpacing=[0.15, 0.15]))
        self.assertIn("no Imager or Nominal Scanned Pixel Spacing", s["basis"])

    def test_every_scale_has_the_same_keys_and_one_magnification(self):
        headers = [dict(PixelSpacing=[0.12, 0.12], ImagerPixelSpacing=[0.15, 0.15], PixelSpacingCalibrationType=kind)
                   for kind in ("FIDUCIAL", "GEOMETRY", "")]
        headers += [dict(PixelSpacing=[0.12, 0.12], PixelSpacingCalibrationType="FIDUCIAL"),
                    dict(ImagerPixelSpacing=[0.15, 0.15], EstimatedRadiographicMagnificationFactor=1.25),
                    dict(PixelSpacing=[0.15, 0.15]), dict()]
        for attrs in headers:
            s = R.projection_scale(ds_with(**attrs))
            self.assertEqual(set(s), {"pixel_mm", "pixel_mm_at_detector", "magnification", "log_sd", "basis"}, msg=str(attrs))
            if s["pixel_mm_at_detector"] is not None:
                self.assertAlmostEqual(s["pixel_mm"] * s["magnification"], s["pixel_mm_at_detector"], msg=str(attrs))
        for kind in ("FIDUCIAL", "GEOMETRY"):
            s = R.projection_scale(ds_with(PixelSpacing=[0.12, 0.12], ImagerPixelSpacing=[0.15, 0.15],
                                           PixelSpacingCalibrationType=kind))
            self.assertAlmostEqual(s["pixel_mm_at_detector"], 0.15, msg=kind)
            self.assertAlmostEqual(s["magnification"], 1.25, msg=kind)
        s = R.projection_scale(ds_with(PixelSpacing=[0.12, 0.12], PixelSpacingCalibrationType="FIDUCIAL"))
        self.assertIsNone(s["pixel_mm_at_detector"])
        self.assertEqual(s["magnification"], 1.0)

    def test_the_callers_pixel_keeps_the_headers_magnification(self):
        s = R.projection_scale(ds_with(ImagerPixelSpacing=[0.14, 0.14], EstimatedRadiographicMagnificationFactor=1.4),
                               override_mm=0.14)
        self.assertAlmostEqual(s["pixel_mm"], 0.1)
        self.assertAlmostEqual(s["magnification"], 1.4)
        self.assertIn("caller's pixel size", s["basis"])
        s = R.projection_scale(ds_with(ImagerPixelSpacing=[0.15, 0.15], DistanceSourceToDetector=1200,
                                       DistanceSourceToPatient=1000), override_mm=0.18)
        self.assertAlmostEqual(s["pixel_mm"], 0.15)
        s = R.projection_scale(ds_with(PixelSpacing=[0.12, 0.12], ImagerPixelSpacing=[0.15, 0.15],
                                       PixelSpacingCalibrationType="GEOMETRY"), override_mm=0.2)
        self.assertAlmostEqual(s["pixel_mm"], 0.16)
        self.assertAlmostEqual(s["log_sd"], 0.05)
        self.assertIn("magnification 1.250 implied", s["basis"])
        s = R.projection_scale(ds_with(ImagerPixelSpacing=[0.15, 0.15]), override_mm=0.2)
        self.assertAlmostEqual(s["pixel_mm"], 0.2 / M)
        self.assertAlmostEqual(s["log_sd"], M_SD)

    def test_pixels_that_are_not_square_are_refused(self):
        for attrs in (dict(ImagerPixelSpacing=[0.30, 0.25]), dict(PixelSpacing=[0.2, 0.3]),
                      dict(PixelSpacing=[0.12, 0.10], ImagerPixelSpacing=[0.15, 0.15], PixelSpacingCalibrationType="GEOMETRY")):
            with self.assertRaises(SystemExit) as e:
                R.projection_scale(ds_with(**attrs))
            self.assertIn("not square", str(e.exception), msg=str(attrs))
            with self.assertRaises(SystemExit):
                R.projection_scale(ds_with(**attrs), override_mm=0.2)
        s = R.projection_scale(ds_with(ImagerPixelSpacing=[0.1500, 0.1505]))
        self.assertAlmostEqual(s["pixel_mm_at_detector"], 0.15025)

    def test_a_spacing_that_is_not_a_pair_of_lengths_is_left_out(self):
        for value in (0.15, [0.0, 0.0], [0.15, 0.15, 0.15]):
            problems = []
            s = R.projection_scale(ds_with(ImagerPixelSpacing=value), problems=problems)
            self.assertIsNone(s["pixel_mm"], msg=str(value))
            self.assertEqual(len(problems), 1, msg=str(value))
            self.assertIn("left out", problems[0])


class Projections(unittest.TestCase):
    def test_dicom_radiograph_is_made_bone_bright_with_its_scale(self):
        px = np.arange(30 * 20).reshape(30, 20) % 1000
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "dx.dcm")
            DF.write_projection(path, px, monochrome1=True,
                                attrs={"ImagerPixelSpacing": [0.14, 0.14], "EstimatedRadiographicMagnificationFactor": 1.4,
                                       "PatientSex": "M", "ViewPosition": "LL"})
            p = R.read_projection(path, with_pixels=True)
            self.assertEqual((p.height, p.width), (30, 20))
            np.testing.assert_array_equal(p.pixels, px.max() - px)
            self.assertAlmostEqual(p.scale["pixel_mm"], 0.1)
            self.assertEqual(p.header["view_position"]["value"], "LL")
            self.assertEqual(p.sha256, R.sha256_of(path))

    def test_only_the_secondary_capture_family_is_read_as_one(self):
        grey = np.full((6, 4), 100)
        with tempfile.TemporaryDirectory() as d:
            sc = os.path.join(d, "sc.dcm")
            DF.write_projection(sc, grey, sop_class="1.2.840.10008.5.1.4.1.1.7", attrs={"PixelSpacing": [0.2, 0.2]})
            self.assertEqual(R.read_projection(sc).source, "DICOM secondary capture")
            vl = os.path.join(d, "vl.dcm")
            DF.write_projection(vl, grey, sop_class="1.2.840.10008.5.1.4.1.1.77.1.4")
            with self.assertRaises(SystemExit) as e:
                R.read_projection(vl)
            self.assertIn("not a projection image", str(e.exception))

    def test_a_scanned_film_is_scaled_by_its_nominal_spacing(self):
        grey = np.full((6, 4), 100)
        with tempfile.TemporaryDirectory() as d:
            film = os.path.join(d, "film.dcm")
            DF.write_projection(film, grey, sop_class="1.2.840.10008.5.1.4.1.1.7",
                                attrs={"NominalScannedPixelSpacing": [0.15, 0.15], "ConversionType": "DF"})
            p = R.read_projection(film)
            self.assertAlmostEqual(p.scale["pixel_mm"], 0.15 / M)
            self.assertFalse(any("scale is unknown" in q for q in p.problems), msg=str(p.problems))
            bare = os.path.join(d, "bare.dcm")
            DF.write_projection(bare, grey, sop_class="1.2.840.10008.5.1.4.1.1.7")
            self.assertIsNone(R.read_projection(bare).scale["pixel_mm"])
            self.assertFalse(any("secondary capture" in q for q in R.read_projection(bare, pixel_mm=0.15).problems))

    def test_a_colour_capture_becomes_one_grey_channel(self):
        rgb = np.zeros((6, 4, 3), np.uint8)
        rgb[..., 0], rgb[..., 1], rgb[..., 2] = 200, 100, 50
        rgb[2, 1] = 255                                   # a white pixel, as bone on a film's screenshot
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "rgb.dcm")
            DF.write_projection(path, rgb, sop_class="1.2.840.10008.5.1.4.1.1.7")
            p = R.read_projection(path, with_pixels=True)
            self.assertEqual(p.pixels.shape, (6, 4))
            self.assertAlmostEqual(p.pixels[0, 0], 0.299 * 200 + 0.587 * 100 + 0.114 * 50)
            self.assertAlmostEqual(p.pixels[2, 1], 255.0)
            self.assertTrue(any("no Pixel Spacing" in q for q in p.problems))
            palette = os.path.join(d, "palette.dcm")
            DF.write_projection(palette, np.zeros((6, 4)), sop_class="1.2.840.10008.5.1.4.1.1.7",
                                attrs={"PhotometricInterpretation": "PALETTE COLOR"})
            with self.assertRaises(SystemExit) as e:
                R.read_projection(palette, with_pixels=True)
            self.assertIn("PALETTE COLOR", str(e.exception))

    def test_a_ct_slice_is_not_a_projection(self):
        hu, aff = small_volume()
        with tempfile.TemporaryDirectory() as d:
            DF.write_ct_series(d, hu, aff)
            with self.assertRaises(SystemExit):
                R.read_projection(os.path.join(d, sorted(os.listdir(d))[0]))

    def test_picture_orientation_is_applied_and_no_scale_is_guessed(self):
        from PIL import Image
        img = np.zeros((40, 25), np.uint8)
        img[5, 3] = 255                                  # row 5, column 3 of the stored image
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "film.jpg")
            exif = Image.Exif()
            exif[0x0112] = 6                             # shown turned 90 degrees clockwise
            Image.fromarray(img).save(path, exif=exif, quality=100)
            p = R.read_projection(path, with_pixels=True)
            self.assertEqual((p.height, p.width), (25, 40))
            r, c = np.unravel_index(int(np.argmax(p.pixels)), p.pixels.shape)
            self.assertEqual((r, c), (3, 40 - 1 - 5))
            self.assertEqual(p.header["exif_orientation"]["value"], 6)
            self.assertIsNone(p.scale["pixel_mm"])
            png = os.path.join(d, "film16.png")
            Image.fromarray((np.arange(12).reshape(3, 4) * 5000).astype(np.uint16)).save(png)
            q = R.read_projection(png, pixel_mm=0.15, with_pixels=True)
            self.assertEqual(q.pixels.max(), 55000)
            self.assertAlmostEqual(q.scale["pixel_mm"], 0.15 / M)

    def test_the_size_is_read_from_the_header_without_the_pixels(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as d:
            dx = os.path.join(d, "dx.dcm")
            DF.write_projection(dx, np.zeros((30, 20)), attrs={"ImagerPixelSpacing": [0.14, 0.14]})
            p = R.read_projection(dx)
            self.assertEqual((p.height, p.width), (30, 20))
            self.assertIsNone(p.pixels)
            # a palette image is refused only where its pixels are decoded, since its size is in Rows and Columns
            palette = os.path.join(d, "palette.dcm")
            DF.write_projection(palette, np.zeros((6, 4)), sop_class="1.2.840.10008.5.1.4.1.1.7",
                                attrs={"PhotometricInterpretation": "PALETTE COLOR"})
            self.assertEqual(R.read_projection(palette).size, (6, 4))
            jpg = os.path.join(d, "turned.jpg")
            exif = Image.Exif()
            exif[0x0112] = 8                             # shown turned 90 degrees anticlockwise
            Image.fromarray(np.zeros((40, 25), np.uint8)).save(jpg, exif=exif)
            q = R.read_projection(jpg)
            self.assertEqual((q.height, q.width), (25, 40))
            self.assertIsNone(q.pixels)
            self.assertEqual(q.size, R.read_projection(jpg, with_pixels=True).pixels.shape)

    def test_a_caller_length_that_is_not_a_positive_number_is_refused(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as d:
            png = os.path.join(d, "film.png")
            Image.fromarray(np.zeros((3, 4), np.uint8)).save(png)
            for bad in (0.0, -0.2, float("nan"), float("inf")):
                with self.assertRaises(SystemExit, msg=str(bad)) as e:
                    R.read_projection(png, pixel_mm=bad)
                self.assertIn("--pixel-mm", str(e.exception))
                with self.assertRaises(SystemExit, msg=str(bad)):
                    R.projection_scale(ds_with(ImagerPixelSpacing=[0.14, 0.14]), override_mm=bad)
        self.assertAlmostEqual(R.projection_scale(ds_with(), override_mm=0.2)["pixel_mm"], 0.2 / M)


class SeriesNamed(unittest.TestCase):
    """--series is held to whatever is read: a folder's series, a lone file's, and never a NIfTI's."""

    def test_a_series_named_for_a_nifti_is_refused(self):
        import nibabel as nib
        hu, aff = small_volume()
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "ct.nii.gz")
            nib.save(nib.Nifti1Image(hu, aff), path)
            with self.assertRaises(SystemExit) as e:
                R.read_volume(path, "1.2.3")
            self.assertIn("NIfTI", str(e.exception))
            self.assertEqual(R.read_volume(path).hu.shape, hu.shape)

    def test_a_lone_file_must_belong_to_the_series_named(self):
        hu, aff = small_volume()
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "enhanced.dcm")
            DF.write_enhanced_ct(path, hu, aff, series_uid="1.2.826.0.1.3680043.10.2")
            with self.assertRaises(SystemExit) as e:
                R.read_volume(path, "1.2.3")
            self.assertIn("no CT series 1.2.3", str(e.exception))
            self.assertEqual(R.read_volume(path, "1.2.826.0.1.3680043.10.2").source, "dicom-enhanced-ct")


if __name__ == "__main__":
    unittest.main()
