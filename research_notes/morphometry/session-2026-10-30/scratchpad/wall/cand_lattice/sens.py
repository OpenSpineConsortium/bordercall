"""Sensitivity variants of candidate A, for the record only: each sets one of cand's bounds and
reads. None of them chose the bounds cand.py keeps."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cand as C

def with_bounds(fn, **kw):
    def run(v, B, xc):
        saved = {k: getattr(C, k) for k in kw}
        for k, x in kw.items():
            setattr(C, k, x)
        try:
            return fn(v, B, xc)
        finally:
            for k, x in saved.items():
                setattr(C, k, x)
    return run

band3 = with_bounds(C.slope, HALF_BAND_MAX_MM=3.0)
band3_plain = with_bounds(C.slope_plain, HALF_BAND_MAX_MM=3.0)
band9 = with_bounds(C.slope, HALF_BAND_MAX_MM=9.0, CANAL_SHARE=0.4)
band9_plain = with_bounds(C.slope_plain, HALF_BAND_MAX_MM=9.0, CANAL_SHARE=0.4)
height80 = with_bounds(C.slope, HEIGHT_SHARE=0.8)
run1 = with_bounds(C.slope, RUN_MM=1.0)
