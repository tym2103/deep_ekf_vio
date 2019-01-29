import numpy as np
from log import logger
import transformations


def skew3(v):
    assert (len(v.shape) == 1 and v.shape[0] == 3)

    m = np.zeros([3, 3])
    m[0, 1] = -v[2]
    m[0, 2] = v[1]
    m[1, 0] = v[2]

    m[1, 2] = -v[0]
    m[2, 0] = -v[1]
    m[2, 1] = v[0]

    return m


def unskew3(m):
    assert (m.shape[0] == 3 and m.shape[1] == 3)
    return np.array([m[2, 1], m[0, 2], m[1, 0]])


def log_SO3(C):
    assert (len(C.shape) == 2 and C.shape[0] == 3 and C.shape[1] == 3)

    arccos = (np.trace(C) - 1) / 2

    if np.abs(arccos) > 1:
        phi = 0.0
        logger.print("WARNING: invalid arccos: %f\n" % arccos)
        logger.print("%s\n" % str(C))
    else:
        phi = np.arccos((np.trace(C) - 1) / 2)

    if abs(phi) > 1e-12:
        u = unskew3(C - np.transpose(C)) / (2 * np.sin(phi))
        theta = phi * u
    else:
        theta = 0.5 * unskew3(C - C.transpose())

    return theta


def exp_SO3(phi):
    phi_norm = np.linalg.norm(phi)
    if np.abs(phi_norm) > 1e-12:
        unit_phi = phi / phi_norm
        unit_phi_skewed = skew3(unit_phi)
        m = np.eye(3, 3) + np.sin(phi_norm) * unit_phi_skewed + \
            (1 - np.cos(phi_norm)) * unit_phi_skewed.dot(unit_phi_skewed)
    else:
        phi_skewed = skew3(phi)
        m = np.eye(3, 3) + phi_skewed + 0.5 * phi_skewed.dot(phi_skewed)

    return m


def C_from_T(T):
    return T[0:3, 0:3]


def r_from_T(T):
    return T[0:3, 3]


def T_from_Ct(C, r):
    T = np.eye(4, 4)
    T[0:3, 0:3] = C
    T[0:3, 3] = r

    return T


# reorthogonalize the SO(3) part of SE(3) by normalizing a quaternion
def reorthogonalize_SE3(T):
    # ensure the rotational matrix is orthogonal
    q = transformations.quaternion_from_matrix(T)
    n = np.sqrt(q[0] ** 2 + q[1] ** 2 + q[2] ** 2 + q[3] ** 2)
    q = q / n
    T_new = transformations.quaternion_matrix(q)
    T_new[0:3, 3] = T[0:3, 3]
    return T_new
