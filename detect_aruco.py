import cv2
from cv2 import aruco
import numpy as np
from pb2.goldo.camera_pb2 import Detections



def detectArucos(image):
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
    return detections