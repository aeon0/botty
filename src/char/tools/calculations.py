import random
import numpy as np
from math import cos, sin, dist, pi, radians, degrees

# return location of a point on a circle
def point_on_circle(radius: float, theta_deg: float, center: np.ndarray = (0, 0)) -> tuple[int, int]:
    theta = radians(theta_deg)
    res = center + radius * np.array([cos(theta), sin(theta)])
    return tuple([round(i) for i in res])

# return location of a point equidistant from origin randomly distributed between theta of spread_deg
def spread(pos_abs: tuple[float, float], spread_deg: float) -> tuple[int, int]:
    x1, y1 = pos_abs
    start_deg = degrees(np.arctan2(y1, x1))
    random_theta_deg = random.uniform(start_deg-spread_deg/2, start_deg+spread_deg/2)
    return point_on_circle(radius = dist(pos_abs, (0, 0)), theta_deg = random_theta_deg)

# return random point within circle centered at x1, y1 with radius r
def spray(pos_abs: tuple[float, float], r: float) -> tuple[int, int]:
    x1, y1 = pos_abs
    x2 = random.uniform(x1-r, x1+r)
    y2 = random.uniform(y1-r, y1+r)
    return tuple([round(i) for i in (x2, y2)])

# rotate a vector by angle degrees
def rotate_vec(vec: np.ndarray, deg: float) -> np.ndarray:
    theta = np.deg2rad(deg)
    rot_matrix = np.array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
    return np.dot(rot_matrix, vec)

def unit_vector(vec: np.ndarray) -> np.ndarray:
    return vec / dist(vec, (0, 0))

def arc_spread(cast_dir: tuple[float,float], spread_deg: float=10, radius_spread: tuple[float, float] = [.95, 1.05]):
    """
        Given an x,y vec (target), generate a new target that is the same vector but rotated by +/- spread_deg/2
    """
    cast_dir = np.array(cast_dir)
    length = dist(cast_dir, (0, 0))
    adj = (radius_spread[1] - radius_spread[0])*random.random() + radius_spread[0]
    rot = spread_deg*(random.random() - .5)
    return rotate_vec(unit_vector(cast_dir)*(length+adj), rot)

def lerp(a: float, b: float, f:float) -> float:
    return a + f * (b - a)