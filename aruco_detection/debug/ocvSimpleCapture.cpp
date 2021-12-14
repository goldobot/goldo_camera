#include "opencv2/opencv.hpp"
#include <iostream>
#include <cstdlib>
#include <chrono>

using namespace std;
using namespace cv;

int main(int argc, char ** argv) {

  // Create a VideoCapture object
  int vidID = argc == 2 ? atoi(argv[1]) : 0;
  VideoCapture cap(vidID);

  // Check if camera opened successfully
  if (!cap.isOpened()) {
    cout << "Error opening video stream or file" << endl;
    return -1;
  }

  while (1) {
    // Capture frame-by-frame
    std::chrono::steady_clock::time_point start = std::chrono::steady_clock::now();
    Mat frame; cap >> frame;
    std::chrono::steady_clock::time_point stop = std::chrono::steady_clock::now();
    auto timeFrame = std::chrono::duration_cast<std::chrono::milliseconds>(stop - start).count();

    // If the frame is empty, break immediately
    if (frame.empty()) break;

    // Display the resulting frame
    start = std::chrono::steady_clock::now();
    imshow( "Frame", frame );
    stop = std::chrono::steady_clock::now();
    auto timeImshow = std::chrono::duration_cast<std::chrono::milliseconds>(stop - start).count();

    // Print timing.
    cout << "timeFrame " << timeFrame/1000. << " s, timeImshow " << timeImshow/1000. << "s" << endl;

    // Press ESC on keyboard to exit
    char c = (char) waitKey(25);
    if (c == 'q') break;
  }

  // When everything done, release the video capture object
  cap.release();

  // Closes all the frames
  destroyAllWindows();

  return 0;
}
