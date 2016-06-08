#!/usr/bin/python

import sys
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
    user_control = None
    camera_mode = None

    # Constants
    DATA_FORMAT = "X{0}Y{1}R{2}T{3}#\n"
    INIT_VALUES = (50, 50, 50, 0)
    #x y rotation throttle
    CORRECTION_VALUES = (3, -3.5, 0, 0)
    USER_CONVERSION_RATE = (0.75, 0.75, 0.75)
    # GYRO_CONVERSION_RATE = (10, 15)
    GYRO_CONVERSION_RATE = (10, 15, 10)
    


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
        self.user_control = True
        self.camera_mode = False

    def limit(self, val):
        return max(0, min(100, val))

    def calc_gyro_percent(self):
        # rotation, y = self.gyro_mon.get_current_vals()
        x, y = self.gyro_mon.get_current_vals()
        return int((x / -180)  * 100) * self.GYRO_CONVERSION_RATE[0] + 50 + self.CORRECTION_VALUES[0], \
               int((y /  180)  * 100) * self.GYRO_CONVERSION_RATE[1] + 50 + self.CORRECTION_VALUES[1],  \
               int((x / -180)  * 100) * self.GYRO_CONVERSION_RATE[2] + 50 + self.CORRECTION_VALUES[2] # rotation

    def calc_user_percent(self):
        x, y, rotation, throttle = self.user_mon.get_current_vals()

        # Vector multiplication!
        # INIT_VALUES + INIT_VALUES * user_values * CONVERSION_RATE
        x, y, rotation = [corr + init + user * init * conversion for
                          corr, init, user, conversion in
                          zip(self.CORRECTION_VALUES,
                              self.INIT_VALUES,
                              (x, y, rotation),
                              self.USER_CONVERSION_RATE)]
        return x, y, rotation, throttle

    def get_data(self):
        #x, rotation = None
        x, y, rotation = self.calc_gyro_percent()
        # rotation, y = self.calc_gyro_percent()
        user_x, user_y, user_rotation, throttle = self.calc_user_percent()
        # x, user_y, user_rotation, throttle = self.calc_user_percent()
        if self.camera_mode:
            #rotation = gyro_rotation
            x = user_x
        else:
            rotation = user_rotation
            #x = gyro_x
        if self.user_control:
            # y, rotation = user_y, user_rotation
            x, y, rotation = user_x, user_y, user_rotation
        return self.limit(x), self.limit(y), self.limit(rotation), self.limit(throttle)

    def change_control(self):
        self.user_control = not self.user_control

    def toggle_camera_mode(self):
        self.camera_mode = not self.camera_mode
        
    def run(self):
        self.send_init_data = True
        self.running = True

        while self.send_init_data and self.running:
            d = self.DATA_FORMAT.format(*self.INIT_VALUES)
            x, y, rotation, throttle = self.get_data()

            sys.stdout.write("Current values: %d %d %d %d \r" % (x, y, rotation, throttle))
            sys.stdout.flush()
            # print x, y, rotation, throttle

            self.port.write(d)
            time.sleep(self.polltime / 1000)

        print '--------------------------------'
        print '|                              |'
        print '|                              |'
        print '|            start             |'
        print '|                              |'
        print '|                              |'
        print '--------------------------------'
        while self.running:
            x, y, rotation, throttle = self.get_data()

            sys.stdout.write("Current values: %d %d %d %d %d\r" % (x, y, rotation, throttle, self.user_control))
            sys.stdout.flush()
            # print x, y, rotation, throttle

            self.port.write(self.DATA_FORMAT.format(x, y, rotation, throttle))
            time.sleep(self.polltime / 1000)

    def start_real(self):
        self.send_init_data = False

    def cancel(self):
        self.running = False
