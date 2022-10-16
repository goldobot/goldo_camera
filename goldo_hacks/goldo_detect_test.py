import sys
import time
import zmq
import struct
import numpy as np
import select

ip = "192.168.0.222"

context = zmq.Context()    
sub_socket_detect = context.socket(zmq.SUB)
sub_socket_detect.connect('tcp://{}:3202'.format(ip))
sub_socket_detect.setsockopt(zmq.SUBSCRIBE,b'')


while True:
    flags = sub_socket_detect.getsockopt(zmq.EVENTS)
    while flags & zmq.POLLIN:
        received_buf_l = sub_socket_detect.recv_multipart()

        received_buf = b''.join(received_buf_l)
        #print (len(received_buf))

        (coockie, obj_attr, nearest_x, nearest_y) = struct.unpack("<IIii", received_buf)
        if coockie==0x7d7f1892:
            color = "RED  :" if obj_attr==1 else "GREEN:" if obj_attr==2 else "?????:"
            print("{} <{},{}>".format(color, nearest_x, nearest_y))
        else:
            print("ERROR!")

        i_desc, o_desc, e_desc = select.select([sys.stdin], [], [], 0.1)
        if i_desc:
            print ("Key pressed: {}".format(sys.stdin.read(1)))
            quit()

        flags = sub_socket_detect.getsockopt(zmq.EVENTS)



    #time.sleep(0.1)




