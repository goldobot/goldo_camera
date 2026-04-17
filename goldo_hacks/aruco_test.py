from picamera2 import Picamera2

import time
import zmq
import struct
import sys
sys.path.append("../")
import math
import select
import os

import numpy as np
from scipy.spatial import Delaunay
import cv2
from cv2 import aruco

# ================================
# 1. SAMPLE DATA (unchanged)
# ================================
P_exp = [
    [(   14,   775,   100,  +400), #
     (   97,   817,   100,  +300), #
     ( 1123,   829,   100,  -300), #
     ( 1206,   785,   100,  -400)],#

    [(   31,   646,   200,  +400), #
     (  116,   664,   200,  +300), #
     (  232,   688,   200,  +200), #
     (  985,   693,   200,  -200), #
     ( 1106,   676,   200,  -300), #
     ( 1168,   651,   200,  -400)],#

    [(   67,   519,   300,  +400), #
     (  154,   516,   300,  +300), #
     (  266,   522,   300,  +200), #
     (  422,   523,   300,  +100), #
     (  608,   529,   300,     0), #
     (  797,   531,   300,  -100), #
     (  952,   528,   300,  -200), #
     ( 1070,   527,   300,  -300), #
     ( 1155,   525,   300,  -400)],#

    [(  112,   407,   400,  +400), #
     (  198,   394,   400,  +300), #
     (  308,   386,   400,  +200), #
     (  450,   378,   400,  +100), #
     (  609,   377,   400,     0), #
     (  773,   383,   400,  -100), #
     (  915,   392,   400,  -200), #
     ( 1025,   403,   400,  -300), #
     ( 1112,   412,   400,  -400)],#

    [(  115,   316,   500,  +400), #
     (  243,   297,   500,  +300), #
     (  348,   285,   500,  +200), #
     (  474,   274,   500,  +100), #
     (  613,   272,   500,     0), #
     (  750,   277,   500,  -100), #
     (  878,   290,   500,  -200), #
     (  981,   304,   500,  -300), #
     ( 1067,   321,   500,  -400)],#

    [(  282,   227,   600,  +300), #
     (  380,   212,   600,  +200), #
     (  492,   201,   600,  +100), #
     (  613,   198,   600,     0), #
     (  735,   203,   600,  -100), #
     (  847,   215,   600,  -200), #
     (  943,   230,   600,  -300)],#

    [(  317,   170,   700,  +300), #
     (  408,   155,   700,  +200), #
     (  508,   140,   700,  +100), #
     (  614,   142,   700,     0), #
     (  720,   147,   700,  -100), #
     (  820,   158,   700,  -200), #
     (  908,   173,   700,  -300)],#

]

# ================================
# 2. FLATTEN DATA
# ================================
points = []
values = []

for row in P_exp:
    for (x, y, xr, yr) in row:
        points.append([x, y])
        values.append([xr, yr])

points = np.array(points)
values = np.array(values)

# ================================
# 3. DELAUNAY TRIANGULATION
# ================================
tri = Delaunay(points)

# ================================
# 4. BARYCENTRIC INTERPOLATION
# ================================
def map_pixel_to_real(x, y):
    simplex = tri.find_simplex([[x, y]])
    if simplex < 0:
        return None  # outside

    simplex = simplex[0]
    vertices = tri.simplices[simplex]

    T = tri.transform[simplex]
    bary = np.dot(T[:2], [x, y] - T[2])
    bary = np.append(bary, 1 - bary.sum())

    xr = np.dot(bary, values[vertices, 0])
    yr = np.dot(bary, values[vertices, 1])

    return xr, yr

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

    timestamp = time.time()

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

    for tri_indices in tri.simplices:
        pts = points[tri_indices].astype(int)
        cv2.line(frame, tuple(pts[0]), tuple(pts[1]), (0,255,0), 1)
        cv2.line(frame, tuple(pts[1]), tuple(pts[2]), (0,255,0), 1)
        cv2.line(frame, tuple(pts[2]), tuple(pts[0]), (0,255,0), 1)

    if (iter%10==0):
        detected_shapes = []
        detections = []
        for i in range(len(corners)):
            my_id = int(ids[i])
            c=corners[i]
            my_x = []
            my_y = []
            for j in range(0,4):
                my_x.append(c[0,j,0])
                my_y.append(c[0,j,1])
                #if (my_id==36) or (my_id==47):
                #    print ("  {} {}".format(c[0,j,0], c[0,j,1]))
            max_x = int(max(my_x))
            min_x = int(min(my_x))
            max_y = int(max(my_y))
            min_y = int(min(my_y))
            x_pix = int(sum(my_x)/len(my_x))
            y_pix = int(sum(my_y)/len(my_y))
            detected_shapes.append((my_id,x_pix,y_pix))
            if (my_id==36) or (my_id==47):
                x_real, y_real = map_pixel_to_real(x_pix,y_pix)
                print ("  #{} : <{:.1f},{:.1f}> [{},{}]".format(my_id,x_real,y_real,x_pix,y_pix))
                detections.append((my_id,x_real,y_real))
        print("----------------")
        print()

        # FIXME : DEBUG : quick hack
        with open("/tmp/detections.txt.tmp", "w") as f:
            for i in range(len(detections)):
                my_id, x_real, y_real = detections[i]
                f.write(f"{timestamp} {my_id} {x_real} {y_real}\n")
        os.rename("/tmp/detections.txt.tmp", "/tmp/detections.txt")

    iter=iter+1

    #cv2.imshow("test", frame)
    #cv2.imshow("test", frame_markers)

    if cv2.waitKey(1) == 27:
        break

    retval, buffer = cv2.imencode('.jpg', frame_markers)
    pub_socket.send(buffer)


