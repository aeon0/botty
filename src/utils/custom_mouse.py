# Mostly copied from: https://github.com/patrikoss/pyclick
import mouse as _mouse
from mouse import _winmouse
import pytweening
import numpy as np
import random
import math
import time
from typing import Union, Tuple
import screen
from config import Config
from utils.misc import is_in_roi
from logger import Logger
import template_finder

def isNumeric(val):
    return isinstance(val, (float, int, np.int32, np.int64, np.float32, np.float64))

def isListOfPoints(l):
    if not isinstance(l, list):
        return False
    try:
        isPoint = lambda p: ((len(p) == 2) and isNumeric(p[0]) and isNumeric(p[1]))
        return all(map(isPoint, l))
    except (KeyError, TypeError) as e:
        return False

class BezierCurve():
    @staticmethod
    def binomial(n, k):
        """Returns the binomial coefficient "n choose k" """
        return math.factorial(n) / float(math.factorial(k) * math.factorial(n - k))

    @staticmethod
    def bernsteinPolynomialPoint(x, i, n):
        """Calculate the i-th component of a bernstein polynomial of degree n"""
        return BezierCurve.binomial(n, i) * (x ** i) * ((1 - x) ** (n - i))

    @staticmethod
    def bernsteinPolynomial(points):
        """
        Given list of control points, returns a function, which given a point [0,1] returns
        a point in the bezier curve described by these points
        """
        def bern(t):
            n = len(points) - 1
            x = y = 0
            for i, point in enumerate(points):
                bern = BezierCurve.bernsteinPolynomialPoint(t, i, n)
                x += point[0] * bern
                y += point[1] * bern
            return x, y
        return bern

    @staticmethod
    def curvePoints(n, points):
        """
        Given list of control points, returns n points in the bezier curve,
        described by these points
        """
        curvePoints = []
        bernstein_polynomial = BezierCurve.bernsteinPolynomial(points)
        for i in range(n):
            t = i / (n - 1)
            curvePoints += bernstein_polynomial(t),
        return curvePoints

class HumanCurve():
    """
    Generates a human-like mouse curve starting at given source point,
    and finishing in a given destination point
    """

    def __init__(self, fromPoint, toPoint, **kwargs):
        self.fromPoint = fromPoint
        self.toPoint = toPoint
        self.points = self.generateCurve(**kwargs)

    def generateCurve(self, **kwargs):
        """
        Generates a curve according to the parameters specified below.
        You can override any of the below parameters. If no parameter is
        passed, the default value is used.
        """
        offsetBoundaryX = kwargs.get("offsetBoundaryX", 100)
        offsetBoundaryY = kwargs.get("offsetBoundaryY", 100)
        leftBoundary = kwargs.get("leftBoundary", min(self.fromPoint[0], self.toPoint[0])) - offsetBoundaryX
        rightBoundary = kwargs.get("rightBoundary", max(self.fromPoint[0], self.toPoint[0])) + offsetBoundaryX
        downBoundary = kwargs.get("downBoundary", min(self.fromPoint[1], self.toPoint[1])) - offsetBoundaryY
        upBoundary = kwargs.get("upBoundary", max(self.fromPoint[1], self.toPoint[1])) + offsetBoundaryY
        knotsCount = kwargs.get("knotsCount", 2)
        distortionMean = kwargs.get("distortionMean", 1)
        distortionStdev = kwargs.get("distortionStdev", 1)
        distortionFrequency = kwargs.get("distortionFrequency", 0.4)
        tween = kwargs.get("tweening", pytweening.easeOutQuad)
        targetPoints = kwargs.get("targetPoints", 10)

        internalKnots = self.generateInternalKnots(leftBoundary,rightBoundary, \
            downBoundary, upBoundary, knotsCount)
        points = self.generatePoints(internalKnots)
        points = self.distortPoints(points, distortionMean, distortionStdev, distortionFrequency)
        points = self.tweenPoints(points, tween, targetPoints)
        return points

    def generateInternalKnots(self, \
        leftBoundary, rightBoundary, \
        downBoundary, upBoundary,\
        knotsCount):
        """
        Generates the internal knots used during generation of bezier curvePoints
        or any interpolation function. The points are taken at random from
        a surface delimited by given boundaries.
        Exactly knotsCount internal knots are randomly generated.
        """
        if not (isNumeric(leftBoundary) and isNumeric(rightBoundary) and
            isNumeric(downBoundary) and isNumeric(upBoundary)):
            raise ValueError("Boundaries must be numeric")
        if not isinstance(knotsCount, int) or knotsCount < 0:
            raise ValueError("knotsCount must be non-negative integer")
        if leftBoundary > rightBoundary:
            raise ValueError("leftBoundary must be less than or equal to rightBoundary")
        if downBoundary > upBoundary:
            raise ValueError("downBoundary must be less than or equal to upBoundary")

        knotsX = np.random.choice(range(leftBoundary, rightBoundary), size=knotsCount)
        knotsY = np.random.choice(range(downBoundary, upBoundary), size=knotsCount)
        knots = list(zip(knotsX, knotsY))
        return knots

    def generatePoints(self, knots):
        """
        Generates bezier curve points on a curve, according to the internal
        knots passed as parameter.
        """
        if not isListOfPoints(knots):
            raise ValueError("knots must be valid list of points")

        midPtsCnt = max( \
            abs(self.fromPoint[0] - self.toPoint[0]), \
            abs(self.fromPoint[1] - self.toPoint[1]), \
            2)
        knots = [self.fromPoint] + knots + [self.toPoint]
        return BezierCurve.curvePoints(midPtsCnt, knots)

    def distortPoints(self, points, distortionMean, distortionStdev, distortionFrequency):
        """
        Distorts the curve described by (x,y) points, so that the curve is
        not ideally smooth.
        Distortion happens by randomly, according to normal distribution,
        adding an offset to some of the points.
        """
        if not(isNumeric(distortionMean) and isNumeric(distortionStdev) and \
               isNumeric(distortionFrequency)):
            raise ValueError("Distortions must be numeric")
        if not isListOfPoints(points):
            raise ValueError("points must be valid list of points")
        if not (0 <= distortionFrequency <= 1):
            raise ValueError("distortionFrequency must be in range [0,1]")

        distorted = []
        for i in range(1, len(points)-1):
            x,y = points[i]
            delta = np.random.normal(distortionMean, distortionStdev) if \
                random.random() < distortionFrequency else 0
            distorted += (x,y+delta),
        distorted = [points[0]] + distorted + [points[-1]]
        return distorted

    def tweenPoints(self, points, tween, targetPoints):
        """
        Chooses a number of points(targetPoints) from the list(points)
        according to tweening function(tween).
        This function in fact controls the velocity of mouse movement
        """
        if not isListOfPoints(points):
            raise ValueError("points must be valid list of points")
        if not isinstance(targetPoints, int) or targetPoints < 2:
            raise ValueError("targetPoints must be an integer greater or equal to 2")

        # tween is a function that takes a float 0..1 and returns a float 0..1
        res = []
        for i in range(targetPoints):
            index = int(tween(float(i)/(targetPoints-1)) * (len(points)-1))
            res += points[index],
        return res

class mouse:
    @staticmethod
    def sleep(duration, get_now=time.perf_counter):
        time.sleep(duration)
        # now = get_now()
        # end = now + duration
        # while now < end:
        #     now = get_now()

    @staticmethod
    def _move_to(x, y, absolute=True, duration=0):
        """
        Moves the mouse. If `absolute`, to position (x, y), otherwise move relative
        to the current position. If `duration` is non-zero, animates the movement.
        """
        x = int(x)
        y = int(y)

        # Requires an extra system call on Linux, but `move_relative` is measured
        # in millimiters so we would lose precision.
        position_x, position_y = _mouse.get_position()

        if not absolute:
            x = position_x + x
            y = position_y + y

        if duration:
            start_x = position_x
            start_y = position_y
            dx = x - start_x
            dy = y - start_y

            if dx == 0 and dy == 0:
                mouse.sleep(duration)
            else:
                # 120 movements per second.
                # Round and keep float to ensure float division in Python 2
                steps = max(1.0, float(int(duration * 120.0)))
                for i in range(int(steps)+1):
                    mouse.move(start_x + dx*i/steps, start_y + dy*i/steps)
                    mouse.sleep(duration/steps)
        else:
            _winmouse.move_to(x, y)

    def move(x, y, absolute: bool = True, randomize: Union[int, Tuple[int, int]] = 5, delay_factor: Tuple[float, float] = [0.9, 1.1]):
        from_point = _mouse.get_position()
        dist = math.dist((x, y), from_point)
        offsetBoundaryX = max(10, int(0.08 * dist))
        offsetBoundaryY = max(10, int(0.08 * dist))
        targetPoints = min(6, max(3, int(0.004 * dist)))
        if not absolute:
            x = from_point[0] + x
            y = from_point[1] + y

        if type(randomize) is int:
            randomize = int(randomize)
            if randomize > 0:
                x = int(x) + random.randrange(-randomize, +randomize)
                y = int(y) + random.randrange(-randomize, +randomize)
        else:
            randomize = (int(randomize[0]), int(randomize[1]))
            if randomize[1] > 0 and randomize[0] > 0:
                x = int(x) + random.randrange(-randomize[0], +randomize[0])
                y = int(y) + random.randrange(-randomize[1], +randomize[1])


        human_curve = HumanCurve(from_point, (x, y), offsetBoundaryX=offsetBoundaryX, offsetBoundaryY=offsetBoundaryY, targetPoints=targetPoints)

        duration = min(0.5, max(0.05, dist * 0.0004) * random.uniform(delay_factor[0], delay_factor[1]))
        delta = duration / len(human_curve.points)

        for point in human_curve.points:
            _mouse.move(point[0], point[1], duration=delta)

    @staticmethod
    def _is_clicking_safe():
        # Because of reports that botty lost equiped items, let's check if the inventory is open, and if it is, restrict the mouse move
        mouse_pos = screen.convert_monitor_to_screen(_mouse.get_position())
        is_inventory_open = template_finder.search(
            "INVENTORY_GOLD_BTN",
            screen.grab(),
            threshold=0.8,
            roi=Config().ui_roi["gold_btn"],
            use_grayscale=True
        ).valid
        if is_inventory_open:
            is_in_equipped_area = is_in_roi(Config().ui_roi["equipped_inventory_area"], mouse_pos)
            is_in_restricted_inventory_area = is_in_roi(Config().ui_roi["restricted_inventory_area"], mouse_pos)
            if is_in_restricted_inventory_area or is_in_equipped_area:
                Logger.error("Mouse wants to click in equipped area. Cancel action.")
                return False
        return True

    @staticmethod
    def click(button):
        if button != "left" or mouse._is_clicking_safe():
            _mouse.click(button)

    @staticmethod
    def press(button):
        if button != "left" or mouse._is_clicking_safe():
            _mouse.press(button)

    @staticmethod
    def release(button):
        _mouse.release(button)

    @staticmethod
    def get_position():
        return _mouse.get_position()

    @staticmethod
    def wheel(delta):
        _mouse.wheel(delta)


if __name__ == "__main__":
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    keyboard.wait("f11")
    screen.find_and_set_window_position()
    move_to_ok = screen.convert_screen_to_monitor((400, 420))
    move_to_bad_equiped = screen.convert_screen_to_monitor((900, 170))
    move_to_bad_inventory = screen.convert_screen_to_monitor((1200, 400))
    mouse.move(*move_to_ok)
    mouse.click("left")
    time.sleep(1)
    mouse.move(*move_to_bad_equiped)
    mouse.click("left")
    time.sleep(1)
    mouse.move(*move_to_bad_inventory)
    mouse.click("left")
