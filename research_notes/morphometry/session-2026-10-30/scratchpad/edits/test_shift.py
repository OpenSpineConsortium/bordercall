import sys
path = sys.argv[1]
src = open(path, encoding="ascii").read()

def swap(old, new, count=1):
    global src
    assert src.count(old) == count, (old[:80], src.count(old))
    src = src.replace(old, new)

swap('''    the CT the row names by its sha256 for the isocentre, its volume's centre; with its edits'
    files and the filter's verdicts beside it."""''', '''    the CT the row names by its sha256 for the isocentre, its volume's centre; with its edits'
    files, how far each moved the render's picture, and the filter's verdicts beside them."""''')

swap('''        cls.folder = cls.render_folder("realism", cls.POSE, 256)
        cls.edits, cls.filter = os.path.join(cls.tmp, "realism-edits"), os.path.join(cls.tmp, "realism-filter")''', '''        cls.folder = cls.render_folder("realism", cls.POSE, 256)
        # the render a smooth random picture; the first edit moves it 3 px along a row and 2 up the
        # image and turns its contrast over, the second moves it 1.5 px along and 0.25 down
        rng = np.random.default_rng(5)
        picture = ndimage.gaussian_filter(rng.normal(size=(256, 256)), 4.0)
        picture = (picture - picture.min()) / np.ptp(picture)
        np.save(os.path.join(cls.folder, "raw", "%s.npy" % cls.SAMPLE), picture.astype(np.float16))
        moved = 1.0 - np.roll(picture, (-2, 3), axis=(0, 1))
        nudged = np.fft.ifft2(ndimage.fourier_shift(np.fft.fft2(picture), (0.25, 1.5))).real
        cls.edits, cls.filter = os.path.join(cls.tmp, "realism-edits"), os.path.join(cls.tmp, "realism-filter")''')

swap('''        for arm, side in ((0, 256), (1, 256), (2, 128)):
            np.save(os.path.join(cls.edits, "edited", "%s__a%d.npy" % (cls.SAMPLE, arm)), np.zeros((side, side), np.float16))''', '''        for arm, image in ((0, moved), (1, nudged), (2, np.zeros((128, 128)))):
            np.save(os.path.join(cls.edits, "edited", "%s__a%d.npy" % (cls.SAMPLE, arm)), image.astype(np.float16))''')

swap('''        self.assertEqual(rec["edits"][0]["file"], "edited/%s__a0.npy" % self.SAMPLE)
        self.assertIn("4 edits of the render, 2 holding its pixels, 1 kept by the filter", said)''', '''        self.assertEqual(rec["edits"][0]["file"], "edited/%s__a0.npy" % self.SAMPLE)
        # each edit's shift, the edit's place less the render's, here at FleXray's 256 canvas too
        for edit, want, within in zip(rec["edits"], ([3.0, -2.0], [1.5, 0.25]), (0.05, 0.2)):
            np.testing.assert_allclose(edit["shift_px"], want, atol=within)
            self.assertAlmostEqual(edit["shift_canvas_px"], math.hypot(*edit["shift_px"]), places=12)
        self.assertEqual([e["shift_px"] for e in rec["edits"][2:]], [None, None])
        self.assertIn("4 edits of the render, 2 holding its pixels, moved %.2f px at most on FleXray's canvas, 1 kept "
                      "by the filter" % rec["edits"][0]["shift_canvas_px"], said)''')

swap('''    def test_a_render_the_records_do_not_bear_out_refuses(self):''', '''    def test_an_edits_shift_is_read_on_any_side_and_none_on_one_grey(self):
        rng = np.random.default_rng(9)
        picture = ndimage.gaussian_filter(rng.normal(size=(96, 160)), 3.0)
        for rows, cols in ((0, 0), (5, -7), (-40, 70)):
            np.testing.assert_allclose(MV.edit_shift(picture, np.roll(picture, (rows, cols), axis=(0, 1))), [cols, rows],
                                       atol=1e-6)
        self.assertIsNone(MV.edit_shift(picture, np.full_like(picture, 0.3)))
        self.assertIsNone(MV.edit_shift(np.zeros_like(picture), picture))

    def test_a_render_the_records_do_not_bear_out_refuses(self):''')
open(path, "w", encoding="ascii").write(src)
print("ok")
