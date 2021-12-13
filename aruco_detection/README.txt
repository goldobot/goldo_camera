Installation:
-------------

Packages - pre-compiled:
~> sudo apt-get install libblas-dev liblapack-dev libhdf5-dev protobuf-compiler python3-pip python3-tk python3-pil.imagetk
~> pip3 install --upgrade pip
~> pip3 install opencv-contrib-python zmq protobuf numpy Pillow Cython pkgconfig
~> H5PY_SETUP_REQUIRES=0 pip3 install -U --no-build-isolation h5py

OpenCV - build from source:
~> sudo apt-get install build-essential cmake git unzip pkg-config zlib1g-dev
~> sudo apt-get install libjpeg-dev libjpeg8-dev libjpeg-turbo8-dev
~> sudo apt-get install libpng-dev libtiff-dev libglew-dev
~> sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev
~> sudo apt-get install libgtk2.0-dev libgtk-3-dev libcanberra-gtk*
~> sudo apt-get install python-dev python-numpy python-pip
~> sudo apt-get install python3-dev python3-numpy python3-pip
~> sudo apt-get install libxvidcore-dev libx264-dev libgtk-3-dev
~> sudo apt-get install libtbb2 libtbb-dev libdc1394-22-dev libxine2-dev
~> sudo apt-get install gstreamer1.0-tools libgstreamer-plugins-base1.0-dev
~> sudo apt-get install libgstreamer-plugins-good1.0-dev
~> sudo apt-get install libv4l-dev v4l-utils v4l2ucp qv4l2
~> sudo apt-get install libtesseract-dev libxine2-dev libpostproc-dev
~> sudo apt-get install libavresample-dev libvorbis-dev
~> sudo apt-get install libfaac-dev libmp3lame-dev libtheora-dev
~> sudo apt-get install libopencore-amrnb-dev libopencore-amrwb-dev
~> sudo apt-get install libopenblas-dev libatlas-base-dev libblas-dev
~> sudo apt-get install liblapack-dev liblapacke-dev libeigen3-dev gfortran
~> sudo apt-get install libhdf5-dev libprotobuf-dev protobuf-compiler
~> sudo apt-get install libgoogle-glog-dev libgflags-dev
~> sudo apt-get install qt5-default
~> sudo apt-get install libeigen3-dev
cosmorak@nanorak:~/Programs/opencv_contrib$ git checkout 4.5.4
cosmorak@nanorak:~/Programs/opencv$ git checkout 4.5.4
cosmorak@nanorak:~/Programs/opencv/build$ cmake -DOPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules -DWITH_CUDA=ON -DEIGEN_INCLUDE_PATH=/usr/include/eigen3 -DBUILD_opencv_python3=ON -DCMAKE_INSTALL_PREFIX:PATH=~/Programs/opencv/local -DOPENCV_GENERATE_PKGCONFIG=ON -DBUILD_LIST=core,calib3d,viz,videoio,highgui,aruco,cudev ..
cosmorak@nanorak:~/Programs/opencv/build$ make -j 2
cosmorak@nanorak:~/Programs/opencv/build$ make install
cosmorak@nanorak:~/Programs/opencv/build$ sudo ldconfig

Camera CSI MIPI (arducam): https://www.arducam.com/docs/camera-for-jetson-nano/native-jetson-cameras-imx219-imx477/imx477-how-to-install-the-driver
  Install driver:
    ~> cd /tmp
    ~> wget https://github.com/ArduCAM/MIPI_Camera/releases/download/v0.0.3/install_full.sh
    ~> chmod +x install_full.sh
    ~> ./install_full.sh -m imx477
       => reboot
  Test camera CSI MIPI:
    ~> cd /tmp
    ~> wget https://bootstrap.pypa.io/get-pip.py
    ~> sudo python3 get-pip.py
    ~> sudo pip3 install v4l2-fix
    ~> cd ~/Workspaces
    ~> git clone https://github.com/ArduCAM/MIPI_Camera.git
    ~> cd MIPI_Camera/Jetson/Jetvariety/example
    ~> python3 arducam_displayer.py
  Test camera CSI MIPI:
    ~> git clone https://github.com/JetsonHacksNano/CSI-Camera
    ~> cd CSI-Camera
    ~> python3 simple_camera.py

Utilisation:
------------

brancher la camera: camera <=> /dev/videoX

Pour calibrer la camera:
>> python3 cameraCalibration.py --video X
   => paramètres de la caméra stockés dans le fichier cameraCalibration.h5

Pour protobuf:
>> protoc -I=. --python_out=. ./cosmorak.proto
   => génération cosmorak_pb2.py (pour protobuf)

Dans un terminal, lancer le publisher zmq:
>> python3 cosmorak.py --video X
   => paramètres de la caméra lus dans le fichier cameraCalibration.h5
   => les données issue du traitement image sont envoyées via zmq/protobuf.

Dans un autre terminal, lancer le subscriber zmq:
>> python3 robot.py 
   => les données issue du traitement image sont reçues via zmq/protobuf.

