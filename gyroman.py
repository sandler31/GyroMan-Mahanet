#!/usr/bin/python

from gyromon import GyroMon
from serialsend import SerialSend
from webserver import WebServer

def main():
    print(open("banner").read())
    print()

    gyro = GyroMon()
    serial_send = SerialSend(gyro)
    gyro.start()
    serial_send.start()

    raw_input("Press any key to start sending real data\n")

    serial_send.start_real()
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.quickstart(WebServer(gyro))

if __name__ == '__main__':
    main()