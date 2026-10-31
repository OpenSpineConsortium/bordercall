# -*- coding: utf-8 -*-
#
# Derived work Spine Model, Di Meng, Marilyn Keller, Edmond Boyer, Michael J. Black, Sergi Pujades,
# Copyright © Inria and Max Planck Institute, CC BY-NC v2.0 license, 2019-2020 v1.0
# Based on Verse19 Challenge Dataset, Jan S. Kirschke, Anjany Sekuboyina, Maximilian Löffler , CC BY v2.0 license, 2019-2020 v3
#

from os.path import join, dirname, abspath

# v10
current_model_filename = join(dirname(abspath(__file__)), 'models/vertebra_smpl_v10.pkl')
current_model_metadata_filename = current_model_filename.replace('.pkl', '_metadata.pkl')
current_ppca_metadata_filename = current_model_filename.replace('.pkl', '_ppca_metadata.pkl')


def load_model_metadata():
    from pickle import load
    return load(open(current_model_metadata_filename))


def load_ppca_metadata():
    from pickle import load
    return load(open(current_ppca_metadata_filename))


def get_bone_mesh(full_mesh, v_smpl_metadata, bone_id):
    from psbody.mesh import Mesh
    v_start, v_end = v_smpl_metadata[bone_id]['indices']
    return Mesh(v=full_mesh.v[v_start:v_end],
                f=v_smpl_metadata[bone_id]['faces'])


def get_translation_index(bone_id):
    end_vertices_index = 381855

    assert(bone_id in range(2,25))

    # Translations are saved in reverse order:
    # - the first one is the one from L5 to L4 and so on
    trans_index_offset = (24 - bone_id) * 3

    return end_vertices_index + trans_index_offset


def get_bone_joint(joint_regressor, v_smpl_metadata, bone_id, mesh):
    import numpy as np

    nb_vertebrae = v_smpl_metadata['nb_vertebrae']
    regressor_index = nb_vertebrae - bone_id
    v_start, v_end = v_smpl_metadata[bone_id]['indices']

    reg_mat = joint_regressor.toarray()[regressor_index, v_start:v_end]

    J_tmpx = np.dot(reg_mat, mesh.v[:, 0])
    J_tmpy = np.dot(reg_mat, mesh.v[:, 1])
    J_tmpz = np.dot(reg_mat, mesh.v[:, 2])

    return np.array([[J_tmpx, J_tmpy, J_tmpz]])


def rotate(v, angles):
    '''
    This function rotates the vertices along each axis step by step
    :param v: 2D numpy array of size (mxn), where m is number of vertices and n is 3. "v" represents the set of 3D vertices.
    :param angles: list of 3 angles(x,y,z) in radians
    :return: rotated set of vertices
    '''
    import cv2
    import numpy as np

    for idx, angle in enumerate(angles):
        # theta is in radians
        theta = [0.] * 3
        theta[idx] = angle
        rodr_matrix, _ = cv2.Rodrigues(np.array(theta))
        v = v.dot(rodr_matrix)

    return v

