from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
from cv2 import aruco
import zmq
import struct

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
new_detection = "0"

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
        
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_100)
    parameters =  aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    #print(corners, ids)
    frame_markers = aruco.drawDetectedMarkers(image, corners, ids)
    buff = b''
    my_x = []
    my_y = []
    if len(corners) == 0:
        #print ("0")
        new_detection = "0"
    for i in range(len(corners)):
        id = ids[i]
        c=corners[i]
        if (id==17):
            #print ("c : ", c)
            #print ("c[0] : ", c[0])
            #print ("c[0,0] : ", c[0,0])
            #print ("c[0,1] : ", c[0,1])
            for j in range(0,4):
                my_x.append(c[0,j,0])
                my_y.append(c[0,j,1])
            #print ("max(my_x) : ", max(my_x))
            #print ("max(my_y) : ", max(my_y))
            max_x = int(max(my_x))
            min_x = int(min(my_x))
            max_y = int(max(my_y))
            min_y = int(min(my_y))
            moy_x = int((min_x+max_x)/2)
            moy_y = int((min_y+max_y)/2)
            #crop = image[min_y:max_y, min_x:max_x]
            crop = gray[moy_y-4:moy_y+4, moy_x-4:moy_x+4]
            #cv2.imwrite("test.jpg", crop)
            sum_up = 0
            sum_down = 0
            for j in range(-4,4):
                sum_up += gray[moy_y-4, moy_x+j]
                sum_down += gray[moy_y+4, moy_x+j]
            if (sum_up > sum_down):
                #print ("N")
                new_detection = "N"
            else:
                #print ("S")
                new_detection = "S"
        #buff+= struct.pack()
        
    if new_detection != last_detection:
        print (new_detection)
        detect_fd = open ("/tmp/girouette.txt", "wt")
        if (new_detection != "0"):
            detect_fd.write(new_detection)
        detect_fd.flush()
        detect_fd.close()
        last_detection = new_detection
        
    
    #retval, buffer = cv2.imencode('.jpg', frame_markers)
    #pub_socket.send(buffer)

    #cv2.imwrite("test.jpg", gray)
    #cv2.imwrite("test.jpg", image)



