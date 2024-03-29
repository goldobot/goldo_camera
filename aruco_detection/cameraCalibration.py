# Import library
import argparse
import sys
import cv2
import numpy as np
import h5py

def calibrateCamera(args, obj, img, gray):
    # Camera calibration.
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj, img, gray.shape[::-1], None, None)
    fdh = h5py.File('cameraCalibration%s.h5'%args.videoName, 'w')
    fdh.create_dataset('ret', data=ret)
    fdh.create_dataset('mtx', data=mtx)
    fdh.create_dataset('dist', data=dist)
    fdh.create_dataset('rvecs', data=rvecs)
    fdh.create_dataset('tvecs', data=tvecs)
    fdh.close()

def chessboardCalibration(args, frame, obj, img):
    # Termination criteria.
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    cbX, cbY = args.chessboardX, args.chessboardY
    objPt = np.zeros((cbX*cbY, 3), np.float32)
    objPt[:, :2] = np.mgrid[0:cbY, 0:cbX].T.reshape(-1, 2)

    # Find the chess board corners
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (cbY, cbX), None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        obj.append(objPt)
        img.append(corners)

        # Draw and display the corners
        cornersSP = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        cv2.drawChessboardCorners(frame, (cbY, cbX), cornersSP, ret)

    print('    Frame: chessboard found %s...' % ret)
    cv2.imshow('Frame: chessboard found %s' % ret, frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return ret, obj, img, gray

def cmdLineArgs():
    # Create parser.
    parser = argparse.ArgumentParser(description='Camera calibration parser.')
    parser.add_argument('--videoID', type=int, required=True)
    parser.add_argument('--videoType', type=str, default='USB')
    parser.add_argument('--videoName', type=str, default='USB')
    parser.add_argument('--nbFrames', type=int, default=10)
    parser.add_argument('--chessboardX', type=int, default=7)
    parser.add_argument('--chessboardY', type=int, default=10)
    args = parser.parse_args()

    return args

def gstreamerPipeline(capture_width=640, capture_height=360, display_width=640, display_height=360, framerate=15, flip_method=0) :
    return ('nvarguscamerasrc sensor-id=%%d ! '
    'video/x-raw(memory:NVMM), '
    'width=(int)%d, height=(int)%d, '
    'format=(string)NV12, framerate=(fraction)%d/1 ! '
    'nvvidconv flip-method=%d ! '
    'video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! '
    'videoconvert ! '
    'video/x-raw, format=(string)BGR ! appsink'  % (capture_width,capture_height,framerate,flip_method,display_width,display_height))

def captureFrames(args):
    # Get a video capture stream.
    vid = None
    if args.videoType == 'USB':
        vid = cv2.VideoCapture(args.videoID)
    else:
        cmd = gstreamerPipeline()
        vid = cv2.VideoCapture(cmd%args.videoID, cv2.CAP_GSTREAMER)
    assert vid is not None, 'create video capture KO'

    # Capture frames.
    print('Capturing frames... [c capture, q quit]')
    obj = [] # 3d point in real world space
    img = [] # 2d points in image plane.
    gray = None
    frames, info = [], True
    while(len(frames) < args.nbFrames):
        # Capture the video frame by frame.
        if info:
            print('  Capturing frame %s...' % len(frames))
            info = False
        _, frame = vid.read()

        # Display the resulting frame.
        cv2.imshow('Capture video [c capture, q quit]', frame)
        key = cv2.waitKey(1)

        # Press 'c' to capture.
        if key == ord('c'):
            cv2.destroyAllWindows()
            cv2.imshow('Captured frame: keep? [y/n]', frame)
            if cv2.waitKey(0) == ord('y'):
                cv2.destroyAllWindows()
                ret, obj, img, gray = chessboardCalibration(args, frame, obj, img)
                if ret == True:
                    frames.append(frame)
            cv2.destroyAllWindows()
            info = True

        # Press 'q' to quit.
        if key == ord('q'):
            break

    # After the loop release the cap object.
    vid.release()
    cv2.destroyAllWindows()

    return obj, img, gray

def main():
    # Get command line arguments.
    args = cmdLineArgs()

    # Capture frames.
    obj, img, gray = captureFrames(args)

    # Calibrate camera.
    calibrateCamera(args, obj, img, gray)

# Main program.
if __name__ == '__main__':
    sys.exit(main())
