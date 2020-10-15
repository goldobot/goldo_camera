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

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture1, format="bgr", use_video_port=True, resize=(640, 480)):
    # grab the raw NumPy array representing the image - this array
    # will be 3D, representing the width, height, and # of channels
    image = frame.array
    # show the frame
    cv2.imshow("Frame", image)
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
    print(corners, ids)
    frame_markers = aruco.drawDetectedMarkers(image, corners, ids)
    buff = b''
    for i in range(len(corners)):
        id = ids[i]
        c=corners
        #buff+= struct.pack()
        
        
    
    retval, buffer = cv2.imencode('.jpg', frame_markers)
    pub_socket.send(buffer)