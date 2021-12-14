# Import the opencv library.
import argparse
import sys
import cv2
import zmq
import cosmorak_pb2
import tkinter
import PIL.Image, PIL.ImageTk
import os
import h5py
import numpy as np
import kalman

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
arucoParams = cv2.aruco.DetectorParameters_create()

# Video stream.
class VideoStream:
    def __init__(self, args, socket, delay):
        # Open the video source.
        self.vid = cv2.VideoCapture(args.video)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", args.video)

        # Get video width, height and resized sizes.
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        resizeWidth = int(self.width * args.scalePercent / 100)
        resizeHeight = int(self.height * args.scalePercent / 100)
        self.resize = (resizeWidth, resizeHeight)

        # Save args and socket.
        self._args = args
        self._socket = socket

        # Tracking with kalman filter.
        self.kfr = {}
        self._delay = delay

    def getFrame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR.
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    def resizeDim(self, xy):
        coef = self._args.scalePercent / 100
        resizedXY = (int(xy[0]*coef), int(xy[1]*coef))
        return resizedXY

    def detectARUCO(self, frame, rszFrame):
        # Detect ArUco.
        arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT[self._args.type])
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
                cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                cY = int((topLeft[1] + bottomRight[1]) / 2.0)
                xX = topLeft[0] - bottomLeft[0]
                xY = topLeft[1] - bottomLeft[1]
                yX = bottomRight[0] - bottomLeft[0]
                yY = bottomRight[1] - bottomLeft[1]

                # Draw the bounding box of the ArUCo detection.
                cv2.line(rszFrame, self.resizeDim(topLeft), self.resizeDim(topRight), (0, 255, 0), 2)
                cv2.line(rszFrame, self.resizeDim(topRight), self.resizeDim(bottomRight), (0, 255, 0), 2)
                cv2.line(rszFrame, self.resizeDim(bottomRight), self.resizeDim(bottomLeft), (0, 255, 0), 2)
                cv2.line(rszFrame, self.resizeDim(bottomLeft), self.resizeDim(topLeft), (0, 255, 0), 2)

                # Draw the directions of the box of the ArUCo detection.
                cv2.line(rszFrame, self.resizeDim((cX, cY)), self.resizeDim((cX+xX, cY+xY)), (0, 0, 255), 2)
                cv2.line(rszFrame, self.resizeDim((cX, cY)), self.resizeDim((cX+yX, cY+yY)), (0, 0, 255), 2)

                # Draw the center (x, y)-coordinates of the ArUco marker.
                cv2.circle(rszFrame, self.resizeDim((cX, cY)), 4, (255, 0, 0), -1)
                cv2.putText(rszFrame, str(markerID), self.resizeDim((cX*1.05, cY*1.05)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                # Tracking with kalman filter.
                if markerID not in self.kfr:
                    self.kfr[markerID] = kalman.KalmanFilter([cX, cY], deltaT=self._delay)
                else:
                    self.kfr[markerID].prediction()
                vecZ = np.array([[cX], [cY]])
                self.kfr[markerID].update(vecZ)

                # Draw marker speed.
                vX = int(self.kfr[markerID].vecS[2])
                vY = int(self.kfr[markerID].vecS[3])
                cv2.line(rszFrame, self.resizeDim((cX, cY)), self.resizeDim((cX+vX, cY+vY)), (255, 127, 0), 2)

                # Publish data with ZMQ.
                data = cosmorak_pb2.data()
                data.markerID = markerID
                data.cX = cX
                data.cY = cY
                data.xX = xX
                data.xY = xY
                data.yX = yX
                data.yY = yY
                data.vX = vX
                data.vY = vY
                raw = data.SerializeToString()
                self._socket.send(raw)

    # Release the video source when the object is destroyed.
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

# Tkinter application.
class TkApplication:
    def __init__(self, window, windowTitle, args, socket):
        # Initialize window and title.
        self.window = window
        self.window.title(windowTitle)
        print(windowTitle)

        # Get camera calibration parameters if any.
        self.cpr = {}
        if os.path.isfile('cameraCalibration.h5'):
            fdh = h5py.File('cameraCalibration.h5', 'r')
            self.cpr['mtx'] = fdh['mtx'][...]
            self.cpr['dist'] = fdh['dist'][...]
            fdh.close()
        else:
            assert True, 'the camera must be calibrated with cameraCalibration.py'

        # Save args and socket.
        self._args = args
        self._socket = socket

        # Open video source (by default this will try to open the computer webcam).
        self.delay = 1
        self.vid = VideoStream(args, socket, self.delay)

        # Create several canvas that can fit the above video source size.
        lbl = tkinter.Label(window, text='raw')
        lbl.grid(row=0, column=0)
        lbl = tkinter.Label(window, text='undistorted')
        lbl.grid(row=0, column=1)
        self.canvasRaw = tkinter.Canvas(window, width=self.vid.resize[0], height=self.vid.resize[1])
        self.canvasRaw.grid(row=1, column=0)
        self.photoRaw = None
        self.canvasDst = tkinter.Canvas(window, width=self.vid.resize[0], height=self.vid.resize[1])
        self.canvasDst.grid(row=1, column=1, columnspan=2)
        self.photoDst = None
        self.roi = tkinter.IntVar(window)
        chkROI = tkinter.Checkbutton(window, text="ROI", variable=self.roi, onvalue=1, offvalue=0)
        chkROI.grid(row=2, column=0)
        self.alpha = tkinter.StringVar(window, value='0')
        tkinter.Label(text='alpha').grid(row=2, column=1)
        entAlp = tkinter.Entry(window, textvariable=self.alpha)
        entAlp.bind('<Key-Return>', self.onAlphaChanged)
        self._newCamMtx, self._roiCam = None, None
        self.onAlphaChanged(None) # Initialize self._newCamMtx and self._roiCam.
        entAlp.grid(row=2, column=2)

        # After it is called once, the update method will be automatically called every delay milliseconds.
        self.update()

        # Tkinter mainloop.
        self.window.mainloop()

    def onAlphaChanged(self, event):
        # Callback triggered when alpha changed.
        alpha = 0 # Returns undistorted image with minimum unwanted pixels.
        try: # Avoid crash when using GUI.
            alpha = float(self.alpha.get())
        except:
            alpha = 0
        print('  alpha changed:', alpha)
        width, height = self.vid.resize[0], self.vid.resize[1]
        self._newCamMtx, self._roiCam = cv2.getOptimalNewCameraMatrix(self.cpr['mtx'], self.cpr['dist'],
                                                                      (width, height), alpha,
                                                                      (width, height))

    def update(self):
        # Get a frame from the video source.
        ret, rawFrame = self.vid.getFrame()

        # Get undistorted frame that has the same size and type as the original frame.
        dstFrame = cv2.undistort(rawFrame, self.cpr['mtx'], self.cpr['dist'], None, self._newCamMtx)
        if self.roi.get():
            x, y, width, height = self._roiCam
            roiFrame = np.ones(dstFrame.shape, np.uint8) # Black image.
            roiFrame[y:y+height, x:x+width] = dstFrame[y:y+height, x:x+width] # Add ROI.
            dstFrame = roiFrame

        # Process image and update canvas of the GUI.
        if ret:
            # Process image.
            rszRawFrame = cv2.resize(rawFrame, self.vid.resize)
            self.photoRaw = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(rszRawFrame))

            # Update canvas of the GUI.
            self.canvasRaw.create_image(0, 0, image=self.photoRaw, anchor=tkinter.NW)

            # Process image.
            rszDstFrame = cv2.resize(dstFrame, self.vid.resize)
            self.vid.detectARUCO(dstFrame, rszDstFrame)
            self.photoDst = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(rszDstFrame))

            # Update canvas of the GUI.
            self.canvasDst.create_image(0, 0, image=self.photoDst, anchor=tkinter.NW)
        self.window.after(self.delay, self.update)

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
            (corners, ids, rejected) = cv2.aruco.detectMarkers(frame, arucoDict,
                                                               parameters=arucoParams)
            if len(corners) > 0:
                print("  Auto-detected type: found {} '{}' markers".format(len(corners), arucoName))
                args.type = arucoName
        cv2.imshow('Auto-detecting types...', frame)
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
    parser.add_argument('--scalePercent', type=int, default=60)
    args = parser.parse_args()

    # Determine type if unknown.
    autoDetectType(args)

    return args

def main():
    # Get command line arguments.
    args = cmdLineArgs()
    if args.type not in ARUCO_DICT:
        sys.exit('Error: type %s not in %s' % (args.type, ARUCO_DICT.keys()))

    # Bind ZMQ socket.
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind('tcp://%s:%s' % (args.host, args.port))

    # Capture video stream.
    TkApplication(tkinter.Tk(), 'Analysing video...', args, socket)

# Main program.
if __name__ == '__main__':
    sys.exit(main())
