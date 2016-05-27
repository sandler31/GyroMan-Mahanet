#!/usr/bin/python

import cherrypy

class WebServer(object):
    gyro_mon = None

    def __init__(self, gyro_mon):
        self.gyro_mon = gyro_mon

    @cherrypy.expose
    def index(self):
        x, y = self.gyro_mon.get_current_vals()
        return "{0:.2f} {1:.2f}".format(x, y)