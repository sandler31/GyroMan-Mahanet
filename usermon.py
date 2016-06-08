#!/usr/bin/python

import time
import threading
import Queue

"""
This class receives user input to update the drones' x-axis, y-axis, rotation-axis and throttle.
This class uses an actor model for controlling axis changes
On an axis change, the change is inserted 'action_time_units' into a the appropriate queue.
The queues are sampled every 'time_unit' milliseconds, and each axis is updated accordingly.
This means that each 'action' is run for 'time_unit' *'action_time_units' milliseconds, and that the class is thread-safe.
The defualt is 250ms for each action (10 * 25)
"""


class UserMon(threading.Thread):
    x = None
    y = None
    running = False
    throttle = None  # percent
    rotation = None  # percent
    time_unit = None
    direction_queues = None
    action_time_units = None

    # Consts
    ZERO_THROTTLE = 0
    THROTTLE_CHANGE_BIG = 5
    THROTTLE_CHANGE_SMALL = 1
    DIRECTION_NONE = 0
    DIRECTION_POSITIVE = 1
    DIRECTION_NEGATIVE = -1

    def __init__(self, time_unit=1): #, action_time_units=3):
        # Init thread
        threading.Thread.__init__(self)
        self.daemon = True

        self.x = 0
        self.y = 0
        self.throttle = self.ZERO_THROTTLE
        self.rotation = 0


    def rotate_left(self):
        self.rotation = self.DIRECTION_NEGATIVE

    def rotate_right(self):
        self.rotation = self.DIRECTION_POSITIVE

    def reset_rotate(self):
        self.rotation = self.DIRECTION_NONE

    def move_left(self):
        self.x = self.DIRECTION_NEGATIVE

    def move_right(self):
        self.x = self.DIRECTION_POSITIVE

    def reset_x(self):
        self.x = self.DIRECTION_NONE

    def move_back(self):
        self.y = self.DIRECTION_NEGATIVE

    def move_forward(self):
        self.y = self.DIRECTION_POSITIVE

    def reset_y(self):
        self.y = self.DIRECTION_NONE

    def set_throttle(self, val):
        self.throttle = max(0, min(self.throttle + val, 100))

    def increase_throttle(self):
        self.set_throttle(self.THROTTLE_CHANGE_BIG)

    def decrease_throttle(self):
        self.set_throttle(self.THROTTLE_CHANGE_BIG * -1)

    def slight_increase_throttle(self):
        self.set_throttle(self.THROTTLE_CHANGE_SMALL)

    def slight_decrease_throttle(self):
        self.set_throttle(self.THROTTLE_CHANGE_SMALL * -1)
        
    def reset_throttle(self):
        self.throttle = self.ZERO_THROTTLE

    def get_current_vals(self):
        return self.x, self.y, self.rotation, self.throttle
