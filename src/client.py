# Note this file runs on jetbot
import socket
import json
from jetbot import Robot

robot = Robot()

UDP_IP = "192.168.137.3"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    data = json.loads(data.decode())
    print("received message: %s" % data)
    leftspeed = data.get("left")/1000
    rightspeed = data.get("right")/1000
    # 0.12
    lower_bound = 0.12
    # 0.3
    upper_bound = 0.3
    
    if leftspeed < 0:
        leftspeed = leftspeed * (upper_bound-lower_bound) - lower_bound
    elif leftspeed > 0:
        leftspeed = leftspeed* (upper_bound-lower_bound) + lower_bound
    else:
        leftspeed = 0
    if rightspeed < 0:
        rightspeed = rightspeed * (upper_bound-lower_bound) - lower_bound
    elif rightspeed > 0:
        rightspeed = rightspeed * (upper_bound-lower_bound) + lower_bound
    else:
        rightspeed = 0

        
    robot.set_motors(leftspeed, rightspeed)

#     print(type(data))
