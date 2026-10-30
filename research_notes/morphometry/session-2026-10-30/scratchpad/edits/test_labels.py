import sys
path = sys.argv[1]
src = open(path, encoding="ascii").read()

def sub(old, new, count=1):
    global src
    if src.count(old) != count:
        raise SystemExit("expected %d of %r, found %d" % (count, old[:70], src.count(old)))
    src = src.replace(old, new)

sub("""among them, the centroid of each bead of 2.5 mm it rendered on the ends of the phantom's lines,
where each vertebra's channel is above zero, and each vertebra's channel over a volume of one
attenuation as a count of nanoDRR's steps at every pixel; a fourth view, of a crop of the
phantom's slices as SchwingNet's render cuts the CT for each view, and each vertebra's support on
it;""", """among them, the centroid of each bead of 2.5 mm it rendered on the ends of the phantom's lines,
FleXray's labels of each vertebra at the threshold of its training profile, 0.0, where the
vertebra's channel is above zero, and at a bare request's 0.5, and each vertebra's channel over a
volume of one attenuation as a count of nanoDRR's steps at every pixel; a fourth view, of a crop
of the phantom's slices as SchwingNet's render cuts the CT for each view, and each vertebra's
support on it;""")
sub('''def support(v: dict, levels) -> np.ndarray:
    """FleXray's shadow of the levels on the view's render, where their channels are above zero."""''',
'''def support(v: dict, levels) -> np.ndarray:
    """FleXray's shadow of the levels on the view's render, its labels of them at its training
    profile's threshold, 0.0, where their channels are above zero."""''')
sub('''    def test_flexrays_label_mask_lies_within_the_shadow_and_drops_thin_bone(self):
        # FleXray's labels are its channels above 0.5, which bone thinner than about 9 mm along the
        # ray does not reach at the phantom's 1000 HU, 0.0573 per mm, so the lines are set against
        # the shadow, never the mask
        for name, _, v in recorded_views():
            shape = (v["view"]["height"], v["view"]["width"])
            for level in RECORD["phantom"]["ids"]:
                mask = FR.unpack(v["masks"][level], shape)
                self.assertFalse(bool((mask & ~support(v, [level])).any()), (name, level))
            dropped = sum(int((support(v, [lv]) & ~FR.unpack(v["masks"][lv], shape)).sum())
                          for lv in RECORD["phantom"]["ids"])
            self.assertGreater(dropped, 0, name)
''', '''    def test_flexrays_labels_at_a_bare_requests_threshold_need_9_mm_of_bone(self):
        # at a bare request's 0.5, at which SchwingNet's realism programme renders its truth masks,
        # FleXray's label of a vertebra is its channel above 0.5. The channel is at most the bone's
        # attenuation, 0.0573 per mm at 1000 HU, times the step times the samples the vertebra
        # holds, our path length a step short at most, so the mask lies where our path length
        # reaches 0.5 over the attenuation, about 9 mm, and drops thinner bone: the lines are set
        # against the shadow, never the mask
        mu, cut = RECORD["uniform"]["mu_per_mm"], RECORD["label_thresholds"]
        self.assertEqual(cut, {"supports": 0.0, "masks": 0.5})
        for name, cam, v in recorded_views():
            shape = (cam.view.height, cam.view.width)
            src, det = cam.rays(cam.pixel_centres())
            step = (np.linalg.norm(det - src, axis=1) / (RECORD["n_samples"] - 1)).reshape(shape)
            dropped = 0
            for level, i in RECORD["phantom"]["ids"].items():
                mask = FR.unpack(v["masks"][level], shape)
                ours = SH.Volume.from_labels(self.lab, self.aff, i, largest=False).path_length(
                    cam, n_samples=RECORD["n_samples"])
                self.assertFalse(bool((mask & (mu * (ours + step) <= cut["masks"])).any()), (name, level))
                dropped += int(((ours > 0) & ~mask).sum())
            self.assertGreater(dropped, 100, name)
''')
sub('''class Live(unittest.TestCase):
    """FleXray itself: the record's views rendered again give its supports, its counts and its
    camera,''', '''class Live(unittest.TestCase):
    """FleXray itself: the record's views rendered again give its labels at both thresholds, its
    supports where the channels are above zero, its counts and its camera,''')
sub('''            rendered = FR.render(bone, self.lab, self.aff, cam.view)
            for level, i in RECORD["phantom"]["ids"].items():
                np.testing.assert_array_equal(rendered[i] > 0, support(v, [level]), err_msg=name)
''', '''            rendered = FR.render(bone, self.lab, self.aff, cam.view)
            for level, i in RECORD["phantom"]["ids"].items():
                np.testing.assert_array_equal(rendered[i] > 0, support(v, [level]), err_msg=name)
            for key, threshold in RECORD["label_thresholds"].items():
                got = FR.labels(bone, self.lab, self.aff, cam.view, threshold)
                for level, i in RECORD["phantom"]["ids"].items():
                    np.testing.assert_array_equal(got[i], FR.unpack(v[key][level], got.shape[1:]), err_msg=(name, key))
''')
open(path, "w", encoding="ascii", newline="\n").write(src)
print("ok")
