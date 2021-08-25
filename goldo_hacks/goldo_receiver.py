import time
import cv2
import zmq
import struct
import numpy as np

ip = "192.168.0.222"

context = zmq.Context()    
sub_socket = context.socket(zmq.SUB)
sub_socket.connect('tcp://{}:3201'.format(ip))
sub_socket.setsockopt(zmq.SUBSCRIBE,b'')


# capture frames from the camera
while True:
    flags = sub_socket.getsockopt(zmq.EVENTS)
    while flags & zmq.POLLIN:
        received_buf_l = sub_socket.recv_multipart()

        received_buf = b''.join(received_buf_l)
        print (len(received_buf))

        cv_array = np.frombuffer(received_buf, dtype=np.uint8)

        cv_image = cv2.imdecode(cv_array, cv2.IMREAD_ANYCOLOR)

        cv2.imshow("Frame", cv_image)

        flags = sub_socket.getsockopt(zmq.EVENTS)


    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

    #time.sleep(0.1)




