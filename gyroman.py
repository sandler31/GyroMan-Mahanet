#!/usr/bin/python

# from gyromon import GyroMon
from usermon import UserMon
# from serialsend import SerialSend
from webserver import WebServer
import cherrypy
import os
import os.path


def main():
    print(open("banner").read())
    print()

    gyro = None  # GyroMon()
    user = UserMon()
    # serial_send = SerialSend(user, gyro)
    # gyro.start()
    user.start()
    # serial_send.start()

    #raw_input("Press any key to start sending real data\n")

    # serial_send.start_real()    
    dirname = os.getcwd()    
    cherrypy.quickstart(WebServer(user, gyro), '/', {
        'global':
            {
                'server.socket_host': '0.0.0.0',
                'server.socket_port': 8080
            },
        '/remote.html':
            {
                'tools.staticfile.on': True,
                'tools.staticfile.filename':
                    os.path.join(dirname, 'remote/remote.html')
            }
    })

if __name__ == '__main__':
    main()
