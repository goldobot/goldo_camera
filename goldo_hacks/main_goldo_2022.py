from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
from cv2 import aruco
import zmq
import struct
import sys
sys.path.append("../")
import math
import select

# GOLDO HACK
#Y_horizon = 240
#Y_horizon = 192
Y_horizon = 48
Y_offset_mm = 17

green = (0, 255, 0)
red = (0, 0, 255)

P_exp_old = [
    [(   61,   460,   700,   300),
     (  150,   460,   700,   200),
     (  324,   460,   700,     0),
     (  498,   460,   700,  -200),
     (  587,   460,   700,  -300)],
    [(   63,   390,   900,   400),
     (  192,   390,   900,   200),
     (  324,   390,   900,     0),
     (  456,   390,   900,  -200),
     (  585,   390,   900,  -400)],
    [(  116,   350,  1100,   400),
     (  218,   350,  1100,   200),
     (  324,   350,  1100,     0),
     (  430,   350,  1100,  -200),
     (  532,   350,  1100,  -400)],
    [(   62,   323,  1300,   600),
     (  152,   323,  1300,   400),
     (  238,   323,  1300,   200),
     (  324,   323,  1300,     0),
     (  410,   323,  1300,  -200),
     (  496,   323,  1300,  -400),
     (  586,   323,  1300,  -600)],
    [(   27,   302,  1500,   800),
     (  102,   302,  1500,   600),
     (  176,   302,  1500,   400),
     (  251,   302,  1500,   200),
     (  324,   302,  1500,     0),
     (  397,   302,  1500,  -200),
     (  472,   302,  1500,  -400),
     (  546,   302,  1500,  -600),
     (  621,   302,  1500,  -800)],
]

P_exp_old2 = [
    [(   67,   428,   400,   150),
     (  320,   431,   400,     0),
     (  573,   428,   400,  -150)],
    [(  120,   324,   600,   200),
     (  320,   324,   600,     0),
     (  520,   324,   600,  -200)],
    [(   31,   275,   800,   400),
     (  179,   275,   800,   200),
     (  320,   273,   800,     0),
     (  461,   275,   800,  -200),
     (  609,   275,   800,  -400)],
    [(   94,   248,  1000,   400),
     (  210,   249,  1000,   200),
     (  320,   245,  1000,     0),
     (  430,   249,  1000,  -200),
     (  546,   248,  1000,  -400)],
    [(   39,   231,  1200,   600),
     (  133,   231,  1200,   400),
     (  228,   231,  1200,   200),
     (  320,   231,  1200,     0),
     (  412,   231,  1200,  -200),
     (  507,   231,  1200,  -400),
     (  602,   231,  1200,  -600)],
    [(   80,   218,  1400,   600),
     (  162,   218,  1400,   400),
     (  242,   218,  1400,   200),
     (  320,   218,  1400,     0),
     (  398,   218,  1400,  -200),
     (  478,   218,  1400,  -400),
     (  560,   218,  1400,  -600)],
]
P_exp = [
    [(   59,   432,   300,   150), #
     (  311,   430,   300,     0), #
     (  573,   432,   300,  -150)],#
    [(  116,   308,   400,   150), #
     (  316,   306,   400,     0), #
     (  522,   306,   400,  -150)],#
    [(  134,   176,   600,   200), #
     (  321,   174,   600,     0), #
     (  514,   169,   600,  -200)],#
    [(   70,   103,   800,   350), #
     (  178,   101,   800,   200), #
     (  325,    99,   800,     0), #
     (  473,    95,   800,  -200), #
     (  586,    92,   800,  -350)],#
    [(   89,    57,  1000,   400), #
     (  208,    54,  1000,   200), #
     (  327,    51,  1000,     0), #
     (  446,    48,  1000,  -200), #
     (  566,    44,  1000,  -400)],#
]

def dist(p0, p1):
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    return math.sqrt(dx*dx+dy*dy)

P_knot = [[] for i in range(0,640)]

for pe in P_exp:
    pc_len = len(pe)
    if (pc_len<3): continue
    for i in range(0,pc_len-1):
        x0  = pe[i][0]
        y0  = pe[i][1]
        xr0 = pe[i][2]
        yr0 = pe[i][3]
        x1  = pe[i+1][0]
        y1  = pe[i+1][1]
        xr1 = pe[i+1][2]
        yr1 = pe[i+1][3]
        x_min = x0
        x_max = x1
        if i==0:
            x_min = 0
        if i==pc_len-2:
            x_max = 640
        dx = x1-x0
        dy = y1-y0
        dxr = xr1-xr0
        dyr = yr1-yr0
        if dx != 0:
            for x in range(x_min,x_max):
                y = y0 + (x-x0)*dy/dx
                Xr = xr0 + (x-x0)*dxr/dx
                Yr = yr0 + (x-x0)*dyr/dx
                #print ("{:>5d},{:>5d}".format(x,int(y)))
                P_knot[x].append((int(y),Xr,Yr))
    #print()


P_map = [[(0,0)]*480 for i in range(0,640)]
for x in range(0,640):
    Pk = P_knot[x]
    #print (Pk)
    Pk_len = len(Pk)
    if (Pk_len<3):
        continue
    for i in range(Pk_len-2,-1,-1):
        y0  = Pk[i+1][0]
        xr0 = Pk[i+1][1]
        yr0 = Pk[i+1][2]
        y1  = Pk[i][0]
        xr1 = Pk[i][1]
        yr1 = Pk[i][2]
        y_min = y0
        y_max = y1
        if i==Pk_len-2:
            y_min = Y_horizon
        if i==0:
            y_max = 480
        dy = y1-y0
        dxr = xr1-xr0
        dyr = yr1-yr0
        #print (y_min,y_max)
        if dy != 0:
            for y in range(y_min,y_max):
                Xr = xr0 + (y-y0)*dxr/dy
                Yr = yr0 + (y-y0)*dyr/dy
                P_map[x][y] = (int(Xr),int(Yr))


# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (1296, 972)
camera.framerate = 15

rawCapture1 = PiRGBArray(camera, size=(640, 480))
rawCapture2 = PiRGBArray(camera, size=(1296, 972))

# allow the camera to warmup
time.sleep(0.1)

context = zmq.Context()    
pub_socket = context.socket(zmq.PUB)
pub_socket.bind('tcp://0.0.0.0:3201')

pub_socket_detection = context.socket(zmq.PUB)
pub_socket_detection.bind('tcp://0.0.0.0:3202')

socket_rpc_resp = context.socket(zmq.REP)
socket_rpc_resp.bind('tcp://0.0.0.0:3203')

#camera.start_recording('capture.h264', splitter_port=2)

last_detection = "0"

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture1, format="bgr", use_video_port=True, resize=(640, 480)):
    # grab the raw NumPy array representing the image - this array
    # will be 3D, representing the width, height, and # of channels
    image = frame.array
    # show the frame
    #cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame
    rawCapture1.truncate(0)
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
        
    t0 = time.time()

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_100)
    parameters =  aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    #print(corners, ids)
    frame_markers = aruco.drawDetectedMarkers(image, corners, ids)
    buff = b''
    detected_shapes = []
    for i in range(len(corners)):
        id = int(ids[i])
        c=corners[i]
        my_x = []
        my_y = []
        for j in range(0,4):
            my_x.append(c[0,j,0])
            my_y.append(c[0,j,1])
            print ("  {} {}".format(c[0,j,0], c[0,j,1]))
        max_x = int(max(my_x))
        min_x = int(min(my_x))
        max_y = int(max(my_y))
        min_y = int(min(my_y))
        moy_x = int((min_x+max_x)/2)
        moy_y = int((min_y+max_y)/2)
        detected_shapes.append((id,moy_x,moy_y))
        
    nearest_x = 3000
    nearest_y = 0
    obj_attr = 0
    hit = False
    for shape in detected_shapes:
        shape_id = shape[0]
        shape_x  = shape[1]
        shape_y  = shape[2]
        #if (shape_y>330):
        #if (shape.up == True) and (shape.y>Y_horizon):
        if (shape_y>0):
            print("detected shape", shape)
            my_x  = shape_x
            my_y  = shape_y
            (my_Xr, my_Yr) = P_map[my_x][my_y]
            my_Yr = my_Yr + Y_offset_mm
            print (" <{}, {}> -> <{}, {}>".format(my_x, my_y, my_Xr, my_Yr))
            if (nearest_x>my_Xr) and (shape_id==13):
                hit = True
                nearest_x = my_Xr
                nearest_y = my_Yr
                obj_attr = shape_id

    t1 = time.time()

    print("dt={}".format(t1-t0))
    print()
    if (hit):
        msg_detect = struct.pack("<IIii",0x7d7f1892,obj_attr,int(nearest_x),int(nearest_y))
        pub_socket_detection.send(msg_detect)

    #time.sleep(1.0)
    i_desc, o_desc, e_desc = select.select([sys.stdin], [], [], 0.1)
    if i_desc:
        print ("Key pressed: {}".format(sys.stdin.read(1)))
        quit()

 
    retval, buffer = cv2.imencode('.jpg', frame_markers)
    pub_socket.send(buffer)

    #cv2.imwrite("test.jpg", gray)
    #cv2.imwrite("test.jpg", image)
    #cv2.imwrite("/tmp/test.jpg", frame_markers)



