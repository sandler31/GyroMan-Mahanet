#!/usr/bin/python

import time
import serial
import threading


class SerialSend(threading.Thread):
    serial_port = None
    baudrate = None
    timeout = None
    gyro_mon = None
    user_mon = None
    send_init_data = False
    running = False
    port = None
    polltime = None  # ms

    # Constants
    DATA_FORMAT = "X{0}Y{1}R{2}T{3}#\n"
    INIT_VALUES = (66, 66, 66, 30)
    USER_CONVERSION_RATE = (0.5, 0.5, 0.5)

    def __init__(self, user_mon, gyro_mon,
                 serial_port="/dev/ttyAMA0", baudrate=115200,
                 timeout=1, polltime=20):
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.timeout = timeout
        self.polltime = float(polltime)

        # Init thread
        threading.Thread.__init__(self)
        self.daemon = True
        self.port = serial.Serial(self.serial_port, baudrate=self.baudrate,
                                  timeout=self.timeout)

        self.gyro_mon = gyro_mon
        self.user_mon = user_mon

    def calc_gyro_percent(self):
        x, y = self.gyro_mon.get_current_vals()
        return int(((x + 90) / 180) * 100), int(((y + 90) / 180) * 100)

    def calc_user_percent(self):
        x, y, rotation, throttle = self.user_mon.get_current_vals()

        # Vector multiplication!
        # INIT_VALUES + INIT_VALUES * user_values * CONVERSION_RATE
        x, y, rotation = [init + user * init * conversion for
                          init, user, conversion in
                          zip(self.INIT_VALUES,
                              (x, y, rotation),
                              self.USER_CONVERSION_RATE)]

        # x = self.INIT_VALUES[0] + (self.INIT_VALUES[0] * x) / 2
        # y = self.INIT_VALUES[1] + (self.INIT_VALUES[1] * y) / 2
        # rotation = self.INIT_VALUES[2] + (self.INIT_VALUES[2] * rotation) / 2
        return x, y, rotation, throttle

    def get_data(self):
        x, y = self.calc_gyro_percent()
        user_x, user_y, rotation, throttle = self.calc_user_percent()
        x = user_x if user_x != self.INIT_VALUES[0] else x
        y = user_y if user_y != self.INIT_VALUES[1] else y
        return x, y, rotation, throttle

    def run(self):
        self.send_init_data = True
        self.running = True

        while self.send_init_data and self.running:
            d = self.DATA_FORMAT.format(*self.INIT_VALUES)
            self.port.write(d)
            time.sleep(self.polltime / 1000)

        while self.running:
            x, y, rotation, throttle = self.get_data()
            self.port.write(self.DATA_FORMAT.format(x, y, rotation, throttle))
            time.sleep(self.polltime / 1000)

    def start_real(self):
        self.send_init_data = False

    def cancel(self):
        self.running = False
