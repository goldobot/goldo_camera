import cv2
import sys
import numpy as np
import sys

def nothing(x):
    pass

def saveColor(color):
    print(color)

def redCB(*args):
    if cv2.getTrackbarPos('Save red', 'image'):
        saveColor("red")

def greenCB(*args):
    if cv2.getTrackbarPos('Save green', 'image'):
        saveColor("green")

def main(path):
    # Load in image
    image = cv2.imread(path)

    # Create a window
    cv2.namedWindow('image')

    # Create trackbars for color change
    cv2.createTrackbar('H Min', 'image', 0, 179, nothing) # Hue is from 0-179 for Opencv
    cv2.createTrackbar('S Min', 'image', 0, 255, nothing)
    cv2.createTrackbar('V Min', 'image', 0, 255, nothing)
    cv2.createTrackbar('H Max', 'image', 0, 179, nothing)
    cv2.createTrackbar('S Max', 'image', 0, 255, nothing)
    cv2.createTrackbar('V Max', 'image', 0, 255, nothing)

    # Save color
    cv2.createTrackbar('Save red', 'image', 0, 1, redCB)
    cv2.createTrackbar('Save green', 'image', 0, 1, greenCB)

    # Set default value for MAX HSV trackbars.
    cv2.setTrackbarPos('H Max', 'image', 179)
    cv2.setTrackbarPos('S Max', 'image', 255)
    cv2.setTrackbarPos('V Max', 'image', 255)

    # Initialize to check if HSV min/max value changes
    hMin = sMin = vMin = hMax = sMax = vMax = 0
    phMin = psMin = pvMin = phMax = psMax = pvMax = 0

    output = image
    wait_time = 30
    while(1):
        # get current positions of all trackbars
        hMin = cv2.getTrackbarPos('H Min', 'image')
        sMin = cv2.getTrackbarPos('S Min', 'image')
        vMin = cv2.getTrackbarPos('V Min', 'image')

        hMax = cv2.getTrackbarPos('H Max', 'image')
        sMax = cv2.getTrackbarPos('S Max', 'image')
        vMax = cv2.getTrackbarPos('V Max', 'image')

        # Set minimum and max HSV values to display
        lower = np.array([hMin, sMin, vMin])
        upper = np.array([hMax, sMax, vMax])

        # Create HSV Image and threshold into a range.
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        output = cv2.bitwise_and(image,image, mask= mask)

        # Print if there is a change in HSV value
        if( (phMin != hMin) | (psMin != sMin) | (pvMin != vMin) | (phMax != hMax) | (psMax != sMax) | (pvMax != vMax) ):
            print("(hMin = %d , sMin = %d, vMin = %d), (hMax = %d , sMax = %d, vMax = %d)" % (hMin , sMin , vMin, hMax, sMax , vMax))
            phMin = hMin
            psMin = sMin
            pvMin = vMin
            phMax = hMax
            psMax = sMax
            pvMax = vMax

        # Display output image
        cv2.imshow('image', output)

        # Wait longer to prevent freeze for videos.
        if cv2.waitKey(wait_time) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
