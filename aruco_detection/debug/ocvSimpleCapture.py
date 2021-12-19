# Import library
import cv2
import sys
import time

def gstreamerPipeline(capture_width=640, capture_height=360, display_width=640, display_height=360, framerate=15, flip_method=0) :
    return ('nvarguscamerasrc sensor-id=%%d ! '
    'video/x-raw(memory:NVMM), '
    'width=(int)%d, height=(int)%d, '
    'format=(string)NV12, framerate=(fraction)%d/1 ! '
    'nvvidconv flip-method=%d ! '
    'video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! '
    'videoconvert ! '
    'video/x-raw, format=(string)BGR ! appsink'  % (capture_width,capture_height,framerate,flip_method,display_width,display_height))

# Command line options.
vidID = int(sys.argv[1]) if len(sys.argv) == 2 else 0
CSI = True if len(sys.argv) == 3 and sys.argv[2] == 'CSI' else False
print('vidID', vidID, 'CSI', CSI)

# Define a video capture object
vid = None
if not CSI: # USB
    vid = cv2.VideoCapture(vidID)
else:
    cmd = gstreamerPipeline()
    vid = cv2.VideoCapture(cmd%vidID, cv2.CAP_GSTREAMER)

# Aruco.
arucoParams = cv2.aruco.DetectorParameters_create()
arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)

# FPS.
begin = time.time()
nbFrames = 0

while(True):
    # Capture the video frame by frame
    start = time.time()
    ret, frame = vid.read()
    if not ret:
        continue
    stop = time.time()
    timeFrame = stop - start
    nbFrames += 1

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

    # FPS
    FPS = int(nbFrames/(time.time() - begin))

    # Print timing.
    print('timeFrame %07.3f s, timeImshow %07.3f s, timeAruco %07.3f s, FPS %d'%(timeFrame, timeImshow, timeAruco, FPS), flush=True)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
