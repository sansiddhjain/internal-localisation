import math
from shapely.geometry import Point, Polygon
from shapely.ops import cascaded_union
from itertools import combinations


def fi(circles):
    cs = [Point(c[0][0], c[0][1]).buffer(c[1]) for c in circles]
    intersections = [a.intersection(b) for a, b in combinations(cs, 2)]

    intersection = []
    for each in intersections:
        if each.area != 0:
            intersection.append(each)

    ans = cs[0]
    for c in cs:
        ans = ans.intersection(c)

    if(ans.area != 0):
        return ans.centroid

    if(len(intersection) != 0):
        return min(intersection, key=lambda x: x.area).centroid

    return None

def heuristic_1(circles):
    cs = [Point(c[0][0], c[0][1]).buffer(c[1]) for c in circles]
    ans = cs[0]
    for c in cs:
        ans = ans.intersection(c)

    if(ans.area != 0):
        return ans.centroid

    return None

def heuristic_2(circles):
    cs = [Point(c[0][0], c[0][1]).buffer(c[1]) for c in circles]
    intersections = [a.intersection(b) for a, b in combinations(cs, 2)]
    weights = [1 / (a[1] * b[1]) for a, b in combinations(circles, 2)]

    centroids = []
    weight = []
    for i, w in zip(intersections, weights):
        if i.area != 0:
            centroids.append(i.centroid)
            weight.append(w)

    ans = cs[0]
    for c in cs:
        ans = ans.intersection(c)

    if(ans.area != 0):
        return ans.centroid

    if(len(centroids) != 0):
        x, y = 0, 0
        t = 0
        for c, w in zip(centroids, weight):
            x += c.x * w
            y += c.y * w
            t += w

        return Point(x / t, y / t)

    return None

def heuristic_3(circles):
    # cs = [Point(c[0][0], c[0][1]).buffer(c[1]) for c in circles]
    # intersections = [a.intersection(b) for a, b in combinations(cs, 2)]
    # weights = [1 / (a[1] * b[1]) for a, b in combinations(circles, 2)]

    # centroids = []
    # weight = []
    # for i, w in zip(intersections, weights):
    #     if i.area != 0:
    #         centroids.append(i.centroid)
    #         weight.append(w)

    # ans = cs[0]
    # for c in cs:
    #     ans = ans.intersection(c)

    # if(ans.area != 0):
    #     return ans.centroid

    x, y = 0, 0
    t = 0
    for c in circles:
        w = 1.0 / (c[1])
        x += c[0][0] * w
        y += c[0][1] * w
        t += w

    return Point(x / t, y / t)


# Using either of the two methods seems to give same results

def signal_strength_to_distance(signal, freq):
    distance = 10 ** ((27.55 + abs(signal) - (20 * math.log10(freq * 1000))) / 20.0)
    distance = distance * 39.3701  # converting into inches
    return distance / 34


def rssi_to_dis(signal):
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
