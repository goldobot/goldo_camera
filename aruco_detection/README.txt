Installation:
-------------

Packages - pre-compiled:
~> sudo apt-get install libblas-dev liblapack-dev libhdf5-dev protobuf-compiler python3-pip python3-tk python3-pil.imagetk
~> pip3 install --upgrade pip
~> pip3 install opencv-contrib-python zmq protobuf numpy Pillow Cython pkgconfig
~> H5PY_SETUP_REQUIRES=0 pip3 install -U --no-build-isolation h5py

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

