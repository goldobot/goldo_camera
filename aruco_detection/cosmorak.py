# Import the opencv library.
import argparse
import sys
import cv2
import zmq
import cosmorak_pb2

# ArUco types.
ARUCO_DICT = {
    'DICT_4X4_50': cv2.aruco.DICT_4X4_50,
    'DICT_4X4_100': cv2.aruco.DICT_4X4_100,
    'DICT_4X4_250': cv2.aruco.DICT_4X4_250,
    'DICT_4X4_1000': cv2.aruco.DICT_4X4_1000,
    'DICT_5X5_50': cv2.aruco.DICT_5X5_50,
    'DICT_5X5_100': cv2.aruco.DICT_5X5_100,
    'DICT_5X5_250': cv2.aruco.DICT_5X5_250,
    'DICT_5X5_1000': cv2.aruco.DICT_5X5_1000,
    'DICT_6X6_50': cv2.aruco.DICT_6X6_50,
    'DICT_6X6_100': cv2.aruco.DICT_6X6_100,
    'DICT_6X6_250': cv2.aruco.DICT_6X6_250,
    'DICT_6X6_1000': cv2.aruco.DICT_6X6_1000,
    'DICT_7X7_50': cv2.aruco.DICT_7X7_50,
    'DICT_7X7_100': cv2.aruco.DICT_7X7_100,
    'DICT_7X7_250': cv2.aruco.DICT_7X7_250,
    'DICT_7X7_1000': cv2.aruco.DICT_7X7_1000,
    'DICT_ARUCO_ORIGINAL': cv2.aruco.DICT_ARUCO_ORIGINAL,
    'DICT_APRILTAG_16h5': cv2.aruco.DICT_APRILTAG_16h5,
    'DICT_APRILTAG_25h9': cv2.aruco.DICT_APRILTAG_25h9,
    'DICT_APRILTAG_36h10': cv2.aruco.DICT_APRILTAG_36h10,
    'DICT_APRILTAG_36h11': cv2.aruco.DICT_APRILTAG_36h11
}

def autoDetectType(args):
    # Auto-detection of type if type is unknown.
    print('Auto-detecting types...')
    vid = None
    while args.type == '': # Unknown type.
        if vid is None:
            vid = cv2.VideoCapture(args.video)
        # Check for all possible types.
        _, frame = vid.read()
        for (arucoName, arucoDict) in ARUCO_DICT.items():
            arucoDict = cv2.aruco.Dictionary_get(arucoDict)
            arucoParams = cv2.aruco.DetectorParameters_create()
            (corners, ids, rejected) = cv2.aruco.detectMarkers(frame, arucoDict,
                                                               parameters=arucoParams)
            if len(corners) > 0:
                print("  Auto-detected type: found {} '{}' markers".format(len(corners), arucoName))
                args.type = arucoName
        cv2.imshow('Detecting type...', frame)
        cv2.waitKey(1)
    if vid:
        vid.release()
        cv2.destroyAllWindows()

def cmdLineArgs():
    # Create parser.
    parser = argparse.ArgumentParser(description='Publisher parser.')
    parser.add_argument('--video', type=int, required=True)
    parser.add_argument('--type', type=str, default='')
    parser.add_argument('--host', type=str, default='127.0.0.1')
    parser.add_argument('--port', type=int, default=2000)
    args = parser.parse_args()

    # Determine type if unknown.
    autoDetectType(args)

    return args

def detectARUCO(args, frame, socket):
    # Detect ArUco.
    arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT[args.type])
    arucoParams = cv2.aruco.DetectorParameters_create()
    (corners, ids, rejected) = cv2.aruco.detectMarkers(frame, arucoDict,
                                                       parameters=arucoParams)

    # Verify at least one ArUco marker was detected.
    if len(corners) > 0:
        # Flatten the ArUco IDs list.
        ids = ids.flatten()
        # Loop over the detected ArUCo corners.
        for (markerCorner, markerID) in zip(corners, ids):
            # Extract corners (top-left, top-right, bottom-right, bottom-left).
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners

            # Convert each of the (x, y)-coordinate pairs to integers.
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))

            # Draw the bounding box of the ArUCo detection.
            cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)

            # Draw the center (x, y)-coordinates of the ArUco marker.
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)

            # Draw the directions of the box of the ArUCo detection.
            uX = topLeft[0] - bottomLeft[0]
            uY = topLeft[1] - bottomLeft[1]
            vX = bottomRight[0] - bottomLeft[0]
            vY = bottomRight[1] - bottomLeft[1]
            cv2.line(frame, (cX, cY), (cX+uX, cY+uY), (0, 0, 255), 2)
            cv2.line(frame, (cX, cY), (cX+vX, cY+vY), (0, 0, 255), 2)

            # Draw the ArUco marker ID on the frame.
            cv2.putText(frame, str(markerID),
                        (topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)

            # Publish data with ZMQ.
            data = cosmorak_pb2.data()
            data.markerID = markerID
            data.cX = cX
            data.cY = cY
            data.uX = uX
            data.uY = uY
            data.vX = vX
            data.vY = vY
            raw = data.SerializeToString()
            socket.send(raw)

def main():
    # Get command line arguments.
    args = cmdLineArgs()
    if args.type not in ARUCO_DICT:
        sys.exit('Error: type %s not in %s' % (args.type, ARUCO_DICT.keys()))

    # Bind ZMQ socket.
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind('tcp://%s:%s' % (args.host, args.port))

    # Get a video capture stream.
    vid = cv2.VideoCapture(args.video)

    # Capture video.
    print('Analysing video... [q quit]')
    while(True):
        # Capture the video frame by frame.
        _, frame = vid.read()

        # Detect ArUCo markers.
        detectARUCO(args, frame, socket)

        # Display the resulting frame.
        cv2.imshow('Raw video [q quit]', frame)

        # Press 'q' to quit.
        if cv2.waitKey(1) == ord('q'):
            break

    # After the loop release the cap object.
    vid.release()

    # Destroy all the windows.
    cv2.destroyAllWindows()

# Main program.
if __name__ == '__main__':
    sys.exit(main())
