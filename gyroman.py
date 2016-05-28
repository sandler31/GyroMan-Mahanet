#!/usr/bin/python

# from gyromon import GyroMon
from usermon import UserMon
# from serialsend import SerialSend
from webserver import WebServer
import cherrypy


def main():
    print(open("banner").read())
    print()

    gyro = None #GyroMon()
    user = UserMon()
    # serial_send = SerialSend(user, gyro)
    # gyro.start()
    user.start()
    # serial_send.start()

    #raw_input("Press any key to start sending real data\n")

    #serial_send.start_real()
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.quickstart(WebServer(user, gyro))

if __name__ == '__main__':
    main()
