import math
from shapely.geometry import Point
from scipy.optimize import fmin_tnc
import numpy as np


aps = {
    1: (-22, 1),
    2: (0, 1),
    3: (0, 24),
    4: (-22, 26)
}


def length(v):
    return math.sqrt(v[0]**2 + v[1]**2)


def dot_product(v, w):
    return v[0] * w[0] + v[1] * w[1]


def determinant(v, w):
    return v[0] * w[1] - v[1] * w[0]


def inner_angle(v, w):
    cosx = dot_product(v, w) / (length(v) * length(w))
    rad = math.acos(cosx)  # in radians
    return rad, cosx

def heuristic_3(circles):
    x, y = 0, 0
    t = 0
    for c in circles:
        w = 1.0 / (c[1])
        x += c[0][0] * w
        y += c[0][1] * w
        t += w

    return Point(x / t, y / t)


def jitter_error(x, y, x1, y1, x2, y2):
    return inner_angle ([x-x2, y-y2], [x2-x1, y2-y1])


def dell_jitter_error(x, y, x1, y1, x2, y2):
    if (x1 == x2 and y1 == y2):
        return 0, 0
    c = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    nr = (x - x2) * (x2 - x1) + (y - y2) * (y2 - y1)
    ans1 = (x2 - x1) / math.sqrt((x - x2)**2 + (y - y2)**2)
    ans1 -= (nr * (x - x2)) / (((x - x2)**2 + (y - y2)**2)**(1.5))
    ans1 *= (1 / c)

    ans2 = (x2 - x1) / math.sqrt((x - x2)**2 + (y - y2)**2)
    ans2 -= (nr * (x - x2)) / (((x - x2)**2 + (y - y2)**2)**(1.5))
    ans2 *= (1 / c)

    return ans1, ans2


def fs(z, *args):
    x, y = z
    cids, powers, params, x1, y1, x2, y2 = args

    F = 0
    jitters = 0
    for cid, p in zip(cids, powers):
        x0, y0 = aps[cid]
        hc = math.sqrt((x - x0)**2 + (y - y0)**2) * 39.3701 / 34
        F += (params[cid][0] - p - 10 * params[cid][1] * np.log10(hc))**2

    jac = np.zeros([2, ])
    jitter_jac = np.zeros([2, 1])

    for cid, p in zip(cids, powers):
        x0, y0 = aps[cid]
        hc = math.sqrt((x - x0)**2 + (y - y0)**2) * 39.3701 / 34

        jac[0] += (2 * (params[cid][0] - p - 10 * params[cid][1] * np.log10(hc)) * 10 * params[cid][1] * (x0 - x)) / (hc * hc)
        jac[1] += (2 * (params[cid][0] - p - 10 * params[cid][1] * np.log10(hc)) * 10 * params[cid][1] * (y0 - y)) / (hc * hc)

    jx, jy = dell_jitter_error(x, y, x1, y1, x2, y2)

    jac[0] /= F
    jac[1] /= F

    theta, cosx = jitter_error(x, y, x1, y1, x2, y2)
    if cosx == 1:
        cosx = 0.99
    elif cosx == -1:
        cosx = -0.99
    jac[0] += jx * (-1 / math.sqrt(1 - cosx*cosx))
    jac[1] += jy * (-1 / math.sqrt(1 - cosx*cosx))
    return np.log(F) + theta, jac


def optimum(cids, powers, params, zinit, x1, y1, x2, y2):
    z = fmin_tnc(fs, list(zinit), args=(cids, powers, params, x1, x2, y1, y2))
    print(z[0])
    return z[0]


def rssi_to_dis(signal, p0, epsi):
    return (10**((p0 - signal) / (10 * epsi))) * (39.3701 / 34)


def rssi_to_dis_2(signal):
    n = 3
    return (10 ** ((-40 - signal) / (10 * n))) * (39.3701 / 34)


def root_mean_square_error(validation, test):
    error = []
    for time in validation:
        if time in test:
            p1 = Point(validation[time][0], validation[time][1])
            p2 = Point(test[time][0], test[time][1])
            error.append(p1.distance(p2))

    error = [e * e for e in error]
    l = len(error)
    return math.sqrt(sum(error) / l)
