#!/usr/bin/python

import cherrypy


class WebServer(object):
    gyro_mon = None
    user_mon = None
    serial_send = None

    def __init__(self, user_mon, gyro_mon, serial_send):
        self.gyro_mon = gyro_mon
        self.user_mon = user_mon
        self.serial_send = serial_send

    @cherrypy.expose
    def index(self):
        x, y = self.gyro_mon.get_current_vals()
        return "{0:.2f} {1:.2f}".format(y, x)

    @cherrypy.expose
    def user_stats(self):
        x, y, rotation, throttle = self.user_mon.get_current_vals()
        return "X:{0}<br>Y:{1}<br>Rotation:{2}<br>Throttle:{3}<br>User Control:{4}<br>Camera Mode:{5}".format(x, y, rotation, throttle, self.serial_send.user_control, self.serial_send.camera_mode)

    @cherrypy.expose
    def rotate_left(self):
        self.user_mon.rotate_left()

    @cherrypy.expose
    def rotate_right(self):
        self.user_mon.rotate_right()

    @cherrypy.expose
    def reset_rotate(self):
        self.user_mon.reset_rotate()

    @cherrypy.expose
    def move_left(self):
        self.user_mon.move_left()

    @cherrypy.expose
    def move_right(self):
        self.user_mon.move_right()

    @cherrypy.expose
    def reset_x(self):
        self.user_mon.reset_x()

    @cherrypy.expose
    def move_forward(self):
        self.user_mon.move_forward()

    @cherrypy.expose
    def move_back(self):
        self.user_mon.move_back()

    @cherrypy.expose
    def reset_y(self):
        self.user_mon.reset_y()

    @cherrypy.expose
    def increase_throttle(self):
        self.user_mon.increase_throttle()

    @cherrypy.expose
    def slight_increase_throttle(self):
        self.user_mon.slight_increase_throttle()

    @cherrypy.expose
    def decrease_throttle(self):
        self.user_mon.decrease_throttle()

    @cherrypy.expose
    def slight_decrease_throttle(self):
        self.user_mon.slight_decrease_throttle()

    @cherrypy.expose
    def reset_throttle(self):
        self.user_mon.reset_throttle()

    @cherrypy.expose
    def user_control(self):
        self.serial_send.change_control()

    @cherrypy.expose
    def toggle_camera_mode(self):
        self.serial_send.toggle_camera_mode()
