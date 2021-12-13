#include "opencv2/opencv.hpp"
#include <iostream>
#include <cstdlib>

using namespace std;
using namespace cv;

int main(int argc, char ** argv) {

  // Create a VideoCapture object
  int vidID = argc == 1 ? 0 : atoi(argv[1]);
  VideoCapture cap(vidID); 

  // Check if camera opened successfully
  if (!cap.isOpened()) {
    cout << "Error opening video stream or file" << endl;
    return -1;
  }

  while (1) {
    // Capture frame-by-frame
    Mat frame;
    cap >> frame;

    // If the frame is empty, break immediately
    if (frame.empty()) break;

    // Display the resulting frame
    imshow( "Frame", frame );

    // Press ESC on keyboard to exit
    char c = (char) waitKey(25);
    if (c==27) break;
  }

  // When everything done, release the video capture object
  cap.release();

  // Closes all the frames
  destroyAllWindows();

  return 0;
}
