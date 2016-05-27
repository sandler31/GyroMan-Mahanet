#!/usr/bin/python

import time
import serial
import threading


class SerialSend(threading.Thread):
    serial_port = None
    baudrate = None
    timeout = None
    gyro_mon = None
    send_init_data = False
    running = False
    port = None
    polltime = None  # ms

    # Constants
    DATA_FORMAT = "${0}|{1}#\n"
    MID_VALUES = (66, 66)

    def __init__(self, gyro_mon, serial_port="/dev/ttyAMA0", baudrate=115200,
                 timeout=1, polltime=20):
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.timeout = timeout
        self.polltime = polltime

        # Init thread
        threading.Thread.__init__(self)
        self.daemon = True
        self.port = serial.Serial(self.serial_port, baudrate=self.baudrate,
                                  timeout=self.timeout)

        self.gyro_mon = gyro_mon

    def calc_percent(self):
        x, y = self.gyro_mon.get_current_vals()
        # print x, y

        return int(((x + 90) / 180) * 100), int(((y + 90) / 180) * 100)

    def run(self):
        self.send_init_data = True
        self.running = True

        while self.send_init_data and self.running:
            d = self.DATA_FORMAT.format(*self.MID_VALUES)
            # print d
            self.port.write(d)
            time.sleep(self.polltime / 1000)

        while self.running:
            x, y = self.calc_percent()
            # print x, y
            self.port.write(self.DATA_FORMAT.format(x, y))
            time.sleep(self.polltime / 1000)

    def start_real(self):
        self.send_init_data = False

    def cancel(self):
        self.running = False
