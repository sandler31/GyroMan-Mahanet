#!/usr/bin/python

import cherrypy


class WebServer(object):
    gyro_mon = None
    user_mon = None

    def __init__(self, user_mon, gyro_mon):
        self.gyro_mon = gyro_mon
        self.user_mon = user_mon

    @cherrypy.expose
    def index(self):
        x, y = self.gyro_mon.get_current_vals()
        return "{0:.2f} {1:.2f}".format(x, y)

    @cherrypy.expose
    def user_stats(self):
        x, y, rotation, throttle = self.user_mon.get_current_vals()
        return "{0} {1} {2} {3}".format(x, y, rotation, throttle)

    @cherrypy.expose
    def rotate_left(self):
        self.user_mon.rotate_left()

    @cherrypy.expose
    def rotate_right(self):
        self.user_mon.rotate_right()

    @cherrypy.expose
    def move_left(self):
        self.user_mon.move_left()

    @cherrypy.expose
    def move_right(self):
        self.user_mon.move_right()

    @cherrypy.expose
    def move_forward(self):
        self.user_mon.move_forward()

    @cherrypy.expose
    def move_back(self):
        self.user_mon.move_back()

    @cherrypy.expose
    def increase_throttle(self):
        self.user_mon.increase_throttle()

    @cherrypy.expose
    def decrease_throttle(self):
        self.user_mon.decrease_throttle()
