#!/usr/bin/python

import time
import threading


class UserMon():
    throttle = None  # percent
    rotation = None  # percent
    rotation_lock = None
    rotation_change = None
    time_unit = None

    # Consts
    ZERO_THROTTLE = 0
    ZERO_ROTATION = 50  # zero == left, 100 == right

    def __init__(self, time_unit=2, rotation_percent=50):
        self.throttle = self.ZERO_THROTTLE
        self.rotation = self.ZERO_ROTATION
        self.rotation_lock = threading.Lock()
        self.rotation_change = (self.ZERO_ROTATION * rotation_percent) / 100
        self.time_unit = float(time_unit) / 1000

  # This one blocks for a while. use it with a new thread.
    def __directional_range(self, start, end):
        if start < end:
            direction = 1
        else:
            direction = -1

        for i in range(start, end, direction):
            time.sleep(self.time_unit)
            yield i
        yield end

    def set_throttle(self, throttle=50):
        if throttle > 100 or throttle < 0:
            raise ValueError("throttle must be between 0-100")

        for i in self.__directional_range(self.throttle, throttle):
            self.throttle = i

    def __cancel_rotation(self):
        for i in self.__directional_range(self.rotation, self.ZERO_ROTATION):
            self.rotation = i

    def __turn(self, rotation):
        for i in self.__directional_range(self.rotation, rotation):
            self.rotation = i
        self.__cancel_rotation()

    def turn_left(self):
        with self.rotation_lock:
            self.__turn(self.ZERO_ROTATION + self.rotation_change)

    def turn_right(self):
        with self.rotation_lock:
            self.__turn(self.ZERO_ROTATION - self.rotation_change)

    def get_current_vals(self):
        return self.throttle, self.rotation
