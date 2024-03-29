#include "opencv2/opencv.hpp"
#include "opencv2/aruco.hpp"
#include <iostream>
#include <cstdlib>
#include <chrono>
#include <iomanip>
#include <fstream>

using namespace std;
using namespace cv;


int main(int argc, char ** argv) {
  // Cout width/precision.
  cout.precision(3); cout.fill('0');

  // Command line options.
  int vidID = argc == 2 ? atoi(argv[1]) : 0;
  bool CSI = (argc == 3 && string(argv[2]) == "CSI") ? true : false;

  // Create a VideoCapture object
  VideoCapture cap;
  if (!CSI) { // USB
    cap.open(vidID, cv::CAP_ANY);
  }
  else {
    stringstream sstr;
    sstr << "nvarguscamerasrc sensor-id=" << vidID << " ! ";
    sstr << "video/x-raw(memory:NVMM), ";
    sstr << "width=(int)640, height=(int)340, ";
    sstr << "format=(string)NV12, framerate=(fraction)15/1 ! ";
    sstr << "nvvidconv flip-method=0 ! ";
    sstr << "video/x-raw, width=(int)640, height=(int)360, format=(string)BGRx ! ";
    sstr << "videoconvert ! ";
    sstr << "video/x-raw, format=(string)BGR ! appsink";
    cap.open(sstr.str(), cv::CAP_GSTREAMER);
  };

  // Aruco.
  cv::Ptr<cv::aruco::Dictionary> dictionary = cv::aruco::getPredefinedDictionary(cv::aruco::DICT_6X6_250);
  std::vector<int> ids;
  std::vector<std::vector<cv::Point2f> > corners;

  // FPS.
  std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
  unsigned int nbFrames = 0;

  // Check if camera opened successfully
  if (!cap.isOpened()) {
    cout << "Error opening video stream or file" << endl;
    return -1;
  }

  while (1) {
    // Capture frame-by-frame
    std::chrono::steady_clock::time_point start = std::chrono::steady_clock::now();
    Mat frame; cap >> frame;
    if (frame.empty()) continue;
    std::chrono::steady_clock::time_point stop = std::chrono::steady_clock::now();
    auto timeFrame = std::chrono::duration_cast<std::chrono::milliseconds>(stop - start).count();
    nbFrames += 1;

    // If the frame is empty, break immediately
    if (frame.empty()) break;

    // Display the resulting frame
    start = std::chrono::steady_clock::now();
    imshow( "Frame", frame );
    stop = std::chrono::steady_clock::now();
    auto timeImshow = std::chrono::duration_cast<std::chrono::milliseconds>(stop - start).count();

    // Aruco.
    start = std::chrono::steady_clock::now();
    cv::aruco::detectMarkers(frame, dictionary, corners, ids);
    stop = std::chrono::steady_clock::now();
    auto timeAruco = std::chrono::duration_cast<std::chrono::milliseconds>(stop - start).count();

    // FPS.
    std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();
    auto timeFPS = std::chrono::duration_cast<std::chrono::milliseconds>(end - begin).count();
    unsigned int FPS = (unsigned int) (nbFrames/(timeFPS/1000.));

    // Print timing.
    cout << "timeFrame " << setw(7) << timeFrame/1000. << " s, timeImshow " << setw(7) << timeImshow/1000.;
    cout << "s, timeAruco " << setw(7) << timeAruco/1000. << " s, FPS " << FPS << endl;

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
