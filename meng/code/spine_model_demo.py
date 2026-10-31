# -*- coding: utf-8 -*-
#
# Derived work Spine Model, Di Meng, Marilyn Keller, Edmond Boyer, Michael J. Black, Sergi Pujades,
# Copyright © Inria and Max Planck Institute, CC BY-NC v2.0 license, 2019-2020 v1.0
# Based on Verse19 Challenge Dataset, Jan S. Kirschke, Anjany Sekuboyina, Maximilian Löffler , CC BY v2.0 license, 2019-2020 v3
#

def _create_cage(vs, radius=1e-2):
    ''' Given an array of 3d vertices, it creates a *cage* containing all given vertices inside.
    The output are a set of spheres with the "corners" of the bounding box of the points.

    :param vs: an array of 3d points
    :returns: an array of eight spheres, creating a *cage*
    '''
    from itertools import product
    from numpy import asarray
    from psbody.mesh.sphere import Sphere
    return([Sphere(asarray(corner), radius=radius).to_mesh()
            for corner in product(*zip(vs.min(axis=0), vs.max(axis=0)))])


def _create_cage_from_meshes(meshes, radius=1e-2):
    ''' Given an iterable with meshes, their vertices are concatenated
    and a cage is created using :func:`create_cage`.

    :param meshes: an iterable with meshes
    :type meshes: Mesh
    :returns: an array of eight spheres, creating a *cage*

    .. seealso:: :func:`create_cage`
    '''

    from numpy import zeros, vstack
    cage_v = zeros([0, 3])
    for m in meshes:
        cage_v = vstack((cage_v, m.v))

    return _create_cage(cage_v, radius=radius)



def create_cage(model):
    from psbody.mesh import Mesh
    model.betas[0] = 3
    m1 = Mesh(v=v_smpl.r, f=v_smpl.f)
    model.betas[0] = 0

    model.trans[0] = 0.25
    m2 = Mesh(v=v_smpl.r, f=v_smpl.f)

    model.trans[0] = -0.25
    m3 = Mesh(v=v_smpl.r, f=v_smpl.f)

    model.trans[0] = 0

    return _create_cage_from_meshes([m1, m2, m3], radius=0.0005)


def spheres_from_joints(model):
    from psbody.mesh.sphere import Sphere
    from numpy import asarray
    from verse_colors import vertebrae_colormap

    radius = 0.02
    spheres = []
    for i, center in enumerate(model.J.r):
        sphere = Sphere(asarray(center), radius=radius).to_mesh()
        sphere.set_vertex_colors(vertebrae_colormap(24- i))

        spheres.append(sphere)

    return spheres


if __name__ == '__main__':
    from smpl_webuser.serialization import load_model

    from psbody.mesh import Mesh, MeshViewer
    from psbody.mesh.colors import name_to_rgb
    from psbody.mesh.sphere import Sphere

    import numpy as np
    from time import sleep

    from spine_model_utils import current_model_filename, load_model_metadata,\
                                  get_bone_mesh, get_bone_joint, rotate
    from verse_colors import vertebrae_colormap

    # Parser for the input options
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-R", "--global_rot", action='store_true', help="Demos global rotation parameter")
    parser.add_argument("-r", "--local_rot", action='store_true', help="Demos local rotation parameter")
    parser.add_argument("-B", "--shape_space", action='store_true', help="Demos shape space parameter")
    parser.add_argument("-I", "--individual_joints", action='store_true', help="Demos individual joint centers")
    parser.add_argument("-J", "--jointlocation", action='store_true', help="Demos all joint centers")
    args = parser.parse_args()

    #
    model_filename = current_model_filename
    model_version = model_filename[-6: -4]

    v_smpl_metadata = load_model_metadata()

    show_global_rot = args.global_rot
    show_local_rot = args.local_rot
    show_shape_space = args.shape_space
    show_individual_joints = args.individual_joints
    show_jointlocation = args.jointlocation

    print "Demoing model ", model_version, "(", model_filename, ")"

    v_smpl = load_model(model_filename)

    mv = MeshViewer()
    m = Mesh(v=v_smpl.r, f=v_smpl.f)

    mv.static_meshes = create_cage(v_smpl)

    mv.set_dynamic_meshes([m])

    mv.set_background_color(np.array([0.75, 0.75, 0.75]))
    sleep(0.5)

    sleep_time = 0.3
    radius = 0.02

    camera_orientations = {
        'front': [0, 0, 0],
        'side': [0., np.pi / 2, 0.]
    }

    bone_id_list = v_smpl_metadata['bone_id_list']

    if show_global_rot:
        # rotate global around y
        for y_angle in np.linspace(0, 2 * np.pi, num=int(360/20)):
            v_smpl.pose[1] = y_angle

            m.v = v_smpl.r
            mv.set_dynamic_meshes([m])
            sleep(sleep_time)

        v_smpl.pose[1] = 0

    if show_local_rot:
        # rotate around y axis the different parts
        for i in range(4, v_smpl.pose.shape[0], 3):
            for angle in np.linspace(0, 2 * np.pi, num=int(360/45)):
                v_smpl.pose[i] = angle

                m.v = v_smpl.r
                mv.set_dynamic_meshes([m])
                sleep(sleep_time)

            v_smpl.pose[i] = 0

    # Display the shape space
    if show_shape_space:

        colors = ['bisque', 'lavender', 'honeydew', 'gray', 'seashell']

        # Demo 5 betas
        nb_betas = 5

        for orientation in camera_orientations:
            for i in range(nb_betas):
                mv.set_background_color(name_to_rgb[colors[i % len(colors)]])
                for offset in np.linspace(0, 2, num=6):
                    v_smpl.betas[i] = offset

                    m.v = v_smpl.r
                    m.v = rotate(m.v, camera_orientations[orientation])

                    mv.set_dynamic_meshes([m])
                    sleep(sleep_time)

                for offset in reversed(list(np.linspace(-2, 2, num=10))):
                    v_smpl.betas[i] = offset

                    m.v = v_smpl.r
                    m.v = rotate(m.v, camera_orientations[orientation])
                    mv.set_dynamic_meshes([m])
                    sleep(sleep_time)

                v_smpl.betas[i] = 0

    # Display individual joint locations sequentially
    if show_individual_joints:

        for orientation in camera_orientations:
            for bone_id in reversed(list(range(1, 25))):

                m1 = get_bone_mesh(m, v_smpl_metadata, bone_id)

                m1.v = rotate(m1.v, camera_orientations[orientation])

                joint_center = get_bone_joint(v_smpl.J_regressor,
                                              v_smpl_metadata,
                                              bone_id, m1)

                sphere = Sphere(np.asarray(joint_center), radius=radius).to_mesh()
                sphere.set_vertex_colors(vertebrae_colormap(bone_id))

                mv.set_dynamic_meshes([m1, sphere])
                sleep(sleep_time)

    # Display all joint locations at the same time
    if show_jointlocation:

        m = Mesh(v=v_smpl.r, f=v_smpl.f)
        spheres = spheres_from_joints(v_smpl)

        mv.set_dynamic_meshes([m] + spheres)
        sleep(sleep_time)

