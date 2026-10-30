import sys
path = sys.argv[1]
src = open(path).read()
def swap(old, new):
    global src
    assert src.count(old) == 1, old[:70]
    src = src.replace(old, new)
swap('''        cls.plain = M.measure_file(cls.path, "verse", "0001")
        cls.whole = read(os.path.join(os.path.dirname(cls.one(cls, "whole")), "..", "lines", "0001.csv"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def one(self, name: str, stamp: str = "") -> str:
        top = os.path.join(self.tmp, name)
        for sub in ("rows", "lines", "frames"):
            os.makedirs(os.path.join(top, sub), exist_ok=True)
        out = os.path.join(top, "rows", "0001.csv")
        RUN.one_study((self.path, "verse", "0001", out, stamp or RUN.code_stamp(True), True))
        return out
''', '''        cls.plain = M.measure_file(cls.path, "verse", "0001")
        cls.one("whole")
        cls.whole = read(os.path.join(cls.tmp, "whole", "lines", "0001.csv"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    @classmethod
    def one(cls, name: str, stamp: str = "") -> str:
        top = os.path.join(cls.tmp, name)
        for sub in ("rows", "lines", "frames"):
            os.makedirs(os.path.join(top, sub), exist_ok=True)
        out = os.path.join(top, "rows", "0001.csv")
        RUN.one_study((cls.path, "verse", "0001", out, stamp or RUN.code_stamp(True), True))
        return out
''')
swap('''            self.assertEqual((x.status, x.rule, x.panel), (y.status, y.rule, y.panel), x.key)
            self.assertTrue(math.isclose(x.value, y.value, rel_tol=0, abs_tol=1e-12), x.key)
            np.testing.assert_array_equal(x.a, y.a)''', '''            self.assertEqual((x.status, x.rule, x.panel), (y.status, y.rule, y.panel), x.key)
            np.testing.assert_array_equal([x.value, x.measured], [y.value, y.measured], err_msg=x.key)
            np.testing.assert_array_equal(x.a, y.a)''')
open(path, "w").write(src)
print("ok")
