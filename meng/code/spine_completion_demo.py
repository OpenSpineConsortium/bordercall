# -*- coding: utf-8 -*-
#
# Derived work Spine Model, Di Meng, Marilyn Keller, Edmond Boyer, Michael J. Black, Sergi Pujades,
# Copyright © Inria and Max Planck Institute, CC BY-NC v2.0 license, 2019-2020 v1.0
# Based on Verse19 Challenge Dataset, Jan S. Kirschke, Anjany Sekuboyina, Maximilian Löffler , CC BY v2.0 license, 2019-2020 v3
#

def proj_ppca(Y, M, C, nb_latent=10):
    '''
        Y is input with missing data
        M, C are the ppca values :
            M : Mean
            C : the reconstruction matrix
    '''
    from numpy import shape, isnan
    from numpy import matmul as mm
    from numpy.linalg import inv

    assert(nb_latent == 10)

    N = shape(Y)[0]
    hidden = isnan(Y)

    missing = hidden.sum()

    print("\tReconstruction from {0:.2f}% missing data".format(100. * missing / N))

    Ye = Y - M
    Ye[hidden] = 0

    CtC = mm(C.T, C)

    X = mm(mm(Ye, C), inv(CtC))

    X[nb_latent:] = 0

    proj = mm(X, C.T)

    Ye[hidden] = proj[hidden]

    return Ye + M


def Y_from_model_mesh(m, M, v_smpl, v_smpl_metadata):
    ''' This function converts "the vertices of a model mesh" into the "ppca representation"
        which includes the local translations.

        The difference between them is:
         - the computation of the local translations from the vertebrae centers
         - the "rigid" registration to the mean positions (as the translation is already factored out)
           -> the ppca was computed with the individual vertebrae unposed to the template shape
        @param: m: a mesh given by the model (v_smpl.r, v_smpl.f)
        @param: M: the mean of the ppca

        extracts the individual vertebrae
        and the translation between them

        translates the vertebrae vertices to be in the same center as the mean vertebrae

        constructs the Y matrix to be used in the reconstruction process
    '''

    from psbody.mesh import Mesh
    from spine_model_utils import get_bone_mesh, get_bone_joint, get_translation_index

    # Create the Y matrix: first the mesh vertices
    import numpy as np
    # Allocate the Y vector
    Y = np.zeros_like(M)

    bone_id_list = v_smpl_metadata['bone_id_list']

    mesh_joints = dict()

    for bone_id in bone_id_list:
        v_start, v_end = v_smpl_metadata[bone_id]['indices']

        mesh_verts = m.v[v_start:v_end]

        mesh_joint = get_bone_joint(v_smpl.J_regressor,
                                    v_smpl_metadata,
                                    bone_id, Mesh(v=mesh_verts, f=[]))

        ppca_verts = M[3*v_start:3*v_end].reshape(-1, 3)

        ppca_joint = get_bone_joint(v_smpl.J_regressor,
                                    v_smpl_metadata,
                                    bone_id, Mesh(v=ppca_verts, f=[]))

        offset = ppca_joint - mesh_joint

        new_verts = mesh_verts + offset

        Y[3*v_start:3*v_end] = new_verts.ravel()

        mesh_joints[bone_id] = mesh_joint

    # Then the local translations
    # The are computed using the joint locations from one vertebra and the consecutive "above"
    # L4 to L5, L4 to L3 and so on until C1 to C2
    for c_bone_id in bone_id_list:
        if c_bone_id == 1:
            # C1 does not have a translation
            continue

        trans = mesh_joints[c_bone_id - 1] - mesh_joints[c_bone_id]

        trans_index = get_translation_index(c_bone_id)
        Y[trans_index:trans_index+3] = trans

    return Y


def cervical_reconstruction_example(Y, v_smpl_metadata,
                                    M, C):

    import numpy as np
    from spine_model_utils import get_translation_index

    nb_bones = 5

    for nb_bone_excluded in range(1, nb_bones+1):

        print ("Excluding {} vertebrae".format(nb_bone_excluded))
        Y_masked = Y.copy()

        for excluded_bone_id in range(1, nb_bone_excluded+1):

            # Mask mesh
            v_start, v_end = v_smpl_metadata[excluded_bone_id]['indices']

            # these indices refer to the vertices, each one is 3D
            # In Y the coordinates are flattened, so we multiply the indices by 3
            Y_start = v_start * 3
            Y_end = v_end * 3
            Y_masked[Y_start:Y_end] = np.nan

            # Mask local translation - which is associated with the next bone_id
            trans_index = get_translation_index(excluded_bone_id + 1)
            Y_masked[trans_index:trans_index+3] = np.nan

        # Complete the masked spine data using the ppca model (M, C,X)
        Y_pred = proj_ppca(Y_masked, M, C)

        # Get the original vertices and the predicted ones
        for excluded_bone_id in range(1, nb_bone_excluded + 1):

            v_start, v_end = v_smpl_metadata[excluded_bone_id]['indices']

            Y_start = v_start * 3
            Y_end = v_end * 3

            # Get first "element"
            orig_data = Y[Y_start:Y_end]
            pred_data = Y_pred[Y_start:Y_end]

            # Compare the ground truth test_vol spine and the extrapolated one
            imputation_abs_err_norm = np.linalg.norm(orig_data.reshape(-1, 3) - pred_data.reshape(-1, 3), axis=1)

            trans_index = get_translation_index(excluded_bone_id + 1)
            orig_trans = Y[trans_index:trans_index+3]
            pred_trans = Y_pred[trans_index:trans_index + 3]
            imputation_abs_err_trans = np.linalg.norm(orig_trans.reshape(-1, 3) - pred_trans.reshape(-1, 3), axis=1)[0]

            # Show some statistics
            print("\tExcluded Bone {} Imputation Error Norm:".format(excluded_bone_id))
            print("\tMax Shape Error in mm: {0:.2f}".format(np.max(imputation_abs_err_norm) * 1000))
            print("\tMean Shape Error in mm: {0:.2f}".format(np.mean(imputation_abs_err_norm) * 1000))
            print("\tTrans Error in mm: {0:.2f}".format(imputation_abs_err_trans * 1000))
            print("")

    return


if __name__ == '__main__':
    from smpl_webuser.serialization import load_model
    from psbody.mesh import Mesh

    from spine_model_utils import current_model_filename, load_model_metadata, load_ppca_metadata

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-M", "--mean_check", action='store_true', help="Demo that starting with the mean all errors are zero")
    args = parser.parse_args()

    print "Reconstruction Demo"

    print "Loading models and metadata ... "
    v_smpl_metadata = load_model_metadata()
    ppca_metadata = load_ppca_metadata()

    M = ppca_metadata['M_pp']
    C = ppca_metadata['C']

    print "\tLoading done"

    if args.mean_check:
        # Use the mean of the ppca as the starting point
        # Predictions will be perfect
        Y = M.copy()
        print "Using the PPCA mean: predictions should be perfect (zero error)."
    else:
        print "Using the Mean Model mesh: predictions should have small errors (approx 0.1 mm max, 0.05-0.07 mm mean)."
        model_filename = current_model_filename
        v_smpl = load_model(model_filename)

        # Example with betas
        v_smpl.betas[0] = 0

        # Create mean mesh
        m = Mesh(v=v_smpl.r, f=v_smpl.f)

        Y = Y_from_model_mesh(m, M, v_smpl, v_smpl_metadata)

    cervical_reconstruction_example(Y, v_smpl_metadata,
                                    M, C)

