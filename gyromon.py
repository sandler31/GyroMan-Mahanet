#!/usr/bin/python

import math
import time
import smbus
import threading
import collections


class GyroMon(threading.Thread):
    bus = None
    address = None
    running = False
    average_array_x = None
    average_array_y = None
    polltime = None  # ms

    # Consts
    DIVISOR = 10
    POWER_MGMT = 0x6b

    def __init__(self, polltime=20):
        self.polltime = float(polltime)

        # Init thread
        threading.Thread.__init__(self)
        self.daemon = True

        # MPU Init        
        self.bus = smbus.SMBus(1)
        self.address = 0x68  # This is the address value read via the i2cdetect command

        # Now wake the 6050 up as it starts in sleep mode
        self.bus.write_byte_data(self.address, self.POWER_MGMT, 0)

        # Data arrays init
        self.average_array_x = collections.deque(maxlen=self.DIVISOR)
        self.average_array_y = collections.deque(maxlen=self.DIVISOR)
        self.average_array_x.append(0)
        self.average_array_y.append(0)

    def read_byte(self, adr):
        return self.bus.read_byte_data(self.address, adr)

    def read_word(self, adr):
        high = self.bus.read_byte_data(self.address, adr)
        low = self.bus.read_byte_data(self.address, adr + 1)
        val = (high << 8) + low
        return val

    def read_word_2c(self, adr):
        val = self.read_word(adr)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val

    def dist(self, a, b):
        return math.sqrt((a * a) + (b * b))

    def get_y_rotation(self, x, y, z):
        radians = math.atan2(x, self.dist(y, z))
        return -math.degrees(radians)

    def get_x_rotation(self, x, y, z):
        radians = math.atan2(y, self.dist(x, z))
        return math.degrees(radians)

    def avg(self, nums):
        return float(sum(nums)) / len(nums)

    def update_values_mpu(self):
        # never used?
        # gyro_xout = self.read_word_2c(0x43)
        # gyro_yout = self.read_word_2c(0x45)
        # gyro_zout = self.read_word_2c(0x47)

        accel_xout = self.read_word_2c(0x3b)
        accel_yout = self.read_word_2c(0x3d)
        accel_zout = self.read_word_2c(0x3f)

        accel_xout_scaled = accel_xout / 16384.0
        accel_yout_scaled = accel_yout / 16384.0
        accel_zout_scaled = accel_zout / 16384.0

        x, y = self.get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled),\
            self.get_y_rotation(accel_xout_scaled,
                                accel_yout_scaled, accel_zout_scaled)

        # Push to array
        self.average_array_x.append(x)
        self.average_array_y.append(y)

        self.x = self.avg(self.average_array_x)
        self.y = self.avg(self.average_array_y)

    def run(self):
        self.running = True

        while self.running:
            time.sleep((self.polltime / self.DIVISOR) / 1000)
            self.update_values_mpu()

    def cancel(self):
        self.running = False

    def get_current_vals(self):
        return self.x, self.y
