from mouse import get_position
from mouse._winmouse import move_to
import random
import math
import time


def move(x, y, absolute=True, duration=0, randomize = 0):
    """
    Moves the mouse. If `absolute`, to position (x, y), otherwise move relative
    to the current position. If `duration` is non-zero, animates the movement.
    """
    if randomize > 0:
        x = int(x) + random.randrange(-randomize, +randomize)
        y = int(y) + random.randrange(-randomize, +randomize)
    else:
        x = int(x)
        y = int(y)

    # Requires an extra system call on Linux, but `move_relative` is measured
    # in millimiters so we would lose precision.
    position_x, position_y = get_position()

    if not absolute:
        x = position_x + x
        y = position_y + y

    if duration:
        start_x = position_x
        start_y = position_y
        dx = x - start_x
        dy = y - start_y

        if dx == 0 and dy == 0:
            time.sleep(duration)
        else:
            # make sure we do not animate the mouse too fast
            # setting a max of 0.20 ms per pixel
            dist = math.dist((dx, dy), (0, 0))
            ms_per_pixel = (duration * 1000) / dist
            if ms_per_pixel < 0.20:
                duration = ((dist * 0.20) / 1000)

            # 125 +- 0.04% movements per second. Thats the Hz of a normal usb mouse
            steps = max(1.0, float(int(duration * 125.0 * random.uniform(0.96, 1.04)))) + 1
            uniform_delta_x = dx / steps
            uniform_delta_y = dy / steps
            dx_i = dy_i = i = 0
            moving = True
            while moving:
                i += 1
                # use exponential function to mimic user movment
                f = max(0.1, ((-(2*i/steps-0.9)**2 + 1.05) * 2.0))
                to_travel_x = f * uniform_delta_x
                to_travel_y = f * uniform_delta_y
                dx_i += to_travel_x + random.uniform(-1, 1)
                dy_i += to_travel_y + random.uniform(-1, 1)
                if abs(dx_i) >= (abs(dx) - 4) and abs(dy_i) >= (abs(dy) - 4):
                    dx_i = dx
                    dy_i = dy
                    moving = False
                move(int(start_x + dx_i), int(start_y + dy_i))
                time.sleep(duration/steps)
    else:
        move_to(x, y)
