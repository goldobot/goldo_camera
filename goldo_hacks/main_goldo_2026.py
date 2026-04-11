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

CAM_W = 1296
CAM_H =  972

Y_horizon = 0
Y_offset_mm = 0

green = (0, 255, 0)
red = (0, 0, 255)

P_exp = [
    [(   14,   775,   100,  -400), #
     (   97,   817,   100,  -300), #
     ( 1123,   829,   100,   300), #
     ( 1206,   785,   100,   400)],#

    [(   31,   646,   200,  -400), #
     (  116,   664,   200,  -300), #
     (  232,   688,   200,  -200), #
     (  985,   693,   200,   200), #
     ( 1106,   676,   200,   300), #
     ( 1168,   651,   200,   400)],#

    [(   67,   519,   300,  -400), #
     (  154,   516,   300,  -300), #
     (  266,   522,   300,  -200), #
     (  422,   523,   300,  -100), #
     (  608,   529,   300,     0), #
     (  797,   531,   300,   100), #
     (  952,   528,   300,   200), #
     ( 1070,   527,   300,   300), #
     ( 1155,   525,   300,   400)],#

    [(  112,   407,   400,  -400), #
     (  198,   394,   400,  -300), #
     (  308,   386,   400,  -200), #
     (  450,   378,   400,  -100), #
     (  609,   377,   400,     0), #
     (  773,   383,   400,   100), #
     (  915,   392,   400,   200), #
     ( 1025,   403,   400,   300), #
     ( 1112,   412,   400,   400)],#

    [(  115,   316,   500,  -400), #
     (  243,   297,   500,  -300), #
     (  348,   285,   500,  -200), #
     (  474,   274,   500,  -100), #
     (  613,   272,   500,     0), #
     (  750,   277,   500,   100), #
     (  878,   290,   500,   200), #
     (  981,   304,   500,   300), #
     ( 1067,   321,   500,   400)],#

    [(  282,   227,   600,  -300), #
     (  380,   212,   600,  -200), #
     (  492,   201,   600,  -100), #
     (  613,   198,   600,     0), #
     (  735,   203,   600,   100), #
     (  847,   215,   600,   200), #
     (  943,   230,   600,   300)],#

    [(  317,   170,   700,  -300), #
     (  408,   155,   700,  -200), #
     (  508,   140,   700,  -100), #
     (  614,   142,   700,     0), #
     (  720,   147,   700,   100), #
     (  820,   158,   700,   200), #
     (  908,   173,   700,   300)],#

]

def dist(p0, p1):
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    return math.sqrt(dx*dx+dy*dy)

P_knot = [[] for i in range(0,1296)]

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
            x_max = 1296
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


P_map = [[(0,0)]*972 for i in range(0,1296)]
for x in range(0,1296):
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
            y_max = 972
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
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(
#    main={"size": (640, 480), "format": "BGR888"}
#    main={"size": (1920, 1080), "format": "BGR888"}
    main={"size": (CAM_W, CAM_H), "format": "RGB888"}
))
picam2.start()

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
while True:
    # grab the raw NumPy array representing the image - this array
    # will be 3D, representing the width, height, and # of channels
    #image = frame.array
    image = picam2.capture_array()
    # show the frame
    #cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
        
    t0 = time.time()

    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_100)
    parameters =  aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    #print(corners, ids)
    frame_markers = aruco.drawDetectedMarkers(image, corners, ids)
    buff = b''
    detected_objects = []
    for i in range(len(corners)):
        id = int(ids[i])
        c=corners[i]
        my_x = []
        my_y = []
        for j in range(0,4):
            my_x.append(c[0,j,0])
            my_y.append(c[0,j,1])
            #print ("  {} {}".format(c[0,j,0], c[0,j,1]))
        max_x = int(max(my_x))
        min_x = int(min(my_x))
        max_y = int(max(my_y))
        min_y = int(min(my_y))
        moy_x = int((min_x+max_x)/2)
        moy_y = int((min_y+max_y)/2)
        detected_objects.append((id,moy_x,moy_y))
        
    nearest_x = 3000
    nearest_y = 0
    obj_attr = 0
    hit = False
    for obj in detected_objects:
        obj_id = obj[0]
        obj_x  = obj[1]
        obj_y  = obj[2]
        if (obj_y>0):
            print("detected obj", obj)
            my_x  = obj_x
            my_y  = obj_y
            (my_Xr, my_Yr) = P_map[my_x][my_y]
            my_Yr = my_Yr + Y_offset_mm
            print (" <{}, {}> -> <{}, {}>".format(my_x, my_y, my_Xr, my_Yr))
            if (nearest_x>my_Xr) and (obj_id==13):
                hit = True
                nearest_x = my_Xr
                nearest_y = my_Yr
                obj_attr = obj_id

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



