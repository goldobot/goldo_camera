# Import library
import argparse
import sys
import cv2

def cmdLineArgs():
    # Create parser.
    parser = argparse.ArgumentParser(description='Camera calibration parser.')
    parser.add_argument('--video', type=int, required=True)
    parser.add_argument('--nbImages', type=int, default=10)
    parser.add_argument('--chessboardX', type=int, default=10)
    parser.add_argument('--chessboardY', type=int, default=10)
    args = parser.parse_args()

    return args

def captureFrames(args):
    # Get a video capture stream.
    vid = cv2.VideoCapture(args.video)

    # Capture frames.
    print('Capturing frames... [c capture, q quit]')
    frames, info = [], True
    while(len(frames) < args.nbImages):
        # Capture the video frame by frame.
        if info:
            print('  Capturing image %s...' % len(frames))
            info = False
        _, frame = vid.read()

        # Display the resulting frame.
        cv2.imshow('Capture video [c capture, q quit]', frame)
        key = cv2.waitKey(1)

        # Press 'c' to capture.
        if key == ord('c'):
            cv2.imshow('Captured image: keep? [y/n]', frame)
            if cv2.waitKey(0) == ord('y'):
                frames.append(frame)
            cv2.destroyAllWindows()
            info = True

        # Press 'q' to quit.
        if key == ord('q'):
            break

    # After the loop release the cap object.
    vid.release()
    cv2.destroyAllWindows()

    return frames

def main():
    # Get command line arguments.
    args = cmdLineArgs()

    # Capture frames.
    frames = captureFrames(args)

# Main program.
if __name__ == '__main__':
    sys.exit(main())
