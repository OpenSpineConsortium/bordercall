"""The candidate over other regions, for the record: the same reader with its region's
constants changed for the call (not a proposal of these regions)."""
import importlib.util
import os

spec = importlib.util.spec_from_file_location("cand", os.path.join(os.path.dirname(os.path.abspath(__file__)), "cand.py"))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


def over(across, share):
    def fn(v, B, xc):
        old = C.ACROSS_HALF_MM, C.HEIGHT_SHARE
        C.ACROSS_HALF_MM, C.HEIGHT_SHARE = across, share
        try:
            return C.slope(v, B, xc)
        finally:
            C.ACROSS_HALF_MM, C.HEIGHT_SHARE = old
    return fn


x3_h80 = over(3.0, 0.8)
x6_h60 = over(6.0, 0.6)
x6_h80 = over(6.0, 0.8)
