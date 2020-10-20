from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
from cv2 import aruco
import zmq
import struct
from pb.goldo.camera.image_pb2 import Image
from pb.goldo.camera.detections_pb2 import Detections



# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (1296, 972)
camera.framerate = 15

rawCapture1 = PiRGBArray(camera, size=(640, 480))
rawCapture2 = PiRGBArray(camera, size=(1296, 972))

# allow the camera to warmup
time.sleep(0.1)

context = zmq.Context()    
socket_pub = context.socket(zmq.PUB)
socket_pub.bind('tcp://*:3201')

def publishTopic(socket, topic, msg):
    socket.send_multipart([topic.encode('utf8'),
                           msg.DESCRIPTOR.full_name.encode('utf8'),
                           msg.SerializeToString()])

#camera.start_recording('capture.h264', splitter_port=2)

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

    #frame_markers = aruco.drawDetectedMarkers(image, corners, ids)
    detections = Detections()
    for i in range(len(corners)):
        detection = Detections.Detection()
        detection.tag_id = ids[i][0]
        for corner in corners[i][0]:
            print(corner)
            detection.corners.append(Detections.Detection.Corner(x=int(corner[0]), y=int(corner[1])))
        detections.detections.append(detection)
    publishTopic(socket_pub, 'camera/out/detections', detections)        
    
    retval, buffer = cv2.imencode('.jpg', image)
    image_proto = Image(width=image.shape[0], height=image.shape[1], encoding=Image.Encoding.JPEG, data=buffer.tobytes())
    publishTopic(socket_pub, 'camera/out/image', image_proto)