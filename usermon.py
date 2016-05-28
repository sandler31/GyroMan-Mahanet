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
    throttle_lock = None
    direction_queues = None
    action_time_units = None

    # Consts
    ZERO_THROTTLE = 0
    DIRECTION_POSITIVE = 1
    DIRECTION_NEGATIVE = -1
    THROTTLE_CHANGE = 10

    def __init__(self, time_unit=100, action_time_units=25):
        # Init thread
        threading.Thread.__init__(self)
        self.daemon = True

        self.x = 0
        self.y = 0
        self.throttle = self.ZERO_THROTTLE
        self.rotation = 0
        self.action_time_units = action_time_units
        self.throttle_lock = threading.Lock()

        self.time_unit = float(time_unit) / 1000
        self.direction_queues = {'x': Queue.Queue(),
                                 'y': Queue.Queue(),
                                 'rotation': Queue.Queue()}

    def rotate_left(self):
        for i in range(self.action_time_units):
            self.direction_queues['rotation'].put(self.DIRECTION_NEGATIVE)

    def rotate_right(self):
        for i in range(self.action_time_units):
            self.direction_queues['rotation'].put(self.DIRECTION_POSITIVE)

    def move_left(self):
        for i in range(self.action_time_units):
            self.direction_queues['x'].put(self.DIRECTION_NEGATIVE)

    def move_right(self):
        for i in range(self.action_time_units):
            self.direction_queues['x'].put(self.DIRECTION_POSITIVE)

    def move_back(self):
        for i in range(self.action_time_units):
            self.direction_queues['y'].put(self.DIRECTION_NEGATIVE)

    def move_forward(self):
        for i in range(self.action_time_units):
            self.direction_queues['y'].put(self.DIRECTION_POSITIVE)

    def increase_throttle(self):
        with self.throttle_lock:
            if self.throttle < 100:
                self.throttle += self.THROTTLE_CHANGE

    def decrease_throttle(self):
        with self.throttle_lock:
            if self.throttle > 0:
                self.throttle -= self.THROTTLE_CHANGE

    def update_values(self):
        for direction_queue in self.direction_queues.values():
            if direction_queue.empty():
                direction_queue.put(0)

        self.x = self.direction_queues['x'].get()
        self.y = self.direction_queues['y'].get()
        self.rotation = self.direction_queues['rotation'].get()

    def run(self):
        self.running = True
        while self.running:
            time.sleep(self.time_unit)
            self.update_values()

    def cancel(self):
        self.running = False

    def get_current_vals(self):
        return self.x, self.y, self.rotation, self.throttle
