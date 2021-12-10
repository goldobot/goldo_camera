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
cosmorak@nanorak:~/Programs/opencv_contrib$ git diff
diff --git a/modules/cudev/test/CMakeLists.txt b/modules/cudev/test/CMakeLists.txt
index d036daf5..83e64906 100644
--- a/modules/cudev/test/CMakeLists.txt
+++ b/modules/cudev/test/CMakeLists.txt
@@ -23,8 +23,8 @@ if(OCV_DEPENDENCIES_FOUND)
   endif()

   CUDA_ADD_EXECUTABLE(${the_target} ${OPENCV_TEST_${the_module}_SOURCES} OPTIONS ${OPENCV_CUDA_OPTIONS_opencv_test_cudev})
-  ocv_target_link_libraries(${the_target} PRIVATE
-      ${test_deps} ${OPENCV_LINKER_LIBS} ${CUDA_LIBRARIES}
+  ocv_target_link_libraries(${the_target} LINK_PRIVATE
+      "${test_deps} ${OPENCV_LINKER_LIBS} ${CUDA_LIBRARIES}"
   )
   add_dependencies(opencv_tests ${the_target})
cosmorak@nanorak:~/Programs/opencv/build$ cmake -DOPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules -DWITH_CUDA=ON -DEIGEN_INCLUDE_PATH=/usr/include/eigen3 -DBUILD_opencv_python3=ON -DCMAKE_INSTALL_PREFIX:PATH=~/Programs/opencv/local ..

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

