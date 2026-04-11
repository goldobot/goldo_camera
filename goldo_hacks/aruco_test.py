from picamera2 import Picamera2

import time
import cv2
from cv2 import aruco
import zmq
import struct
import sys
sys.path.append("../")
import math
import select

def crux(x,y):
    cv2.line(frame, (x-5,y), (x+5,y), (255,255,255), 2)
    cv2.line(frame, (x,y-5), (x,y+5), (255,255,255), 2)

CAM_W = 1296
CAM_H =  972

Y_horizon = 4

context = zmq.Context()    
pub_socket = context.socket(zmq.PUB)
pub_socket.bind('tcp://0.0.0.0:3201')


picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(
#    main={"size": (640, 480), "format": "BGR888"}
#    main={"size": (1920, 1080), "format": "BGR888"}
    main={"size": (CAM_W, CAM_H), "format": "RGB888"}
))
picam2.start()

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

iter=0
while True:
    frame = picam2.capture_array()

    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    corners, ids, rejectedImgPoints = detector.detectMarkers(gray)
    frame_markers = aruco.drawDetectedMarkers(frame, corners, ids)

    cv2.line(frame, (0,Y_horizon), (CAM_W,Y_horizon), (0,255,255), 2)
    x=10
    y=10
    cv2.rectangle(frame, (x-5,y-5), (x+5,y+5), (0,255,0), 2)
    x=CAM_W-10
    y=CAM_H-10
    cv2.rectangle(frame, (x-5,y-5), (x+5,y+5), (0,255,0), 2)
    x=10
    y=CAM_H-10
    cv2.rectangle(frame, (x-5,y-5), (x+5,y+5), (0,255,0), 2)
    x=CAM_W-10
    y=10
    cv2.rectangle(frame, (x-5,y-5), (x+5,y+5), (0,255,0), 2)

    for i in range (1,int(CAM_H/80)):
        crux(int(CAM_W/2), i*80)

    if (iter%10==0):
        detected_shapes = []
        for i in range(len(corners)):
            id = int(ids[i])
            c=corners[i]
            my_x = []
            my_y = []
            for j in range(0,4):
                my_x.append(c[0,j,0])
                my_y.append(c[0,j,1])
                #if (id==36) or (id==47):
                #    print ("  {} {}".format(c[0,j,0], c[0,j,1]))
            max_x = int(max(my_x))
            min_x = int(min(my_x))
            max_y = int(max(my_y))
            min_y = int(min(my_y))
            moy_x = int(sum(my_x)/len(my_x))
            moy_y = int(sum(my_y)/len(my_y))
            detected_shapes.append((id,moy_x,moy_y))
            if (id==36) or (id==47):
                print ("  #{} : <{},{}>".format(id,moy_x,moy_y))
        print("----------------")
        print()
    iter=iter+1

    #cv2.imshow("test", frame)
    cv2.imshow("test", frame_markers)

    if cv2.waitKey(1) == 27:
        break

    retval, buffer = cv2.imencode('.jpg', frame_markers)
    pub_socket.send(buffer)


