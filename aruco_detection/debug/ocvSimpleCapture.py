# Import library
import cv2
import sys
import time

# Define a video capture object
vidID = int(sys.argv[1]) if len(sys.argv) == 2 else 0
vid = cv2.VideoCapture(vidID)

# Aruco.
arucoParams = cv2.aruco.DetectorParameters_create()
arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)

while(True):
    # Capture the video frame by frame
    start = time.time()
    ret, frame = vid.read()
    stop = time.time()
    timeFrame = stop - start

    # Display the resulting frame
    start = time.time()
    cv2.imshow('frame', frame)
    stop = time.time()
    timeImshow = stop - start

    # Aruco.
    start = time.time()
    cv2.aruco.detectMarkers(frame, arucoDict, parameters=arucoParams)
    stop = time.time()
    timeAruco = stop - start

    # Print timing.
    print('timeFrame %07.3f s, timeImshow %07.3f s, timeAruco %07.3f s'%(timeFrame, timeImshow, timeAruco))

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
