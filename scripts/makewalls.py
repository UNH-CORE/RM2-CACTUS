#!/usr/bin/env python
"""Generate walls for CACTUS simulation.

Adapted from work by Phillip Chiu, Sandia National Labs, August 25, 2015:
https://gist.github.com/whophil/e5405071a143b38aa4d64dbcd4acef3a
"""

import os
import numpy as np
import math
from __future__ import print_function


def gen_quad_grid(a, b, c, d, n1, n2):
    """Generate a structured grid for a quadrilateral with four specified
    corners.

    Arguments
    ---------
    a, b, c, d: tuples of length 3
        (x,y,z) coordinates of four quadrilateral nodes.
    n1 : int
        Number of grid nodes in the a->b direction.
    n2: int
        Number of grid nodes in the a->d direction.

    Returns
    -------
    x, y, z : numpy arrays
        Numpy arrays of the x, y, and z locations of all grid nodes.
    """

    # convert to np.arrays (if they are not)
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    d = np.array(d)

    # check if four corners of quadrilater are coplanar
    if np.linalg.det(np.vstack([b - a, c - a, d - a])) != 0:
        print 'Error, points are not collinear.'
        return

    # allocate storage for plane (since this is a plane, n3 = 1 always)
    x = np.zeros([n1, n2, 1])
    y = np.zeros([n1, n2, 1])
    z = np.zeros([n1, n2, 1])

    # define r,s coordinate system (for weighting)
    r = np.linspace(-1, 1, n1)
    s = np.linspace(-1, 1, n2)

    # compute coordinates of grid points by taking a weighted average of
    # node points
    for i, r_i in enumerate(r):
        for j, s_j in enumerate(s):
            x[i,j,0], y[i,j,0], z[i,j,0] = 0.25 * ( (1-r_i)*(1-s_j)*a +
                                                    (1+r_i)*(1-s_j)*b +
                                                    (1+r_i)*(1+s_j)*c +
                                                    (1-r_i)*(1+s_j)*d )

    # return the grid arrays
    return x, y, z


def write_to_p3d_multi(coords, p3d_filename):
    """Write an ASCII-formatted, multi-block, structured Plot3D mesh.

       Arguments
       ---------
       coords : list
           A list containing mesh data as (x,y,z) tuples, where x,y,z are 2-D
           numpy-arrays.
       p3d_filename : str
           Path to output filename.
       """

    # see how many blocks were passed in
    num_blocks = len(coords)

    # allocate storage
    size = np.zeros(num_blocks, dtype=int)

    with open(p3d_filename, 'w') as f:
        # write number of blocks
        print >> f, num_blocks

        # write block dimensions
        for nbi, (x, y, z) in enumerate(coords):
            if x.shape != y.shape or y.shape != z.shape:
                print 'Error: X,Y,Z are different shape!.'
                return

            nx, ny, nz = x.shape
            size[nbi] = nx*ny*nz

            print >> f, nx, ny, nz

        # write block cordinates
        for nbi, (x, y, z) in enumerate(coords):
            x = x.T
            y = y.T
            z = z.T

            for i in range(size[nbi]):
                print >>f, x.item(i)
            for i in range(size[nbi]):
                print >>f, y.item(i)
            for i in range(size[nbi]):
                print >>f, z.item(i)


def quad_nxny_from_ds(quadcoords, ds1max, ds2max=None):
    """Return the number of node points needed to give a desired spacing in a
    quad.

    Arguments
    ---------
        quadcoords : list of tuples
            A list of four (x,y,z) tuples which are the corners of the quad.
    Returns
    -------
        n1, n2 : int
           number of node points in the a->b and a->d directions"""
    if not ds2max:
        ds2max = ds1max

    # compute lengths of sides
    A = np.linalg.norm(quadcoords[1] - quadcoords[0])
    B = np.linalg.norm(quadcoords[2] - quadcoords[1])
    C = np.linalg.norm(quadcoords[3] - quadcoords[2])
    D = np.linalg.norm(quadcoords[0] - quadcoords[3])

    n1 = int(max([A,C])/ds1max) + 1
    n2 = int(max([B,D])/ds2max) + 1

    return n1,n2


if __name__ == "__main__":
    W = 3.66
    H = 2.44
    L = 10.0

    coords = {0: np.array([0,0,W]),
              1: np.array([0,H,W]),
              2: np.array([L,H,W]),
              3: np.array([L,0,W]),
              4: np.array([0,0,0]),
              5: np.array([0,H,0]),
              6: np.array([L,H,0]),
              7: np.array([L,0,0])}

    quads = {'right': (0,1,2,3),
             'top': (1,5,6,2),
             'left': (5,4,7,6),
             'bottom': (4,0,3,7)}

    # Relative position of turbine center
    x_center = L/2 # m
    y_center = W/2 # m
    z_center = H/2 # m

    p_rel = np.array([x_center, y_center, z_center])

    # Turbine radius
    R = 0.5375

    # transform to center at hub, N.D. by R
    for key,coord in coords.iteritems():
        coords[key] = (coord - p_rel)/R

    # specify desired spacing for the quads
    ds_quads = {'right': 0.50,
                'top': 0.50,
                'left': 0.50,
                'bottom': 0.50}

    n = {}

    # loop through the quads
    for quad_name, quad_node_ids in quads.iteritems():
        # get the coordinates of the four corners and put them into a list
        quad_coords = [coords[node_id] for node_id in quad_node_ids]

        # compute how many elements are needed for the desired spacing
        n1t, n2t = quad_nxny_from_ds(quad_coords, ds_quads[quad_name])

        n[quad_name] = (n1t, n2t)

    xs = []
    ys = []
    zs = []

    # generate a mesh for all the points
    for quad_name, quad_node_ids in quads.iteritems():
        # get the coordinates of the four corners and put them into a list
        quad_coords = [coords[node_id] for node_id in quad_node_ids]

        # extract these elements
        a = np.array(quad_coords[0])
        b = np.array(quad_coords[1])
        c = np.array(quad_coords[2])
        d = np.array(quad_coords[3])

        # generate the grids
        n1 = n[quad_name][0]
        n2 = n[quad_name][1]
        x, y, z = gen_quad_grid(a, b, c, d, n1, n2)

        # append them to a list of grids
        xs.append(x)
        ys.append(y)
        zs.append(z)

    coords = [(x,y,z) for x,y,z in zip(xs,ys,zs)]
    write_to_p3d_multi(coords, nb_dir + 'easy_tunnel.xyz')
