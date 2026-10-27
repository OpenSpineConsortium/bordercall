"""Synthetic DICOM files for the tests, written with pydicom: a CT series, one Enhanced CT Image
holding the same volume as frames, and a projection, grey or RGB. No patient and no scanner:
every value is made here, so a test knows what the reader must give back.
"""
from __future__ import annotations

import os
from typing import Dict, Optional, Sequence

import numpy as np

from ..readers import CT_IMAGE, ENHANCED_CT, LPS_TO_RAS

INTERCEPT = -1024.0


def meta(sop_class: str, sop_instance: str):
    from pydicom.dataset import FileMetaDataset
    from pydicom.uid import ExplicitVRLittleEndian
    fm = FileMetaDataset()
    fm.MediaStorageSOPClassUID = sop_class
    fm.MediaStorageSOPInstanceUID = sop_instance
    fm.TransferSyntaxUID = ExplicitVRLittleEndian
    return fm


def dataset(sop_class: str, uid_root: str, n: int):
    from pydicom.dataset import FileDataset
    instance = "%s.%d" % (uid_root, n + 1)
    ds = FileDataset(None, {}, file_meta=meta(sop_class, instance), preamble=b"\0" * 128)
    ds.SOPClassUID, ds.SOPInstanceUID = sop_class, instance
    ds.StudyInstanceUID = uid_root + ".900"
    return ds


def set_pixels(ds, stored: np.ndarray, frames: int = 1) -> None:
    ds.SamplesPerPixel, ds.PhotometricInterpretation = 1, "MONOCHROME2"
    ds.Rows, ds.Columns = int(stored.shape[-2]), int(stored.shape[-1])
    ds.BitsAllocated, ds.BitsStored, ds.HighBit, ds.PixelRepresentation = 16, 16, 15, 1
    if frames > 1:
        ds.NumberOfFrames = frames
    ds.PixelData = np.ascontiguousarray(stored.astype(np.int16)).tobytes()


def lps_frame(affine_ras: np.ndarray):
    """The row and column directions, the step between slices and the first position in LPS, and
    the spacings, of a RAS affine whose first two columns lie in the slice."""
    lps = LPS_TO_RAS @ np.asarray(affine_ras, float)
    dc, dr = np.linalg.norm(lps[:3, 0]), np.linalg.norm(lps[:3, 1])
    return lps[:3, 0] / dc, lps[:3, 1] / dr, lps[:3, 2], lps[:3, 3], dr, dc


def write_ct_series(folder: str, hu: np.ndarray, affine_ras: np.ndarray, series_uid: str = "1.2.826.0.1.3680043.10.1",
                    covariates: Optional[Dict[str, object]] = None, order: Optional[Sequence[int]] = None,
                    drop: Sequence[int] = ()) -> None:
    """hu[i, j, k] as one CT Image per k, stored as int16 with an intercept of -1024. Instance
    Numbers run against the slices' order and the files are written in `order`, so a reader that
    sorts by either is caught; slices in `drop` are left out."""
    os.makedirs(folder, exist_ok=True)
    row, col, step, first, dr, dc = lps_frame(affine_ras)
    nk = hu.shape[2]
    for n in (order if order is not None else range(nk)):
        if n in drop:
            continue
        ds = dataset(CT_IMAGE, series_uid, n)
        ds.SeriesInstanceUID, ds.Modality = series_uid, "CT"
        ds.ImageType = ["ORIGINAL", "PRIMARY", "AXIAL"]
        ds.InstanceNumber = nk - n
        ds.ImageOrientationPatient = [float(v) for v in np.r_[row, col]]
        ds.ImagePositionPatient = [float(v) for v in first + n * step]
        ds.PixelSpacing = [float(dr), float(dc)]
        ds.SliceThickness = float(np.linalg.norm(step))
        ds.RescaleSlope, ds.RescaleIntercept = 1.0, INTERCEPT
        for k, v in (covariates or {}).items():
            setattr(ds, k, v)
        set_pixels(ds, np.round(hu[:, :, n].T - INTERCEPT))
        ds.save_as(os.path.join(folder, "f%03d.dcm" % ((n * 7) % 1000)), enforce_file_format=True)


def write_localizer(path: str, series_uid: str) -> None:
    ds = dataset(CT_IMAGE, series_uid, 999)
    ds.SeriesInstanceUID, ds.Modality = series_uid, "CT"
    ds.ImageType = ["ORIGINAL", "PRIMARY", "LOCALIZER"]
    ds.ImageOrientationPatient = [1.0, 0.0, 0.0, 0.0, 0.0, -1.0]
    ds.ImagePositionPatient = [0.0, 0.0, 0.0]
    ds.PixelSpacing = [1.0, 1.0]
    set_pixels(ds, np.zeros((8, 8)))
    ds.save_as(path, enforce_file_format=True)


def write_enhanced_ct(path: str, hu: np.ndarray, affine_ras: np.ndarray,
                      series_uid: str = "1.2.826.0.1.3680043.10.2", rescale_type: str = "HU",
                      macros: Optional[Dict[str, Dict[str, object]]] = None) -> None:
    """The same volume as one Enhanced CT Image: orientation, pixel measures and rescale shared,
    each frame's position its own, frames written top slice first so the reader must sort.
    `macros` adds shared functional group macros by sequence name, each with its attributes, as
    {"CTXRayDetailsSequence": {"KVP": 120}}."""
    from pydicom.dataset import Dataset
    from pydicom.sequence import Sequence as Seq
    row, col, step, first, dr, dc = lps_frame(affine_ras)
    nk = hu.shape[2]
    ds = dataset(ENHANCED_CT, series_uid, 0)
    ds.SeriesInstanceUID, ds.Modality = series_uid, "CT"
    ds.ImageType = ["ORIGINAL", "PRIMARY", "VOLUME", "NONE"]
    shared = Dataset()
    ori, meas, resc = Dataset(), Dataset(), Dataset()
    ori.ImageOrientationPatient = [float(v) for v in np.r_[row, col]]
    meas.PixelSpacing, meas.SliceThickness = [float(dr), float(dc)], float(np.linalg.norm(step))
    resc.RescaleSlope, resc.RescaleIntercept, resc.RescaleType = 1.0, INTERCEPT, rescale_type
    shared.PlaneOrientationSequence, shared.PixelMeasuresSequence = Seq([ori]), Seq([meas])
    shared.PixelValueTransformationSequence = Seq([resc])
    for sequence, attrs in (macros or {}).items():
        item = Dataset()
        for k, v in attrs.items():
            setattr(item, k, v)
        setattr(shared, sequence, Seq([item]))
    ds.SharedFunctionalGroupsSequence = Seq([shared])
    order = list(range(nk))[::-1]
    per = []
    for n in order:
        item, pos, kind = Dataset(), Dataset(), Dataset()
        pos.ImagePositionPatient = [float(v) for v in first + n * step]
        kind.FrameType = ["ORIGINAL", "PRIMARY", "VOLUME", "NONE"]
        item.PlanePositionSequence, item.CTImageFrameTypeSequence = Seq([pos]), Seq([kind])
        per.append(item)
    ds.PerFrameFunctionalGroupsSequence = Seq(per)
    set_pixels(ds, np.stack([np.round(hu[:, :, n].T - INTERCEPT) for n in order]), frames=nk)
    ds.save_as(path, enforce_file_format=True)


def set_colour_pixels(ds, rgb: np.ndarray) -> None:
    """rgb[row, column, channel] as 8-bit RGB, channels interleaved pixel by pixel."""
    ds.SamplesPerPixel, ds.PhotometricInterpretation, ds.PlanarConfiguration = 3, "RGB", 0
    ds.Rows, ds.Columns = int(rgb.shape[0]), int(rgb.shape[1])
    ds.BitsAllocated, ds.BitsStored, ds.HighBit, ds.PixelRepresentation = 8, 8, 7, 0
    ds.PixelData = np.ascontiguousarray(rgb.astype(np.uint8)).tobytes()


def write_projection(path: str, pixels: np.ndarray, sop_class: str = "1.2.840.10008.5.1.4.1.1.1.1",
                     attrs: Optional[Dict[str, object]] = None, monochrome1: bool = False) -> None:
    """One radiograph, pixels[row, column] stored as given (MONOCHROME1 if asked), or
    pixels[row, column, channel] stored as RGB."""
    ds = dataset(sop_class, "1.2.826.0.1.3680043.10.3", 0)
    ds.SeriesInstanceUID, ds.Modality = "1.2.826.0.1.3680043.10.3.1", "DX"
    if pixels.ndim == 3:
        set_colour_pixels(ds, pixels)
    else:
        set_pixels(ds, pixels)
    if monochrome1:
        ds.PhotometricInterpretation = "MONOCHROME1"
    for k, v in (attrs or {}).items():
        setattr(ds, k, v)
    ds.save_as(path, enforce_file_format=True)
