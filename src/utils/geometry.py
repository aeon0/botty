import random
import numpy as np
from math import cos, sin, dist, pi


def rotate_vec(vec: np.ndarray, deg: float) -> np.ndarray:
    theta = np.deg2rad(deg)
    rot_matrix = np.array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
    return np.dot(rot_matrix, vec)

def unit_vector(vec: np.ndarray) -> np.ndarray:
    return vec / dist(vec, (0, 0))

# random point along arc length of a circle
def point_on_circle(radius: float, center: np.ndarray = (0, 0), ) -> np.ndarray:
    theta = random.uniform(0, 2 * pi)
    return center + radius * np.array([cos(theta), sin(theta)])

# convert angle in degrees to radians
def deg_to_rad(deg: float) -> float:
    return deg * pi / 180


def arc_spread(cast_dir: tuple[float,float], spread_deg: float=10, radius_spread: tuple[float, float] = [.95, 1.05]) -> np.ndarray:
    """
        Given an x,y vec (target), generate a new target that is the same vector but rotated by +/- spread_deg/2
    """
    cast_dir = np.array(cast_dir)
    length = dist(cast_dir, (0, 0))
    adj = (radius_spread[1] - radius_spread[0])*random.random() + radius_spread[0]
    rot = spread_deg*(random.random() - .5)
    return rotate_vec(unit_vector(cast_dir)*(length+adj), rot)

# return random point in circle centered at x,y with radius r
def random_point_in_circle(pos: tuple[float, float], r: float) -> tuple[int, int]:
    x, y = pos
    theta = random.random()*2*pi
    return round(x + r*cos(theta)), round(y + r*sin(theta))