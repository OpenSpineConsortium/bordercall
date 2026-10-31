# -*- coding: utf-8 -*-
#
# Derived work Spine Model, Di Meng, Marilyn Keller, Edmond Boyer, Michael J. Black, Sergi Pujades,
# Copyright © Inria and Max Planck Institute, CC BY-NC v2.0 license, 2019-2020 v1.0
# Based on Verse19 Challenge Dataset, Jan S. Kirschke, Anjany Sekuboyina, Maximilian Löffler , CC BY v2.0 license, 2019-2020 v3
#

def vertebrae_colormap(label):
    return vertebrae_colormap_di("{}".format(label))[:3]


def vertebrae_colormap_di(label):
    import numpy as np

    if label == '0':
        return np.array([0, 0, 0, 1])

    if label == '1':
        return np.array([255 / 255., 102 / 255., 102 / 255., 1])

    if label == '2':
        return np.array([153 / 255., 255 / 255., 51 / 255., 1])

    if label == '3':
        return np.array([255 / 255., 187 / 255., 153 / 255., 1])

    if label == '4':
        return np.array([77 / 255., 225 / 255., 255 / 255., 1])

    if label == '5':
        return np.array([255 / 255., 153 / 255., 255 / 255., 1])

    if label == '6':
        return np.array([153 / 255., 102 / 255., 255 / 255., 1])

    if label == '7':
        return np.array([238 / 255., 255 / 255., 153 / 255., 1])

    if label == '8':
        return np.array([102 / 255., 102 / 255., 255 / 255., 1])

    if label == '9':
        return np.array([255 / 255., 0, 0, 1])

    if label == '10':
        return np.array([128 / 255., 212 / 255., 255 / 255., 1])

    if label == '11':
        return np.array([204 / 255., 255 / 255., 102 / 255., 1])

    if label == '12':
        return np.array([119 / 255., 0, 179 / 255., 1])

    if label == '13':
        return np.array([255 / 255., 255 / 255., 0, 1])

    if label == '14':
        return np.array([204 / 255., 102 / 255., 0, 1])

    if label == '15':
        return np.array([0, 255 / 255., 0, 1])

    if label == '16':
        return np.array([128 / 255., 0, 0, 1])

    if label == '17':
        return np.array([106 / 255., 128 / 255., 0, 1])

    if label == '18':
        return np.array([255 / 255., 0, 255 / 255., 1])

    if label == '19':
        return np.array([0, 68 / 255., 204 / 255., 1])

    if label == '20':
        return np.array([255 / 255., 102 / 255., 128 / 255., 1])

    if label == '21':
        return np.array([179 / 255., 255 / 255., 242 / 255., 1])

    if label == '22':
        return np.array([102 / 255., 51 / 255., 0, 1])

    if label == '23':
        return np.array([0, 77 / 255., 13 / 255., 1])

    if label == '24':
        return np.array([255 / 255., 170 / 255., 0, 1])

    if label == '25':
        return np.array([255 / 255., 255 / 255., 255 / 255., 1])

    else:
        raise ValueError('Unknown label %s ' % label)