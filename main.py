from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
from cv2 import aruco
import numpy as np
import zmq
import struct
from pb2.goldo.camera_pb2 import Image
from pb2.goldo.camera_pb2 import Detections

import asyncio
import setproctitle
import io

from detect_aruco import detectArucos




# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (1296, 976)
camera.framerate = 15

stream = io.BytesIO()
rawCapture1 = PiRGBArray(camera, size=(640, 480))
rawCapture2 = PiRGBArray(camera, size=(1296, 976))

# allow the camera to warmup
time.sleep(0.1)

context = zmq.Context()    
socket_pub = context.socket(zmq.PUB)
socket_pub.bind('tcp://*:3201')

socket_sub = context.socket(zmq.SUB)
socket_sub.setsockopt(zmq.SUBSCRIBE, b'')
socket_sub.bind('tcp://*:3202')

def publishTopic(socket, topic, msg):
    socket.send_multipart([topic.encode('utf8'),
                           msg.DESCRIPTOR.full_name.encode('utf8'),
                           msg.SerializeToString()])

#camera.start_recording('capture.h264', splitter_port=2)
async def foo():
    while True:
        await asyncio.sleep(0.5)
        print('foo')

def main():
    cap_it1 = camera.capture_continuous(rawCapture1, format="bgr", use_video_port=True, splitter_port = 0, resize=(640, 480))
    cap_it2 = camera.capture_continuous(rawCapture2, format="bgr", use_video_port=True, splitter_port = 1)    
        
    while True:
        flags = socket_sub.getsockopt(zmq.EVENTS)
        while flags & zmq.POLLIN:
            data =  socket_sub.recv_multipart()
            flags = socket_sub.getsockopt(zmq.EVENTS)
            
            frame = next(cap_it2)
            image = frame.array
            rawCapture2.truncate(0)
            detections = detectArucos(image)
            publishTopic(socket_pub, 'camera/out/detections', detections)  
        time.sleep(0.1)
        
        #frame = next(cap_it1)
        #image = frame.array
        #rawCapture1.truncate(0)
        #print(image.shape)
        
    
    return
    for frame in camera.capture_continuous(rawCapture1, format="bgr", use_video_port=True, splitter_port = 1, resize=(640, 480)):
        # grab the raw NumPy array representing the image - this array
        # will be 3D, representing the width, height, and # of channels
        image = frame.array
        rawCapture1.truncate(0)
        print('image')
    
if __name__ == '__main__':
    setproctitle.setproctitle('goldo_camera')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print('finihed')

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture1, format="bgr", use_video_port=True, resize=(640, 480)):
    # grab the raw NumPy array representing the image - this array
    # will be 3D, representing the width, height, and # of channels
    image = frame.array
    # show the frame
    #cv2.imshow("Frame", image)
    #key = cv2.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame
    rawCapture1.truncate(0)
    # if the `q` key was pressed, break from the loop
    #if key == ord("q"):
    #    break
        
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_100)
    parameters =  aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    detections = Detections()
    for i in range(len(corners)):
        detection = Detections.Detection()
        detection.tag_id = ids[i][0]
        tag_corners = corners[i][0]
        vec = tag_corners[1] - tag_corners[2] + tag_corners[0] - tag_corners[3]
        vec = vec/np.linalg.norm(vec)
        detection.ux = vec[0]
        detection.uy = vec[1]
        for corner in corners[i][0]:
             detection.corners.append(Detections.Detection.Corner(x=int(corner[0]), y=int(corner[1])))
        detections.detections.append(detection)
    publishTopic(socket_pub, 'camera/out/detections', detections)        
    
    retval, buffer = cv2.imencode('.jpg', image)
    image_proto = Image(width=image.shape[0], height=image.shape[1], encoding=Image.Encoding.JPEG, data=buffer.tobytes())
    publishTopic(socket_pub, 'camera/out/image', image_proto)